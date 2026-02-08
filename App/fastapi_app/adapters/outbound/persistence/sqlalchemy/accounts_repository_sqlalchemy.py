from sqlalchemy.orm import Session
from adapters.outbound.persistence.sqlalchemy.models import AccountDB
from application.customers.ports.outbound.accounts_repository import AccountsRepository


class AccountsRepositorySqlAlchemy(AccountsRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_by_customer(self, customer_id: int):
        return self.db.query(AccountDB).filter(
            AccountDB.customer_id == customer_id
        ).all()

    def get(self, account_id: int):
        return self.db.query(AccountDB).filter(
            AccountDB.id == account_id
        ).first()

    def save(self, account: AccountDB) -> None:
        self.db.add(account)
