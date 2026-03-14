# tests/test_models.py
import pytest
from App.fastapi_app.models import (
    AccountDB,
    WalletDB,
    UserDB,
    MovementDB,
    get_accounts_by_customer,
    get_wallet_by_customer,
    get_user_by_username,
    get_movements_by_customer,
    get_account_by_id
)

def test_get_accounts_by_customer(db_session):
    # Setup test data
    acc1 = AccountDB(customer_id=1, type="ahorros", balance=100.0)
    acc2 = AccountDB(customer_id=1, type="corriente", balance=50.0)
    acc3 = AccountDB(customer_id=2, type="ahorros", balance=200.0)
    
    db_session.add_all([acc1, acc2, acc3])
    db_session.commit()
    
    # Test existing customer
    accounts = get_accounts_by_customer(db_session, 1)
    assert len(accounts) == 2
    assert {a.type for a in accounts} == {"ahorros", "corriente"}
    
    # Test non-existing customer
    assert get_accounts_by_customer(db_session, 99) == []

def test_get_wallet_by_customer(db_session):
    # Setup test data
    wallet = WalletDB(customer_id=1, balance=500.0)
    db_session.add(wallet)
    db_session.commit()
    
    # Existing wallet
    db_wallet = get_wallet_by_customer(db_session, 1)
    assert db_wallet is not None
    assert db_wallet.balance == 500.0
    
    # Non-existing wallet
    assert get_wallet_by_customer(db_session, 99) is None

def test_get_user_by_username(db_session):
    # Setup test data
    user = UserDB(username="testuser", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()
    
    # Existing user
    db_user = get_user_by_username(db_session, "testuser")
    assert db_user is not None
    assert db_user.username == "testuser"
    
    # Non-existing user
    assert get_user_by_username(db_session, "missing") is None

def test_get_movements_by_customer_filters(db_session):
    # Setup test data
    m1 = MovementDB(account_id=1, customer_id=1, account_type="ahorros", date="2025-01-01", description="test1", amount=10, type="credito")
    m2 = MovementDB(account_id=2, customer_id=1, account_type="corriente", date="2025-01-05", description="test2", amount=20, type="debito")
    m3 = MovementDB(account_id=3, customer_id=2, account_type="ahorros", date="2025-01-10", description="test3", amount=30, type="credito")
    
    db_session.add_all([m1, m2, m3])
    db_session.commit()
    
    # No filters
    movements = get_movements_by_customer(db_session, 1)
    assert len(movements) == 2
    assert [m.amount for m in movements] == [20, 10] # order desc
    
    # Filter by account_type
    movements_ahorros = get_movements_by_customer(db_session, 1, account_type="ahorros")
    assert len(movements_ahorros) == 1
    assert movements_ahorros[0].amount == 10
    
    # Filter by date_from
    movements_from_03 = get_movements_by_customer(db_session, 1, date_from="2025-01-03")
    assert len(movements_from_03) == 1
    assert movements_from_03[0].amount == 20
    
    # Empty result
    assert get_movements_by_customer(db_session, 99) == []

def test_get_account_by_id(db_session):
    # Setup test data
    acc = AccountDB(customer_id=1, type="ahorros", balance=100.0)
    db_session.add(acc)
    db_session.commit()
    
    # Notice we don't assign `id` explicitly but rely on SQLite's auto-increment which generates id=1
    db_acc = get_account_by_id(db_session, acc.id)
    assert db_acc is not None
    assert db_acc.balance == 100.0
    
    assert get_account_by_id(db_session, 999) is None

