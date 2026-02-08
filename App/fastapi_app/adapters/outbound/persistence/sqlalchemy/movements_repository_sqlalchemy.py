from sqlalchemy.orm import Session
from adapters.outbound.persistence.sqlalchemy.models import MovementDB

class MovementsRepositorySqlAlchemy:
    def __init__(self, db: Session):
        self.db = db

    def list_by_customer(self, customer_id: int, account_type=None, date_from=None, date_to=None):
        q = self.db.query(MovementDB).filter(MovementDB.customer_id == customer_id)

        if account_type:
            q = q.filter(MovementDB.account_type == account_type)
        if date_from:
            q = q.filter(MovementDB.date >= date_from)
        if date_to:
            q = q.filter(MovementDB.date <= date_to)

        return q.order_by(MovementDB.date.desc(), MovementDB.id.desc()).all()
    