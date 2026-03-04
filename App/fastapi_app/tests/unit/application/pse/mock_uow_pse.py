from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class MockAccount:
    id: int
    customer_id: int
    balance: float
    type: str = "ahorros"


@dataclass
class MockPSETransaction:
    id: int
    internal_order_id: str
    customer_id: int
    account_id: int
    amount: float
    currency: str
    status: str
    provider: str
    payment_url: str
    return_url_success: str
    return_url_failure: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    provider_tx_id: Optional[str] = None
    provider_reference: Optional[str] = None
    callback_status_raw: Optional[str] = None


class MockAccountsRepository:
    def __init__(self):
        self.accounts = {}

    def get(self, account_id: int):
        return self.accounts.get(account_id)

    def save(self, account) -> None:
        self.accounts[account.id] = account


class MockPSERepository:
    def __init__(self):
        self.transactions = {}
        self.counter = 1

    def new_tx(self, **kwargs) -> MockPSETransaction:
        tx = MockPSETransaction(id=self.counter, **kwargs)
        self.counter += 1
        return tx

    def add(self, tx: MockPSETransaction):
        self.transactions[tx.internal_order_id] = tx

    def save(self, tx: MockPSETransaction):
        self.transactions[tx.internal_order_id] = tx

    def get_by_internal_order_id(
        self, internal_order_id: str
    ) -> Optional[MockPSETransaction]:
        return self.transactions.get(internal_order_id)

    def serialize_payload(self, raw_payload: dict | None) -> str:
        import json

        return json.dumps(raw_payload) if raw_payload else "{}"


class MockMovementsRepository:
    def __init__(self):
        self.movements = []

    def add_credit(self, **kwargs):
        self.movements.append(kwargs)


class MockPSEUnitOfWork:
    def __init__(self):
        self.accounts = MockAccountsRepository()
        self.pse = MockPSERepository()
        self.movements = MockMovementsRepository()
        self.committed = False

    def commit(self):
        self.committed = True
