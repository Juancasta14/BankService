from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import Query
from pydantic import BaseModel


from database import get_db, engine
from models import (
    Base,
    AccountDB,
    WalletDB,
    UserDB,
    MovementDB,
    Account,
    Wallet,
    Movement,
    CustomerSummary,
    get_accounts_by_customer,
    get_wallet_by_customer,
    get_user_by_username,
    get_movements_by_customer,
)
from security import verify_password, create_access_token

app = FastAPI(title="Bank Service with Auth")

# Crear tablas (accounts, wallets, users...)
Base.metadata.create_all(bind=engine)

# Donde FastAPI “cree” que está el endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class TransferRequest(BaseModel):
    origin_account: int
    destination_account: int
    amount: float
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos",
        )

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
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

@app.post("/customers/{customer_id}/transfer")
def make_transfer(customer_id: int, data: TransferRequest, db: Session = Depends(get_db)):
    
    origin = db.query(AccountDB).filter(
        AccountDB.id == data.origin_account,
        AccountDB.customer_id == customer_id
    ).first()

    if not origin:
        raise HTTPException(404, "Cuenta de origen no encontrada o no pertenece al cliente")

    destination = db.query(AccountDB).filter(
        AccountDB.id == data.destination_account
    ).first()

    if not destination:
        raise HTTPException(404, "Cuenta destino no existe")

    if origin.balance < data.amount:
        raise HTTPException(400, "Fondos insuficientes")

    # Actualizar saldos
    origin.balance -= data.amount
    destination.balance += data.amount

    # Registrar movimientos
    mov_out = MovementDB(
        account_id=origin.id,
        amount=-data.amount,
        type="transfer_out",
        description=f"Transferencia enviada a cuenta {destination.id}"
    )
    mov_in = MovementDB(
        account_id=destination.id,
        amount=data.amount,
        type="transfer_in",
        description=f"Transferencia recibida desde cuenta {origin.id}"
    )

    db.add(mov_out)
    db.add(mov_in)
    db.commit()

    return {
        "message": "Transferencia realizada con éxito",
        "from": origin.id,
        "to": destination.id,
        "amount": data.amount
    }

@app.get("/")
def root():
    return {"message": "FastAPI Bank Service with Auth Running!"}
