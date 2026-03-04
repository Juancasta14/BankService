from typing import Protocol


class WalletsRepository(Protocol):
    def get_by_customer(self, customer_id: int): ...
