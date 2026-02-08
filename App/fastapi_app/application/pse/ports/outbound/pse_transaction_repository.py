from typing import Protocol, Optional
from datetime import datetime

class PSETransactionRepository(Protocol):
    def get_by_internal_order_id(self, internal_order_id: str):
        ...

    def add(self, tx) -> None:
        ...

    def save(self, tx) -> None:
        ...
