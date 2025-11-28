from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import Query
from pydantic import BaseModel
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi.responses import RedirectResponse
import random

from database import get_db, engine
from models import (
    Base,
    AccountDB,
    WalletDB,
    UserDB,
    MovementDB,
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
    get_user_by_username,
    get_movements_by_customer,
    get_account_by_id,
)
from security import verify_password, create_access_token

app = FastAPI(title="Bank Service with Auth")

# Crear tablas (accounts, wallets, users...)
Base.metadata.create_all(bind=engine)

# Donde FastAPI “cree” que está el endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ========= DEPENDENCIA: usuario actual a partir del token =========

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserDB:
    from security import decode_token  # import aquí para evitar ciclos

    payload = decode_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload["sub"]
    user = get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ========= AUTH =========

@app.post("/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Recibe username y password (form-data) y devuelve un JWT si son correctos.
    """
    user = get_user_by_username(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.id,
    }


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
    
class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float

@app.post("/customers/{customer_id}/transfer")
def make_transfer(req: TransferRequest, db: Session = Depends(get_db)):
    from_account_id = req.from_account_id
    to_account_id = req.to_account_id
    amount = req.amount

    if amount <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor que cero")

    if from_account_id == to_account_id:
        raise HTTPException(status_code=400, detail="La cuenta origen y destino no pueden ser iguales")

    acc_out = db.query(AccountDB).filter(AccountDB.id == from_account_id).first()
    acc_in  = db.query(AccountDB).filter(AccountDB.id == to_account_id).first()

    if not acc_out:
        raise HTTPException(status_code=404, detail="Cuenta de origen no encontrada")
    if not acc_in:
        raise HTTPException(status_code=404, detail="Cuenta de destino no encontrada")

    if acc_out.balance < amount:
        raise HTTPException(status_code=400, detail="Fondos insuficientes en la cuenta de origen")

    try:
        # Actualizar saldos
        acc_out.balance -= amount
        acc_in.balance  += amount

        now = datetime.now().strftime("%Y-%m-%d")

        mov_out = MovementDB(
            account_id   = acc_out.id,
            customer_id  = acc_out.customer_id,
            account_type = acc_out.type,
            date         = now,
            description  = f"Transferencia enviada a cuenta {acc_in.id}",
            amount       = amount,        # positivo
            type         = "debito",      # <- clave
        )


        mov_in = MovementDB(
            account_id   = acc_in.id,
            customer_id  = acc_in.customer_id,
            account_type = acc_in.type,
            date         = now,
            description  = f"Transferencia recibida desde cuenta {acc_out.id}",
            amount       = amount,        # positivo
            type         = "credito",     # <- clave
        )

        db.add_all([mov_out, mov_in])
        db.commit()

        return {"message": "Transferencia realizada correctamente"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al procesar la transferencia: {e}")

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

@app.post("/payments")
def create_pse_payment(
    data: PSETransactionCreate,
    db: Session = Depends(get_db),
):
    # 1. Obtener la cuenta de origen
    account = (
        db.query(AccountDB)
        .filter(AccountDB.id == data.account_id)
        .first()
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Cuenta de origen no encontrada",
        )
    # 3. Validar saldo suficiente
    if account.balance < data.amount:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Saldo insuficiente en la cuenta #{account.id}. "
                f"Saldo disponible: {account.balance:.2f}"
            ),
        )

    # 4. Crear la orden PSE
    try:
        internal_order_id = f"PSE-{uuid4().hex[:20]}"

        tx = PSETransactionDB(
            internal_order_id=internal_order_id,
            customer_id=data.customer_id,
            account_id=data.account_id,
            amount=data.amount,
            currency=data.currency,
            status="PENDING",
            provider="PSE",
            payment_url="",  # Flask puede construir la URL externa
            return_url_success=data.return_url_success,
            return_url_failure=data.return_url_failure,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )

        db.add(tx)
        db.commit()
        db.refresh(tx)

        return {
            "id": tx.id,
            "internal_order_id": tx.internal_order_id,
            "status": tx.status,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al crear la orden PSE: {e}",
        )


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
