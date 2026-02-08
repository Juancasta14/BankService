from typing import Protocol, Optional

class WalletsRepository(Protocol):
    def get_by_customer(self, customer_id: int):
        ...
