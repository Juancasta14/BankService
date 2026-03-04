from dataclasses import dataclass


@dataclass
class MockAccount:
    id: int
    customer_id: int
    balance: float
    type: str = "ahorros"


class MockAccountsRepository:
    def __init__(self):
        self.accounts = {}

    def add(self, account: MockAccount):
        self.accounts[account.id] = account

    def get(self, account_id: int):
        return self.accounts.get(account_id)

    def save(self, account) -> None:
        self.accounts[account.id] = account


class MockMovementsRepository:
    def __init__(self):
        self.movements = []

    def add_transfer_movements(
        self,
        acc_out_id: int,
        acc_in_id: int,
        customer_out_id: int,
        customer_in_id: int,
        acc_out_type: str,
        acc_in_type: str,
        date: str,
        amount: float,
    ):
        self.movements.append(
            {
                "acc_out_id": acc_out_id,
                "acc_in_id": acc_in_id,
                "customer_out_id": customer_out_id,
                "customer_in_id": customer_in_id,
                "acc_out_type": acc_out_type,
                "acc_in_type": acc_in_type,
                "date": date,
                "amount": amount,
            }
        )


class MockUnitOfWork:
    def __init__(self):
        self.accounts = MockAccountsRepository()
        self.movements = MockMovementsRepository()
        self.committed = False

    def commit(self):
        self.committed = True
