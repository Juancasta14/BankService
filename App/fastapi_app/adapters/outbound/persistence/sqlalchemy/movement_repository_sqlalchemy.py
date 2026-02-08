from sqlalchemy.orm import Session
from models import MovementDB 
from bankservice.application.banking.ports.outbound.movement_repository import MovementRepository
from adapters.outbound.persistence.sqlalchemy.models import MovementDB

class MovementRepositorySqlAlchemy(MovementRepository):
    def __init__(self, db: Session):
        self.db = db

    def add_transfer_movements(
        self,
        *,
        acc_out_id: int,
        acc_in_id: int,
        customer_out_id: int,
        customer_in_id: int,
        acc_out_type: str,
        acc_in_type: str,
        amount: float,
        date_str: str,
    ) -> None:
        mov_out = MovementDB(
            account_id=acc_out_id,
            customer_id=customer_out_id,
            account_type=acc_out_type,
            date=date_str,
            description=f"Transferencia enviada a cuenta {acc_in_id}",
            amount=amount,
            type="debito",
        )
        mov_in = MovementDB(
            account_id=acc_in_id,
            customer_id=customer_in_id,
            account_type=acc_in_type,
            date=date_str,
            description=f"Transferencia recibida desde cuenta {acc_out_id}",
            amount=amount,
            type="credito",
        )
        self.db.add_all([mov_out, mov_in])


class MovementRepositorySqlAlchemy:
    def __init__(self, db: Session):
        self.db = db

    def add_credit(
        self,
        *,
        account_id: int,
        customer_id: int,
        account_type: str | None,
        date: str,
        description: str,
        amount: float,
        type: str = "credito",
    ) -> None:
        mov = MovementDB(
            account_id=account_id,
            customer_id=customer_id,
            account_type=account_type,
            date=date,
            description=description,
            amount=amount,
            type=type,
        )
        self.db.add(mov)
