from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from database import Base, engine, get_db
from models import (
    Account,
    Wallet,
    CustomerSummary,
    get_accounts_by_customer,
    get_wallet_by_customer,
)

app = FastAPI(title="Servicio Bancario - Saldos (PostgreSQL)")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/customers/{customer_id}/accounts", response_model=List[Account])
def get_customer_accounts(customer_id: int, db: Session = Depends(get_db)):
    accounts_db = get_accounts_by_customer(db, customer_id)
    if not accounts_db:
        raise HTTPException(status_code=404, detail="No se encontraron cuentas para este cliente")
    return accounts_db


@app.get("/customers/{customer_id}/wallet", response_model=Wallet)
def get_customer_wallet(customer_id: int, db: Session = Depends(get_db)):
    wallet_db = get_wallet_by_customer(db, customer_id)
    if not wallet_db:
        raise HTTPException(status_code=404, detail="El cliente no tiene billetera")
    return wallet_db


@app.get("/customers/{customer_id}/summary", response_model=CustomerSummary)
def get_customer_summary(customer_id: int, db: Session = Depends(get_db)):
    accounts_db = get_accounts_by_customer(db, customer_id)
    wallet_db = get_wallet_by_customer(db, customer_id)

    if not accounts_db and wallet_db is None:
        raise HTTPException(status_code=404, detail="Cliente sin productos")

    total = sum(a.balance for a in accounts_db)
    if wallet_db:
        total += wallet_db.balance

    return CustomerSummary(
        customer_id=customer_id,
        accounts=accounts_db,
        wallet=wallet_db,
        total_balance=total,
    )