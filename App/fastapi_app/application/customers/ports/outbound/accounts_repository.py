from typing import Protocol

class AccountsRepository(Protocol):
    def get(self, account_id: int):
        ...

    def save(self, account) -> None:
        ...
