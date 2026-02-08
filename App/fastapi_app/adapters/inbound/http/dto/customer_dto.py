from typing import List, Optional
from pydantic import BaseModel


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


class Movement(BaseModel):
    date: str
    description: str
    amount: float
    type: str  # "credito" / "debito"
    account_type: Optional[str] = None

    class Config:
        from_attributes = True


class CustomerSummary(BaseModel):
    customer_id: int
    accounts: List[Account]
    wallet: Optional[Wallet]
    total_balance: float
