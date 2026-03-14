# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from database import get_db
from models import Base, UserDB, AccountDB, WalletDB
from security import hash_password

# --- Setup in-memory DB for TestClient ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
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
    response = client.get(f"/pse-gateway/{order_id}", allow_redirects=False)
    
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

