# fastapi_app/models.py

from typing import List, Optional

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, Session
from pydantic import BaseModel

# AQUÍ definimos el ÚNICO Base para los modelos de BD
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


# =========================
#   MODELOS PYDANTIC
# =========================

class Account(BaseModel):
    id: int
    customer_id: int
    type: str
    balance: float

    class Config:
        orm_mode = True


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


# =========================
#   HELPERS DE CONSULTA
# =========================

def get_accounts_by_customer(db: Session, customer_id: int) -> List[AccountDB]:
    return db.query(AccountDB).filter(AccountDB.customer_id == customer_id).all()


def get_wallet_by_customer(db: Session, customer_id: int) -> Optional[WalletDB]:
    return db.query(WalletDB).filter(WalletDB.customer_id == customer_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[UserDB]:
    return db.query(UserDB).filter(UserDB.username == username).first()
