from typing import Protocol, List

class AccountsRepository(Protocol):
    def list_by_customer(self, customer_id: int):
        ...
