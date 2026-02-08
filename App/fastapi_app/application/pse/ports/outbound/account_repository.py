from typing import Protocol, Optional

class AccountRepository(Protocol):
    def get(self, account_id: int):
        ...
    def save(self, account) -> None:
        ...
