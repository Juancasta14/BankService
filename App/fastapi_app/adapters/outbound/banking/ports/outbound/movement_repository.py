from typing import Protocol

class MovementRepository(Protocol):
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
    ) -> None: ...
