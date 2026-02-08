from dataclasses import dataclass
from typing import Optional

@dataclass
class GetMovementsService:
    movements_repo: any

    def execute(
        self,
        *,
        customer_id: int,
        account_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ):
        return self.movements_repo.list_by_customer(
            customer_id=customer_id,
            account_type=account_type,
            date_from=date_from,
            date_to=date_to,
        )
