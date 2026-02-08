from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from adapters.inbound.http.dependencies import get_current_user
from adapters.inbound.http.dto.customer_dto import Account, Wallet, Movement, CustomerSummary

from adapters.outbound.persistence.sqlalchemy.models import UserDB

from adapters.outbound.persistence.sqlalchemy.accounts_repository_sqlalchemy import AccountsRepositorySqlAlchemy
from adapters.outbound.persistence.sqlalchemy.wallets_repository_sqlalchemy import WalletsRepositorySqlAlchemy
from adapters.outbound.persistence.sqlalchemy.movements_repository_sqlalchemy import MovementsRepositorySqlAlchemy

# Services (casos de uso)
from application.customers.services.get_accounts_service import GetAccountsService
from application.customers.services.get_wallet_service import GetWalletService
from application.customers.services.get_movements_service import GetMovementsService
from application.customers.services.get_summary_service import GetSummaryService


router = APIRouter(prefix="/customers", tags=["customers"])


def build_services(db: Session):
    accounts_repo = AccountsRepositorySqlAlchemy(db)
    wallets_repo = WalletsRepositorySqlAlchemy(db)
    movements_repo = MovementsRepositorySqlAlchemy(db)

    return {
        "accounts": GetAccountsService(accounts_repo),
        "wallet": GetWalletService(wallets_repo),
        "movements": GetMovementsService(movements_repo),
        "summary": GetSummaryService(accounts_repo, wallets_repo),
    }


@router.get("/{customer_id}/accounts", response_model=List[Account])
def get_accounts(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    svcs = build_services(db)
    rows = svcs["accounts"].execute(customer_id)
    return [Account.model_validate(r) for r in rows]


@router.get("/{customer_id}/wallet", response_model=Optional[Wallet])
def get_wallet(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    svcs = build_services(db)
    row = svcs["wallet"].execute(customer_id)
    return None if row is None else Wallet.model_validate(row)


@router.get("/{customer_id}/summary", response_model=CustomerSummary)
def get_customer_summary(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    svcs = build_services(db)
    result = svcs["summary"].execute(customer_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Cliente sin productos")

    accounts, wallet, total = result
    return CustomerSummary(
        customer_id=customer_id,
        accounts=[Account.model_validate(a) for a in accounts],
        wallet=None if wallet is None else Wallet.model_validate(wallet),
        total_balance=total,
    )


@router.get("/{customer_id}/movements", response_model=List[Movement])
def get_customer_movements(
    customer_id: int,
    account_type: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    svcs = build_services(db)
    rows = svcs["movements"].execute(
        customer_id=customer_id,
        account_type=account_type,
        date_from=date_from,
        date_to=date_to,
    )

    return rows
