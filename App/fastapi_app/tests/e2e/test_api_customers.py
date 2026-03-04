import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LOGIN_EVENTS_URL"] = "http://mock"
os.environ["LOGIN_EVENTS_SECRET"] = "mock"

import pytest
from fastapi.testclient import TestClient
from main import app
from adapters.inbound.http.dependencies import get_current_user
from adapters.outbound.persistence.sqlalchemy.models import UserDB

# Mock objects to return from services
class MockGetAccountsService:
    def execute(self, customer_id):
        if customer_id == 1:
            return [{"id": 10, "customer_id": 1, "type": "ahorros", "balance": 1000.0}]
        return []

class MockGetWalletService:
    def execute(self, customer_id):
        if customer_id == 1:
            return {"id": 1, "customer_id": 1, "balance": 500.0}
        return None

class MockGetMovementsService:
    def execute(self, customer_id, account_type=None, date_from=None, date_to=None):
        if customer_id == 1:
            return [
                {"id": 1, "account_id": 10, "customer_id": 1, "account_type": "ahorros", "date": "2026-01-01", "description": "Deposito", "amount": 1000.0, "type": "credit"}
            ]
        return []

class MockGetSummaryService:
    def execute(self, customer_id):
        if customer_id == 1:
            accounts = [{"id": 10, "customer_id": 1, "type": "ahorros", "balance": 1000.0}]
            wallet = {"id": 1, "customer_id": 1, "balance": 500.0}
            return accounts, wallet, 1500.0
        return None

def override_get_current_user():
    user = UserDB()
    user.id = 1
    user.username = "mockuser"
    return user

# Here we use pytest monkeypatching instead of FastAPI overrides for build_services
# since build_services is a normal python function, not a Depends()

# We still need to override the dependency get_current_user to bypass token verification
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_customer_services(monkeypatch):
    def fake_build_services(db):
        return {
            "accounts": MockGetAccountsService(),
            "wallet": MockGetWalletService(),
            "movements": MockGetMovementsService(),
            "summary": MockGetSummaryService(),
        }
    monkeypatch.setattr("adapters.inbound.http.routes.customers.build_services", fake_build_services)


def test_api_get_accounts():
    response = client.get("/customers/1/accounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["balance"] == 1000.0

def test_api_get_accounts_empty():
    response = client.get("/customers/99/accounts")
    assert response.status_code == 200
    assert response.json() == []

def test_api_get_wallet():
    response = client.get("/customers/1/wallet")
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 500.0

def test_api_get_wallet_not_found():
    response = client.get("/customers/99/wallet")
    assert response.status_code == 200
    assert response.json() is None

def test_api_get_summary():
    response = client.get("/customers/1/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_balance"] == 1500.0
    assert len(data["accounts"]) == 1

def test_api_get_summary_not_found():
    response = client.get("/customers/99/summary")
    assert response.status_code == 404
    assert response.json()["detail"] == "Cliente sin productos"

def test_api_get_movements():
    response = client.get("/customers/1/movements")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Deposito"
