from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from enum import Enum
import os
import sys

# DEBUG para CI
DB_PROVIDER = os.getenv("DB_PROVIDER", "supabase").lower()
print(f"DEBUG: models.py loaded with DB_PROVIDER={DB_PROVIDER}", file=sys.stderr)

Base = declarative_base()

# SQLite (provider="memory") no soporta esquemas (schemas)
DB_PROVIDER = os.getenv("DB_PROVIDER", "supabase").lower()
SCHEMA = "public" if DB_PROVIDER != "memory" else None


class AccountDB(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": SCHEMA} if SCHEMA else {}

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True, nullable=False)
    type = Column(String, nullable=False)
    balance = Column(Float, nullable=False)


class MovementType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER_OUT = "transfer_out"
    TRANSFER_IN = "transfer_in"


class WalletDB(Base):
    __tablename__ = "wallets"
    __table_args__ = {"schema": SCHEMA} if SCHEMA else {}

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True, nullable=False)
    balance = Column(Float, nullable=False)


class UserDB(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": SCHEMA} if SCHEMA else {}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class MovementDB(Base):
    __tablename__ = "movements"
    __table_args__ = {"schema": SCHEMA} if SCHEMA else {}

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, index=True, nullable=False)
    account_type = Column(String, nullable=True)  # "ahorros", "corriente", etc.

    date = Column(String, nullable=False)

    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(
        String, nullable=False
    )  # "credit"/"debit" (ideal: usar Enum a futuro)


class PSETransactionDB(Base):
    __tablename__ = "pse_transactions"
    __table_args__ = {"schema": SCHEMA} if SCHEMA else {}

    id = Column(Integer, primary_key=True, index=True)

    internal_order_id = Column(String(64), unique=True, index=True, nullable=False)

    customer_id = Column(Integer, index=True, nullable=False)

    account_id = Column(Integer, ForeignKey(f"{SCHEMA}.accounts.id" if SCHEMA else "accounts.id"), nullable=False)

    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="COP")

    status = Column(String(20), nullable=False, default="CREATED")

    provider = Column(String(50), nullable=False, default="PSE")
    provider_tx_id = Column(String(100), nullable=True)
    provider_reference = Column(String(100), nullable=True)
    payment_url = Column(String, nullable=True)

    callback_status_raw = Column(String, nullable=True)

    return_url_success = Column(String, nullable=True)
    return_url_failure = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=True)

    account = relationship("AccountDB", backref="pse_transactions")
