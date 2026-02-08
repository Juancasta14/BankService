from typing import Protocol
from .pse_transaction_repository import PSETransactionRepository
from .account_repository import AccountRepository

class UnitOfWork(Protocol):
    pse: PSETransactionRepository
    accounts: AccountRepository
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
