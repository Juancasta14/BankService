from sqlalchemy.orm import Session
from bankservice.application.banking.ports.outbound.unit_of_work import UnitOfWork
from .account_repository_sqlalchemy import AccountRepositorySqlAlchemy
from .movement_repository_sqlalchemy import MovementRepositorySqlAlchemy
from .pse_transaction_repository_sqlalchemy import PSETransactionRepositorySqlAlchemy

class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, db: Session):
        self.db = db
        self.accounts = AccountRepositorySqlAlchemy(db)
        self.movements = MovementRepositorySqlAlchemy(db)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()


class SqlAlchemyPSEUnitOfWork:
    def __init__(self, db: Session):
        self.db = db
        self.accounts = AccountRepositorySqlAlchemy(db)
        self.pse = PSETransactionRepositorySqlAlchemy(db)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
