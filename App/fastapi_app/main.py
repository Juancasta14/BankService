from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import AccountDB, WalletDB
from models import Account, Wallet, CustomerSummary

app = FastAPI()


# ===== Helpers =====

def get_accounts_by_customer(db: Session, customer_id: int) -> List[AccountDB]:
    return db.query(AccountDB).filter(AccountDB.customer_id == customer_id).all()


def get_wallet_by_customer(db: Session, customer_id: int) -> Optional[WalletDB]:
    return db.query(WalletDB).filter(WalletDB.customer_id == customer_id).first()


# ===== Endpoints =====

@app.get("/customers/{customer_id}/accounts", response_model=List[Account])
def get_accounts(customer_id: int, db: Session = Depends(get_db)):
    accounts_db = get_accounts_by_customer(db, customer_id)

    return [
        Account(
            id=a.id,
            customer_id=a.customer_id,
            type=a.type,
            balance=a.balance
        )
        for a in accounts_db
    ]


@app.get("/customers/{customer_id}/wallet", response_model=Optional[Wallet])
def get_wallet(customer_id: int, db: Session = Depends(get_db)):
    wallet_db = get_wallet_by_customer(db, customer_id)

    if wallet_db is None:
        return None

    return Wallet(
        id=wallet_db.id,
        customer_id=wallet_db.customer_id,
        balance=wallet_db.balance
    )


@app.get("/customers/{customer_id}/summary", response_model=CustomerSummary)
def get_customer_summary(customer_id: int, db: Session = Depends(get_db)):
    accounts_db = get_accounts_by_customer(db, customer_id)
    wallet_db = get_wallet_by_customer(db, customer_id)

    if not accounts_db and wallet_db is None:
        raise HTTPException(status_code=404, detail="Cliente sin productos")

    # Convertir SQLAlchemy -> Pydantic
    accounts = [
        Account(
            id=a.id,
            customer_id=a.customer_id,
            type=a.type,
            balance=a.balance,
        )
        for a in accounts_db
    ]

    wallet = None
    if wallet_db:
        wallet = Wallet(
            id=wallet_db.id,
            customer_id=wallet_db.customer_id,
            balance=wallet_db.balance,
        )

    total = sum(a.balance for a in accounts_db)
    if wallet_db:
        total += wallet_db.balance

    return CustomerSummary(
        customer_id=customer_id,
        accounts=accounts,
        wallet=wallet,
        total_balance=total,
    )


@app.get("/")
def root():
    return {"message": "FastAPI Bank Service Running!"}
