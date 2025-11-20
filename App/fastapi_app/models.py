# fastapi_app/models.py

from typing import List, Optional

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, Session
from pydantic import BaseModel
from datetime import date
from enum import Enum

Base = declarative_base()


# =========================
#   MODELOS SQLALCHEMY
# =========================

class AccountDB(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True, nullable=False)
    type = Column(String, nullable=False)
    balance = Column(Float, nullable=False)


class WalletDB(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True, nullable=False)
    balance = Column(Float, nullable=False)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class MovementDB(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, index=True, nullable=False)
    account_type = Column(String, nullable=True)  # "ahorros", "corriente", etc.
    date = Column(String, nullable=False)  # también podría ser Date, pero string ISO es suficiente
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # "credito" o "debito"

class MovementType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER_OUT = "transfer_out"
    TRANSFER_IN = "transfer_in"

# =========================
#   MODELOS PYDANTIC
# =========================

class Account(BaseModel):
    id: int
    customer_id: int
    type: str
    balance: float

    class Config:
        from_attributes = True


class Wallet(BaseModel):
    id: int
    customer_id: int
    balance: float

    class Config:
        from_attributes = True


class CustomerSummary(BaseModel):
    customer_id: int
    accounts: List[Account]
    wallet: Optional[Wallet]
    total_balance: float


class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str

class Movement(BaseModel):
    date: str
    description: str
    amount: float
    type: str          # "credito" / "debito"
    account_type: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
#   HELPERS DE CONSULTA
# =========================

def get_accounts_by_customer(db: Session, customer_id: int) -> List[AccountDB]:
    return db.query(AccountDB).filter(AccountDB.customer_id == customer_id).all()


def get_wallet_by_customer(db: Session, customer_id: int) -> Optional[WalletDB]:
    return db.query(WalletDB).filter(WalletDB.customer_id == customer_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[UserDB]:
    return db.query(UserDB).filter(UserDB.username == username).first()
    
def get_movements_by_customer(
    db: Session,
    customer_id: int,
    account_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[MovementDB]:
    query = db.query(MovementDB).filter(MovementDB.customer_id == customer_id)

    if account_type:
        query = query.filter(MovementDB.account_type == account_type)

    # asumiendo fechas en formato "YYYY-MM-DD" guardadas como texto
    if date_from:
        query = query.filter(MovementDB.date >= date_from)
    if date_to:
        query = query.filter(MovementDB.date <= date_to)

    return query.order_by(MovementDB.date.desc(), MovementDB.id.desc()).all()
