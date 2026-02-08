from sqlalchemy.orm import Session
from adapters.outbound.persistence.sqlalchemy.models import WalletDB

class WalletsRepositorySqlAlchemy:
    def __init__(self, db: Session):
        self.db = db

    def get_by_customer(self, customer_id: int):
        return self.db.query(WalletDB).filter(WalletDB.customer_id == customer_id).first()
