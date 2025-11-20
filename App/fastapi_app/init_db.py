# fastapi_app/init_db.py

from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, AccountDB, WalletDB, UserDB
from security import hash_password


def init():
    print("== Creando tablas si no existen ==")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # -------- Usuario por defecto --------
        print("== Revisando usuarios ==")
        user = db.query(UserDB).first()
        if not user:
            new_user = UserDB(
                username="admin",
                hashed_password=hash_password("password123"),
            )
            db.add(new_user)
            print("Usuario creado: admin / password123")
        else:
            print("Ya existe al menos un usuario, no se crea otro.")

        # -------- Cuentas y billeteras --------
        print("== Revisando cuentas ==")
        if not db.query(AccountDB).first():
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
            print("Cuentas y billeteras insertadas.")
        else:
            print("Ya existen cuentas en la BD, no se insertan nuevas.")

        db.commit()
        print("== Inicialización completada. ==")

    except Exception as e:
        print("ERROR en init_db:", e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init()
