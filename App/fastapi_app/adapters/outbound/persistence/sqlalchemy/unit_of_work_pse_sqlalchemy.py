from sqlalchemy.orm import Session
from .accounts_repository_sqlalchemy import AccountsRepositorySqlAlchemy
from .pse_transaction_repository_sqlalchemy import PSETransactionRepositorySqlAlchemy
from .movement_repository_sqlalchemy import MovementRepositorySqlAlchemy

class SqlAlchemyPSEUnitOfWork:
    def __init__(self, db: Session):
        self.db = db
        self.accounts = AccountsRepositorySqlAlchemy(db)
        self.pse = PSETransactionRepositorySqlAlchemy(db)
        self.movements = MovementRepositorySqlAlchemy(db)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
