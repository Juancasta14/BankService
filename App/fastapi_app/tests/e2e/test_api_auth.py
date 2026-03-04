import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LOGIN_EVENTS_URL"] = "http://mock"
os.environ["LOGIN_EVENTS_SECRET"] = "mock"

from fastapi.testclient import TestClient

from main import app
from adapters.inbound.http.routes.auth_routes import get_login_service
from domain.auth.exceptions import InvalidCredentials

class MockLoginService:
    def login(self, username, password, ip=None, user_agent=None):
        if username == "admin" and password == "secret":
            return {
                "access_token": "mocked_token",
                "token_type": "bearer",
                "username": username,
                "user_id": 1,
            }
        raise InvalidCredentials("Usuario o contraseña incorrectos")

def override_get_login_service():
    return MockLoginService()

# Override the FastAPI dependency
app.dependency_overrides[get_login_service] = override_get_login_service

client = TestClient(app)

def test_api_login_success():
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "secret"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["access_token"] == "mocked_token"
    assert json_data["token_type"] == "bearer"

def test_api_login_failure():
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Usuario o contraseña incorrectos"}
