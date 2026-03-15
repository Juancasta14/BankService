import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Any

# ─────────────────────────────────────────────────────────────────
#  DB_PROVIDER switch
#  Allowed values: "postgres" | "supabase" | "memory"
#  Set in .env or docker-compose environment section.
# ─────────────────────────────────────────────────────────────────
DB_PROVIDER = os.getenv("DB_PROVIDER", "supabase").lower()
print(f"DEBUG: database.py loaded with DB_PROVIDER={DB_PROVIDER}", file=sys.stderr)

connect_args: dict[str, Any] = {}

if DB_PROVIDER == "memory":
    # SQLite en RAM — útil para desarrollo rápido sin Docker
    DATABASE_URL = "sqlite:///:memory:"
    connect_args["check_same_thread"] = False

elif DB_PROVIDER == "supabase":
    # Supabase (PostgreSQL remoto con SSL obligatorio)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        DB_USER     = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST     = os.getenv("DB_HOST")
        DB_PORT     = os.getenv("DB_PORT", "6543")
        DB_NAME     = os.getenv("DB_NAME", "postgres")

        if not all([DB_USER, DB_PASSWORD, DB_HOST]):
            # En vez de KeyError, damos un mensaje más claro o fallamos solo al conectar
            DATABASE_URL = "postgresql://missing_user:missing_pass@missing_host:5432/missing_db"
        else:
            DATABASE_URL = (
                f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
                f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
                f"?sslmode=require"
            )
    connect_args["options"] = "-c search_path=public"

else:
    # postgres — PostgreSQL local (Docker o instancia propia sin SSL)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        DB_USER     = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST     = os.getenv("DB_HOST")
        DB_PORT     = os.getenv("DB_PORT", "5432")
        DB_NAME     = os.getenv("DB_NAME", "postgres")
        DB_SSLMODE  = os.getenv("DB_SSLMODE", "disable")

        if not all([DB_USER, DB_PASSWORD, DB_HOST]):
            DATABASE_URL = "postgresql://missing_user:missing_pass@missing_host:5432/missing_db"
        else:
            DATABASE_URL = (
                f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
                f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
                f"?sslmode={DB_SSLMODE}"
            )
    connect_args["options"] = "-c search_path=public"

# ─────────────────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
