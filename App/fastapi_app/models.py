from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import Session
from typing import List, Optional

from pydantic import BaseModel

from database import Base   # <-- sin punto


# ----- MODELOS SQLALCHEMY -----

class AccountDB(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    type = Column(String, nullable=False)
    balance = Column(Float, default=0.0)


class WalletDB(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True, unique=True)
    balance = Column(Float, default=0.0)


# ----- ESQUEMAS Pydantic -----

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
        orm_mode = True


class CustomerSummary(BaseModel):
    customer_id: int
    accounts: List[Account]
    wallet: Optional[Wallet]
    total_balance: float


# ----- FUNCIONES DE ACCESO A DATOS -----

def get_accounts_by_customer(db: Session, customer_id: int) -> List[AccountDB]:
    return db.query(AccountDB).filter(AccountDB.customer_id == customer_id).all()


def get_wallet_by_customer(db: Session, customer_id: int) -> Optional[WalletDB]:
    return db.query(WalletDB).filter(WalletDB.customer_id == customer_id).first()