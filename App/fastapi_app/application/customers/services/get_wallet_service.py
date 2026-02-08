from dataclasses import dataclass

@dataclass
class GetWalletService:
    wallets_repo: any

    def execute(self, customer_id: int):
        return self.wallets_repo.get_by_customer(customer_id)
