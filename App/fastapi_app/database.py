import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# Nuevo: sslmode configurable por ambiente
DB_SSLMODE = os.getenv("DB_SSLMODE")  # "disable" (local) o "require" (supabase)

if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "6543")
    DB_NAME = os.getenv("DB_NAME", "postgres")

    if not all([DB_USER, DB_PASSWORD, DB_HOST]):
        raise RuntimeError("Database environment variables are not set")

    # Default inteligente:
    # - si el host es el contenedor local "db" => disable
    # - si no => require (Supabase normalmente)
    if not DB_SSLMODE:
        DB_SSLMODE = "disable" if DB_HOST == "db" else "require"

    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={DB_SSLMODE}"
    )
else:
    # Si viene DATABASE_URL ya armada, y no trae sslmode, se lo agregamos
    if "sslmode=" not in DATABASE_URL:
        if not DB_SSLMODE:
            DB_SSLMODE = "require"  # razonable para URLs tipo Supabase
        sep = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL = f"{DATABASE_URL}{sep}sslmode={DB_SSLMODE}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"options": "-c search_path=public"},
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