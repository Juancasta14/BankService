# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from database import get_db
from models import Base, UserDB, AccountDB, WalletDB, MovementDB, PSETransactionDB
from security import hash_password

# --- Setup in-memory DB for TestClient ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    # Setup
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # 1. Insert common test data
    test_user = UserDB(username="testuser", hashed_password=hash_password("testpass"))
    db.add(test_user)
    
    # Add accounts for a fake customer 100
    acc1 = AccountDB(customer_id=100, type="ahorros", balance=1500.0)
    acc2 = AccountDB(customer_id=100, type="corriente", balance=500.0)
    acc3 = AccountDB(customer_id=101, type="ahorros", balance=100.0) # different customer
    db.add_all([acc1, acc2, acc3])
    
    wallet = WalletDB(customer_id=100, balance=200.0)
    db.add(wallet)
    
    mov1 = MovementDB(account_id=1, customer_id=100, account_type="ahorros", date="2025-01-01", description="Depósito Inicial", amount=1500.0, type="credito")
    mov2 = MovementDB(account_id=2, customer_id=100, account_type="corriente", date="2025-01-02", description="Depósito Inicial", amount=500.0, type="credito")
    db.add_all([mov1, mov2])
    
    db.commit()
    db.close()
    
    yield
    
    # Teardown
    Base.metadata.drop_all(bind=engine)

# ================================
# TESTS PARA: /auth/login
# ================================
def test_login_success():
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "testuser"

def test_login_failure():
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuario o contraseña incorrectos"

def test_login_non_existent():
    response = client.post(
        "/auth/login",
        data={"username": "nobody", "password": "password"}
    )
    assert response.status_code == 400

# Helper function to get valid token
def get_auth_headers():
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ================================
# TESTS PARA PROTECTED ROUTES (Reads)
# ================================
def test_get_accounts_unauthorized():
    # No token provided
    response = client.get("/customers/100/accounts")
    assert response.status_code == 401

    # Invalid token provided
    response = client.get("/customers/100/accounts", headers={"Authorization": "Bearer invalid.token.here"})
    assert response.status_code == 401

def test_get_current_user_user_not_found():
    from security import create_access_token
    # Token valid, but user doesn't exist in DB
    token = create_access_token(data={"sub": "ghost_user"})
    response = client.get("/customers/100/accounts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Usuario no encontrado"

def test_get_accounts_authorized():
    headers = get_auth_headers()
    response = client.get("/customers/100/accounts", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["balance"] == 1500.0

def test_get_wallet_authorized():
    headers = get_auth_headers()
    response = client.get("/customers/100/wallet", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 200.0
    
def test_get_wallet_not_found():
    headers = get_auth_headers()
    response = client.get("/customers/999/wallet", headers=headers)
    assert response.status_code == 200
    assert response.json() is None

def test_get_customer_summary():
    headers = get_auth_headers()
    response = client.get("/customers/100/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["accounts"]) == 2
    assert data["wallet"] is not None
    assert data["total_balance"] == 1500.0 + 500.0 + 200.0 # acc1 + acc2 + wallet

def test_get_customer_summary_not_found():
    headers = get_auth_headers()
    response = client.get("/customers/999/summary", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Cliente sin productos"

def test_get_customer_movements():
    headers = get_auth_headers()
    response = client.get("/customers/100/movements", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Filters
    response = client.get("/customers/100/movements?account_type=ahorros", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["account_type"] == "ahorros"

# ================================
# TESTS PARA: Transferencias
# ================================
def test_make_transfer_success():
    headers = get_auth_headers()
    payload = {
        "from_account_id": 1,
        "to_account_id": 2,
        "amount": 200.0
    }
    response = client.post("/customers/100/transfer", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Transferencia realizada correctamente"
    
    # Verificar saldos
    acc1 = client.get("/customers/100/accounts", headers=headers).json()
    assert acc1[0]["balance"] == 1300.0 # 1500 - 200
    assert acc1[1]["balance"] == 700.0  # 500 + 200

def test_make_transfer_insufficient_funds():
    headers = get_auth_headers()
    payload = {
        "from_account_id": 1,
        "to_account_id": 2,
        "amount": 9000.0
    }
    response = client.post("/customers/100/transfer", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Fondos insuficientes" in response.json()["detail"]
    
def test_make_transfer_invalid_amount():
    headers = get_auth_headers()
    payload = {
        "from_account_id": 1,
        "to_account_id": 2,
        "amount": -50.0
    }
    response = client.post("/customers/100/transfer", json=payload, headers=headers)
    assert response.status_code == 400
    assert "mayor que cero" in response.json()["detail"]

def test_make_transfer_same_account():
    headers = get_auth_headers()
    payload = {
        "from_account_id": 1,
        "to_account_id": 1,
        "amount": 10.0
    }
    response = client.post("/customers/100/transfer", json=payload, headers=headers)
    assert response.status_code == 400
    assert "no pueden ser iguales" in response.json()["detail"]

def test_make_transfer_from_not_found():
    headers = get_auth_headers()
    payload = {"from_account_id": 999, "to_account_id": 2, "amount": 10.0}
    response = client.post("/customers/100/transfer", json=payload, headers=headers)
    assert response.status_code == 404
    assert "Cuenta de origen" in response.json()["detail"]

def test_make_transfer_to_not_found():
    headers = get_auth_headers()
    payload = {"from_account_id": 1, "to_account_id": 999, "amount": 10.0}
    response = client.post("/customers/100/transfer", json=payload, headers=headers)
    assert response.status_code == 404
    assert "Cuenta de destino" in response.json()["detail"]

# ================================
# TESTS PARA: Flujo PSE
# ================================
def test_create_pse_payment_success():
    headers = get_auth_headers()
    payload = {
        "customer_id": 100,
        "account_id": 1,
        "amount": 300.0,
        "currency": "COP",
        "return_url_success": "http://success",
        "return_url_failure": "http://failure"
    }
    response = client.post("/payments", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "internal_order_id" in data
    assert data["status"] == "PENDING"
    
    return data["internal_order_id"]

def test_create_pse_payment_insufficient_funds():
    headers = get_auth_headers()
    payload = {
        "customer_id": 100,
        "account_id": 1,
        "amount": 99999.0,
    }
    response = client.post("/payments", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Saldo insuficiente" in response.json()["detail"]

def test_pse_gateway_valid_transaction():
    # Setup a pending transaction
    order_id = test_create_pse_payment_success()
    
    # Hit the gateway (simulates PSE approval/rejection)
    response = client.get(f"/pse-gateway/{order_id}", follow_redirects=False)
    
    # Because of random approval (90%), it will redirect to either success or failure URL
    assert response.status_code in [302, 303, 307]
    assert "http://success" in response.headers["location"] or "http://failure" in response.headers["location"]

def test_pse_callback_success():
    # Setup a pending transaction
    order_id = test_create_pse_payment_success()
    
    # Process callback
    payload = {
        "internal_order_id": order_id,
        "status": "SUCCESS",
        "provider_tx_id": "pse-12345",
        "provider_reference": "ref-001"
    }
    response = client.post("/callback", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Callback procesado correctamente"
    
def test_pse_callback_not_found():
    payload = {
        "internal_order_id": "non_existent_order",
        "status": "SUCCESS"
    }
    response = client.post("/callback", json=payload)
    assert response.status_code == 404

def test_get_pse_payment_success():
    headers = get_auth_headers()
    order_id = test_create_pse_payment_success()
    response = client.get(f"/payments/{order_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["internal_order_id"] == order_id

def test_get_pse_payment_not_found():
    headers = get_auth_headers()
    response = client.get(f"/payments/MISSING-ORDER-ID", headers=headers)
    assert response.status_code == 404

def test_create_pse_payment_account_not_found():
    headers = get_auth_headers()
    payload = {
        "customer_id": 100,
        "account_id": 999,
        "amount": 10.0,
    }
    response = client.post("/payments", json=payload, headers=headers)
    assert response.status_code == 404
    assert "Cuenta de origen no encontrada" in response.json()["detail"]

def test_pse_gateway_not_found():
    response = client.get("/pse-gateway/MISSING_ORDER_ID", follow_redirects=False)
    assert response.status_code == 404

def test_pse_gateway_expired():
    # Setup a pending transaction
    order_id = test_create_pse_payment_success()
    db = TestingSessionLocal()
    from datetime import datetime, timedelta
    tx = db.query(PSETransactionDB).filter(PSETransactionDB.internal_order_id == order_id).first()
    # expire the tx manually
    tx.expires_at = datetime.utcnow() - timedelta(minutes=30)
    db.commit()
    db.close()
    
    response = client.get(f"/pse-gateway/{order_id}", follow_redirects=False)
    # the code redirects to return_url_failure
    assert response.status_code in [302, 303, 307]
    assert "http://failure" in response.headers["location"]

def test_pse_gateway_account_not_found():
    order_id = test_create_pse_payment_success()
    db = TestingSessionLocal()
    tx = db.query(PSETransactionDB).filter(PSETransactionDB.internal_order_id == order_id).first()
    # change account_id to non-existing
    tx.account_id = 9999
    db.commit()
    db.close()
    
    response = client.get(f"/pse-gateway/{order_id}", follow_redirects=False)
    assert response.status_code == 404
    assert "Cuenta de origen" in response.json()["detail"]

def test_pse_callback_success_account_not_found():
    order_id = test_create_pse_payment_success()
    db = TestingSessionLocal()
    tx = db.query(PSETransactionDB).filter(PSETransactionDB.internal_order_id == order_id).first()
    tx.account_id = 9999
    db.commit()
    db.close()

    payload = {
        "internal_order_id": order_id,
        "status": "SUCCESS",
    }
    response = client.post("/callback", json=payload)
    assert response.status_code == 400
    assert "Cuenta asociada no existe" in response.json()["detail"]

def test_pse_gateway_insufficient_funds_on_approve():
    order_id = test_create_pse_payment_success()
    db = TestingSessionLocal()
    # Drain the account completely
    account = db.query(AccountDB).filter(AccountDB.id == 1).first()
    account.balance = 0.0
    db.commit()
    db.close()
    
    # gateway attempts to pull $300 but there's only $0 -> reject
    response = client.get(f"/pse-gateway/{order_id}", follow_redirects=False)
    # The code redirects to return_url_failure when account.balance < tx.amount
    assert response.status_code in [302, 303, 307]
    assert "http://failure" in response.headers["location"]

