from typing import Protocol, Optional, List

class MovementsRepository(Protocol):
    def list_by_customer(
        self,
        customer_id: int,
        account_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ):
        ...
