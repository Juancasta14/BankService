from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import Query
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi.responses import RedirectResponse
import random
from adapters.inbound.http.routes.auth_routes import router as auth_router
from adapters.inbound.http.routes.transfers import router as transfer_router
from adapters.inbound.http.routes.payments import router as payments_router


from database import get_db, engine
from models import (
    Base,
    WalletDB,
    PSETransactionDB,
    PSETransactionCreate,
    PSETransactionOut,
    PSETransferResponse,
    PSECallbackIn,
    Account,
    Wallet,
    Movement,
    CustomerSummary,
    get_accounts_by_customer,
    get_wallet_by_customer,
    get_movements_by_customer,
    get_account_by_id,
)

app = FastAPI(title="Bank Service with Auth")
app.include_router(auth_router)
app.include_router(transfer_router)
app.include_router(payments_router)
Base.metadata.create_all(bind=engine)

# ========= ENDPOINTS DE NEGOCIO (PROTEGIDOS) =========

@app.get("/customers/{customer_id}/accounts", response_model=List[Account])
def get_accounts(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    accounts_db = get_accounts_by_customer(db, customer_id)
    return [
        Account(
            id=a.id,
            customer_id=a.customer_id,
            type=a.type,
            balance=a.balance,
        )
        for a in accounts_db
    ]


@app.get("/customers/{customer_id}/wallet", response_model=Optional[Wallet])
def get_wallet(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    wallet_db = get_wallet_by_customer(db, customer_id)
    if wallet_db is None:
        return None

    return Wallet(
        id=wallet_db.id,
        customer_id=wallet_db.customer_id,
        balance=wallet_db.balance,
    )


@app.get("/customers/{customer_id}/summary", response_model=CustomerSummary)
def get_customer_summary(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    accounts_db = get_accounts_by_customer(db, customer_id)
    wallet_db = get_wallet_by_customer(db, customer_id)

    if not accounts_db and wallet_db is None:
        raise HTTPException(status_code=404, detail="Cliente sin productos")

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

@app.get(
    "/customers/{customer_id}/movements",
    response_model=List[Movement],
)
def get_customer_movements(
    customer_id: int,
    account_type: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    movimientos_db = get_movements_by_customer(
        db=db,
        customer_id=customer_id,
        account_type=account_type,
        date_from=date_from,
        date_to=date_to,
    )
    return movimientos_db
    



@app.get("/payments/{internal_order_id}")
def get_pse_payment(
    internal_order_id: str,
    db: Session = Depends(get_db),
):
    tx = (
        db.query(PSETransactionDB)
        .filter(PSETransactionDB.internal_order_id == internal_order_id)
        .first()
    )

    if not tx:
        raise HTTPException(status_code=404, detail="Transacción PSE no encontrada")
    return tx

@app.post("/callback")
def pse_callback(data: PSECallbackIn, db: Session = Depends(get_db)):
    tx = (
        db.query(PSETransactionDB)
        .filter(PSETransactionDB.internal_order_id == data.internal_order_id)
        .first()
    )

    if not tx:
        raise HTTPException(status_code=404, detail="Transacción PSE no encontrada")

    # Actualizamos datos del proveedor
    tx.status = data.status
    tx.provider_tx_id = data.provider_tx_id
    tx.provider_reference = data.provider_reference
    tx.callback_status_raw = json.dumps(data.raw_payload or {})
    tx.updated_at = datetime.utcnow()

    if data.status.upper() == "SUCCESS":
        account = db.query(AccountDB).filter(AccountDB.id == tx.account_id).first()
        if not account:
            raise HTTPException(status_code=400, detail="Cuenta asociada no existe")

        # Acreditar dinero en la cuenta
        account.balance += tx.amount

        # Registrar movimiento (depósito PSE)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        mov = MovementDB(
            account_id=account.id,
            customer_id=account.customer_id,
            account_type=account.type,
            date=today,
            description=f"Depósito vía PSE ref {tx.internal_order_id}",
            amount=tx.amount,
            type="credito",
        )
        db.add(mov)

    db.commit()

    return {"message": "Callback procesado correctamente", "status": tx.status}



@app.get("/pse-gateway/{internal_order_id}")
def pse_gateway(internal_order_id: str, db: Session = Depends(get_db)):
    # Buscar la transacción
    tx = (
        db.query(PSETransactionDB)
        .filter(PSETransactionDB.internal_order_id == internal_order_id)
        .first()
    )

    if tx is None:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    # Transacción expirada
    if tx.expires_at < datetime.utcnow():
        tx.status = "EXPIRED"
        db.commit()
        return RedirectResponse(url=tx.return_url_failure)

    # Buscar la cuenta asociada
    account = (
        db.query(AccountDB)
        .filter(AccountDB.id == tx.account_id)
        .first()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Cuenta de origen no encontrada")

    # ===============================
    #  SIMULACIÓN: Aprobación PSE
    #  90% aprobado, 10% rechazado
    # ===============================

    import random
    aprobado = random.random() < 0.9   # 90% chance

    if not aprobado:
        tx.status = "REJECTED"
        tx.updated_at = datetime.utcnow()
        db.commit()
        return RedirectResponse(url=tx.return_url_failure)

    # ===============================
    #  Descontar saldo
    # ===============================

    if account.balance < tx.amount:
        # Saldo insuficiente al momento de pagar
        tx.status = "REJECTED"
        tx.updated_at = datetime.utcnow()
        db.commit()
        return RedirectResponse(url=tx.return_url_failure)

    # Descontar balance
    account.balance -= tx.amount

    tx.status = "APPROVED"
    tx.updated_at = datetime.utcnow()
    db.commit()
    # Redirigir al frontend (Flask)
    return RedirectResponse(url=tx.return_url_success)
