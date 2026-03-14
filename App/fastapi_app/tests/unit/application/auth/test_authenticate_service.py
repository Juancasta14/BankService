import pytest
from unittest.mock import Mock
from domain.auth.exceptions import Unauthorized
from domain.auth.user import User
from application.auth.services.authenticate_service import AuthenticateService
from tests.unit.application.auth.mock_ports import InMemoryUserRepository

def test_authenticate_success():
    # Setup
    users = InMemoryUserRepository()
    user = User(id=1, username="test_user", hashed_password="hashed_password")
    users.add_user(user)

    tokens = Mock()
    tokens.decode_subject.return_value = "test_user"

    service = AuthenticateService(users=users, tokens=tokens)

    # Execute
    result = service.authenticate("valid_token")

    # Verify
    assert result == user
    tokens.decode_subject.assert_called_once_with("valid_token")

def test_authenticate_invalid_token():
    # Setup
    users = InMemoryUserRepository()
    tokens = Mock()
    tokens.decode_subject.return_value = None

    service = AuthenticateService(users=users, tokens=tokens)

    # Execute & Verify
    with pytest.raises(Unauthorized, match="Token inv\u00e1lido o expirado"):
        service.authenticate("invalid_token")
    tokens.decode_subject.assert_called_once_with("invalid_token")

def test_authenticate_user_not_found():
    # Setup
    users = InMemoryUserRepository()
    # No user added
    tokens = Mock()
    tokens.decode_subject.return_value = "unknown_user"

    service = AuthenticateService(users=users, tokens=tokens)

    # Execute & Verify
    with pytest.raises(Unauthorized, match="Usuario no encontrado"):
        service.authenticate("valid_token_unknown_user")
    tokens.decode_subject.assert_called_once_with("valid_token_unknown_user")
