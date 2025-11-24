 # fastapi_app/models.py

from typing import List, Optional

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, Session, relationship
from pydantic import BaseModel
from datetime import date
from datetime import datetime
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

class PSETransactionDB(Base):
    __tablename__ = "pse_transactions"

    id = Column(Integer, primary_key=True, index=True)

    # Identificador interno de tu banco (único por orden)
    internal_order_id = Column(String(64), unique=True, index=True, nullable=False)

    # Relación con el cliente y la cuenta origen del débito
    customer_id = Column(Integer, index=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)

    # Datos financieros
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="COP")

    # Estado de la transacción: CREATED, PENDING, SUCCESS, FAILED, EXPIRED, CANCELED
    status = Column(String(20), nullable=False, default="CREATED")

    # Información del proveedor (PSE / pasarela)
    provider = Column(String(50), nullable=False, default="PSE")
    provider_tx_id = Column(String(100), nullable=True)
    provider_reference = Column(String(100), nullable=True)
    payment_url = Column(String, nullable=True)

    # Último payload crudo del callback
    callback_status_raw = Column(String, nullable=True)

    # URLs de retorno para el front del banco
    return_url_success = Column(String, nullable=True)
    return_url_failure = Column(String, nullable=True)

    # Tiempos de auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    # Relación opcional con la cuenta
    account = relationship("AccountDB", backref="pse_transactions")

class PSETransferDB(Base):
    __tablename__ = "pse_transfers"

    id = Column(Integer, primary_key=True, index=True)
    source_account_id = Column(Integer, nullable=False)
    destination_bank = Column(String, nullable=False)
    destination_account = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

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

class PSETransactionCreate(BaseModel):
    customer_id: int
    account_id: int
    amount: float
    currency: str = "COP"
    return_url_success: Optional[str] = None
    return_url_failure: Optional[str] = None
    metadata: Optional[dict] = None

class PSETransactionOut(BaseModel):
    id: int
    internal_order_id: str
    customer_id: int
    account_id: int
    amount: float
    currency: str
    status: str
    provider: str
    provider_tx_id: Optional[str] = None
    provider_reference: Optional[str] = None
    payment_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # antes orm_mode = True


class PSECallbackIn(BaseModel):
    internal_order_id: str
    status: str                    
    provider_tx_id: Optional[str] = None
    provider_reference: Optional[str] = None
    raw_payload: Optional[dict] = None

class PSETransferCreate(BaseModel):
    source_account_id: int
    destination_bank: str
    destination_account: str
    amount: float
    description: str | None = None


class PSETransferResponse(BaseModel):
    id: int
    source_account_id: int
    destination_bank: str
    destination_account: str
    amount: float
    description: str | None
    status: str
    created_at: str

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

def get_account_by_id(db: Session, account_id: int) -> Optional[AccountDB]:
    return db.query(AccountDB).filter(AccountDB.id == account_id).first()
