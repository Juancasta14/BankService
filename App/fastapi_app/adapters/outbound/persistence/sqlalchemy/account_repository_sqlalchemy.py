from sqlalchemy.orm import Session
from bankservice.application.banking.ports.outbound.account_repository import AccountRepository
from models import AccountDB  # tu modelo actual :contentReference[oaicite:2]{index=2}

class AccountRepositorySqlAlchemy(AccountRepository):
    def __init__(self, db: Session):
        self.db = db

    def get(self, account_id: int):
        return self.db.query(AccountDB).filter(AccountDB.id == account_id).first()

    def save(self, account) -> None:
        # account ya es una instancia trackeada por SQLAlchemy
        self.db.add(account)
