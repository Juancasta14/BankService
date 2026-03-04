from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class Account(BaseModel):
    id: int
    customer_id: int
    type: str
    balance: float

    model_config = ConfigDict(from_attributes=True)


class Wallet(BaseModel):
    id: int
    customer_id: int
    balance: float

    model_config = ConfigDict(from_attributes=True)


class Movement(BaseModel):
    date: str
    description: str
    amount: float
    type: str  # "credito" / "debito"
    account_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CustomerSummary(BaseModel):
    customer_id: int
    accounts: List[Account]
    wallet: Optional[Wallet]
    total_balance: float
