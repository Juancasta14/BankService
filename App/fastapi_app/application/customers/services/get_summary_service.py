from dataclasses import dataclass

@dataclass
class GetSummaryService:
    accounts_repo: any
    wallets_repo: any

    def execute(self, customer_id: int):
        accounts = self.accounts_repo.list_by_customer(customer_id)
        wallet = self.wallets_repo.get_by_customer(customer_id)

        if (not accounts) and (wallet is None):
            return None

        total = sum(a.balance for a in accounts)
        if wallet:
            total += wallet.balance

        return accounts, wallet, total
