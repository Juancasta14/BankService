from sqlalchemy.orm import Session
from fastapi_app.adapters.outbound.persistence.sqlalchemy.models import AccountDB

class AccountsRepositorySqlAlchemy:
    def __init__(self, db: Session):
        self.db = db

    def list_by_customer(self, customer_id: int):
        return self.db.query(AccountDB).filter(AccountDB.customer_id == customer_id).all()
