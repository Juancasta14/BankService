from dataclasses import dataclass

@dataclass
class GetAccountsService:
    accounts_repo: any

    def execute(self, customer_id: int):
        return self.accounts_repo.list_by_customer(customer_id)
