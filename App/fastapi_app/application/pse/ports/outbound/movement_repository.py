from typing import Protocol, Optional


class MovementRepository(Protocol):
    def add_credit(
        self,
        *,
        account_id: int,
        customer_id: int,
        account_type: Optional[str],
        date: str,
        description: str,
        amount: float,
    ) -> None:
        """Registra un movimiento tipo crédito (ej. PSE callback, abonos)."""
        ...

    def add_transfer_movements(
        self,
        *,
        acc_out_id: int,
        acc_in_id: int,
        customer_out_id: int,
        customer_in_id: int,
        acc_out_type: Optional[str],
        acc_in_type: Optional[str],
        date: str,
        amount: float,
    ) -> None:
        """Registra los 2 movimientos de una transferencia: débito y crédito."""
        ...
