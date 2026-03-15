import pytest
from dataclasses import dataclass

from application.customers.ports.outbound.movements_repository import MovementsRepository
from application.customers.ports.outbound.wallets_repository import WalletsRepository

from application.customers.services.get_accounts_service import GetAccountsService
from application.customers.services.get_movements_service import GetMovementsService
from application.customers.services.get_wallet_service import GetWalletService
from application.customers.services.get_summary_service import GetSummaryService


@dataclass
class MockAccount:
    balance: float


@dataclass
class MockWallet:
    balance: float


class MockAccountsRepository:
    def list_by_customer(self, customer_id: int):
        if customer_id == 1:
            return [MockAccount(balance=100.0), MockAccount(balance=200.0)]
        return []


class MockWalletsRepository:
    def get_by_customer(self, customer_id: int):
        if customer_id == 1:
            return MockWallet(balance=50.0)
        return None


class MockMovementsRepository:
    def list_by_customer(
        self, customer_id: int, account_type=None, date_from=None, date_to=None
    ):
        if customer_id == 1:
            return [{"amount": 50.0}, {"amount": -10.0}]
        return []


@pytest.fixture
def accounts_repo():
    return MockAccountsRepository()


@pytest.fixture
def wallets_repo():
    return MockWalletsRepository()


@pytest.fixture
def movements_repo():
    return MockMovementsRepository()


def test_get_accounts(accounts_repo):
    service = GetAccountsService(accounts_repo=accounts_repo)
    result = service.execute(customer_id=1)
    assert len(result) == 2

    result_empty = service.execute(customer_id=99)
    assert len(result_empty) == 0


def test_get_wallet(wallets_repo):
    service = GetWalletService(wallets_repo=wallets_repo)
    assert service.execute(customer_id=1).balance == 50.0
    assert service.execute(customer_id=99) is None


def test_get_movements(movements_repo):
    service = GetMovementsService(movements_repo=movements_repo)
    result = service.execute(customer_id=1)
    assert len(result) == 2

    result_empty = service.execute(customer_id=99)
    assert len(result_empty) == 0


def test_get_summary(accounts_repo, wallets_repo):
    service = GetSummaryService(accounts_repo=accounts_repo, wallets_repo=wallets_repo)

    # Test valid customer
    accounts, wallet, total = service.execute(customer_id=1)
    assert len(accounts) == 2
    assert wallet.balance == 50.0
    assert total == 350.0  # 100 + 200 + 50

    # Test customer without accounts or wallet
    result_none = service.execute(customer_id=99)
    assert result_none is None
