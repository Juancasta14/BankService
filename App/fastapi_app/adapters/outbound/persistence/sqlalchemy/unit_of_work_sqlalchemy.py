from sqlalchemy.orm import Session

from application.pse.ports.outbound.unit_of_work import UnitOfWork
from .account_repository_sqlalchemy import AccountsRepositorySqlAlchemy
from .movement_repository_sqlalchemy import MovementRepositorySqlAlchemy
from .pse_transaction_repository_sqlalchemy import PSETransactionRepositorySqlAlchemy


class SqlAlchemyUnitOfWork(UnitOfWork):
    """
    UoW para operaciones bancarias (transferencias, movimientos, cuentas)
    """
    def __init__(self, db: Session):
        self.db = db
        self.accounts = AccountRepositorySqlAlchemy(db)
        self.movements = MovementRepositorySqlAlchemy(db)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()


class SqlAlchemyPSEUnitOfWork(UnitOfWork):
    """
    UoW para flujos PSE (payments, callback, gateway)
    """
    def __init__(self, db: Session):
        self.db = db
        self.accounts = AccountRepositorySqlAlchemy(db)
        self.movements = MovementRepositorySqlAlchemy(db)
        self.pse = PSETransactionRepositorySqlAlchemy(db)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
