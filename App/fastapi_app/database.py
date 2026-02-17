import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER", "postgres.xponoxoiqjmkslmqazsu")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "j03g33$gay**")
    DB_HOST = os.getenv("DB_HOST", "aws-0-us-west-2.pooler.supabase.com")
    DB_PORT = os.getenv("DB_PORT", "6543")  # Pooler port
    DB_NAME = os.getenv("DB_NAME", "postgres")


    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?sslmode=require"
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
