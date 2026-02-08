from typing import Protocol
from .account_repository import AccountRepository
from .movement_repository import MovementRepository

class UnitOfWork(Protocol):
    accounts: AccountRepository
    movements: MovementRepository
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
