from sqlalchemy.orm import Session
from bankservice.application.banking.ports.outbound.account_repository import AccountRepository
from adapters.outbound.persistence.sqlalchemy.models import AccountDB

class AccountRepositorySqlAlchemy(AccountRepository):
    def __init__(self, db: Session):
        self.db = db

    def get(self, account_id: int):
        return self.db.query(AccountDB).filter(AccountDB.id == account_id).first()

    def save(self, account) -> None:
        # account ya es una instancia trackeada por SQLAlchemy
        self.db.add(account)


class AccountRepositorySqlAlchemy:
    def __init__(self, db: Session):
        self.db = db

    def get(self, account_id: int):
        return self.db.query(AccountDB).filter(AccountDB.id == account_id).first()

    def save(self, account) -> None:
        self.db.add(account)

