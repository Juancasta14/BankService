import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ─────────────────────────────────────────────────────────────────
#  DB_PROVIDER switch
#  Allowed values: "postgres" | "supabase" | "memory"
#  Set in .env or docker-compose environment section.
# ─────────────────────────────────────────────────────────────────
DB_PROVIDER = os.getenv("DB_PROVIDER", "supabase").lower()

connect_args = {}

if DB_PROVIDER == "memory":
    # SQLite en RAM — útil para desarrollo rápido sin Docker
    DATABASE_URL = "sqlite:///:memory:"
    connect_args["check_same_thread"] = False

elif DB_PROVIDER == "supabase":
    # Supabase (PostgreSQL remoto con SSL obligatorio)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        DB_USER     = os.environ["DB_USER"]
        DB_PASSWORD = os.environ["DB_PASSWORD"]
        DB_HOST     = os.environ["DB_HOST"]
        DB_PORT     = os.getenv("DB_PORT", "5432")
        DB_NAME     = os.getenv("DB_NAME", "postgres")
        DATABASE_URL = (
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            f"?sslmode=require"             # Supabase siempre exige SSL
        )
    connect_args["options"] = "-c search_path=public"

else:
    # postgres — PostgreSQL local (Docker o instancia propia sin SSL)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        DB_USER     = os.environ["DB_USER"]
        DB_PASSWORD = os.environ["DB_PASSWORD"]
        DB_HOST     = os.environ["DB_HOST"]
        DB_PORT     = os.getenv("DB_PORT", "5432")
        DB_NAME     = os.getenv("DB_NAME", "postgres")
        DB_SSLMODE  = os.getenv("DB_SSLMODE", "disable")
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
