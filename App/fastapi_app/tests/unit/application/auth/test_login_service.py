import pytest
from domain.auth.user import User
from domain.auth.exceptions import InvalidCredentials
from application.auth.services.login_service import LoginService
from tests.unit.application.auth.mock_ports import (
    InMemoryUserRepository,
    MockPasswordHasher,
    MockTokenService,
    MockLoginNotifier
)

@pytest.fixture
def login_service():
    users = InMemoryUserRepository()
    # Pre-populate a test user
    test_user = User(id=1, username="testuser", hashed_password="hashed_mypassword")
    users.add_user(test_user)

    hasher = MockPasswordHasher()
    tokens = MockTokenService()
    notifier = MockLoginNotifier()

    service = LoginService(users=users, hasher=hasher, tokens=tokens, notifier=notifier)
    return service

def test_login_success(login_service: LoginService):
    result = login_service.login(
        username="testuser",
        password="mypassword",
        ip="127.0.0.1",
        user_agent="pytest"
    )

    assert result["username"] == "testuser"
    assert result["user_id"] == 1
    assert result["access_token"] == "fake_token_for_testuser"
    assert result["token_type"] == "bearer"

    notifier: MockLoginNotifier = login_service.notifier
    assert len(notifier.notifications) == 1
    assert notifier.notifications[0]["success"] is True
    assert notifier.notifications[0]["username"] == "testuser"

def test_login_invalid_password_raises_exception(login_service: LoginService):
    with pytest.raises(InvalidCredentials) as excinfo:
        login_service.login(username="testuser", password="wrongpassword")
    
    assert "Usuario o contraseña incorrectos" in str(excinfo.value)
    
    notifier: MockLoginNotifier = login_service.notifier
    assert len(notifier.notifications) == 1
    assert notifier.notifications[0]["success"] is False
    assert notifier.notifications[0]["username"] == "testuser"

def test_login_user_not_found_raises_exception(login_service: LoginService):
    with pytest.raises(InvalidCredentials) as excinfo:
        login_service.login(username="unknownuser", password="any")
    
    assert "Usuario o contraseña incorrectos" in str(excinfo.value)
    
    notifier: MockLoginNotifier = login_service.notifier
    assert len(notifier.notifications) == 1
    assert notifier.notifications[0]["success"] is False
    assert notifier.notifications[0]["username"] == "unknownuser"
