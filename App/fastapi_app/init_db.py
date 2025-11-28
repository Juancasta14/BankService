# fastapi_app/init_db.py

from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, AccountDB, WalletDB, UserDB, MovementDB
from security import hash_password


def init():
    print("== Creando tablas si no existen ==")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # -------- Usuarios por defecto --------
        print("== Revisando usuarios ==")
        existing_users = db.query(UserDB).all()
        if not existing_users:
            admin_user = UserDB(
                username="admin",
                hashed_password=hash_password("admin123"),
            )
            normal_user = UserDB(
                username="user",
                hashed_password=hash_password("user123"),
            )
            db.add_all([admin_user, normal_user])
            print("Usuarios creados:")
            print(" - admin / password123")
            print(" - user / user123")
        else:
            user_user = (
                db.query(UserDB)
                .filter(UserDB.username == "user")
                .first()
            )
            if not user_user:
                user_user = UserDB(
                    username="user",
                    hashed_password=hash_password("user123"),
                )
                db.add(user_user)
                print("Usuario adicional creado: user / user123")
            else:
                print("Ya existe al menos un usuario, no se crean nuevos.")

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

        # -------- Movimientos de ejemplo --------
        print("== Revisando movimientos ==")
        if not db.query(MovementDB).first():
            movimientos = [
                # Cliente 100
                MovementDB(
                    account_id=1,
                    customer_id=100,
                    account_type="ahorros",
                    date="2025-11-15",
                    description="Nómina",
                    amount=1200.00,
                    type="credito",
                ),
                MovementDB(
                    account_id=1,
                    customer_id=100,
                    account_type="ahorros",
                    date="2025-11-16",
                    description="Pago supermercado",
                    amount=150.50,
                    type="debito",
                ),
                MovementDB(
                    account_id=2,
                    customer_id=100,
                    account_type="corriente",
                    date="2025-11-17",
                    description="Pago tarjeta de crédito",
                    amount=300.00,
                    type="debito",
                ),
                MovementDB(
                    account_id=2,
                    customer_id=100,
                    account_type="corriente",
                    date="2025-11-18",
                    description="Transferencia recibida",
                    amount=500.00,
                    type="credito",
                ),
                # Cliente 101
                MovementDB(
                    account_id=3,
                    customer_id=101,
                    account_type="ahorros",
                    date="2025-11-14",
                    description="Depósito en efectivo",
                    amount=2000.00,
                    type="credito",
                ),
                MovementDB(
                    account_id=3,
                    customer_id=101,
                    account_type="ahorros",
                    date="2025-11-19",
                    description="Pago servicios públicos",
                    amount=220.75,
                    type="debito",
                ),
            ]
            db.add_all(movimientos)
            print("Movimientos de ejemplo insertados.")
        else:
            print("Ya existen movimientos en la BD, no se insertan nuevos.")

        db.commit()
        print("== Inicialización completada. ==")

    except Exception as e:
        print("ERROR en init_db:", e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init()
