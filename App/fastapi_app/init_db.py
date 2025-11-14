from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import AccountDB, WalletDB


def init():
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        if db.query(AccountDB).first():
            print("La BD ya tiene datos, no se insertará nada.")
            return

        cuentas = [
            AccountDB(id=1, customer_id=100, type="ahorros", balance=1500.75),
            AccountDB(id=2, customer_id=100, type="corriente", balance=250.00),
            AccountDB(id=3, customer_id=101, type="ahorros", balance=9999.99),
        ]

        billeteras = [
            WalletDB(id=1, customer_id=100, balance=300.00),
            WalletDB(id=2, customer_id=101, balance=50.50),
        ]

        db.add_all(cuentas + billeteras)
        db.commit()
        print("Datos de ejemplo insertados.")

    finally:
        db.close()


if __name__ == "__main__":
    init()