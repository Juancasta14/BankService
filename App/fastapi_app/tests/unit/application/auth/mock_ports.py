from typing import Optional
from domain.auth.user import User
from application.auth.ports.user_repository import UserRepository
from application.auth.ports.password_hasher import PasswordHasher
from application.auth.ports.token_service import TokenService
from application.auth.ports.login_notifier import LoginNotifier


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users = {}

    def add_user(self, user: User):
        self.users[user.username] = user

    def get_by_username(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def get_by_id(self, user_id: int) -> Optional[User]:
        for u in self.users.values():
            if u.id == user_id:
                return u
        return None


class MockPasswordHasher(PasswordHasher):
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        # For our mock, we just check if it matches the text "hashed_" + plain_password
        return hashed_password == f"hashed_{plain_password}"


class MockTokenService(TokenService):
    def create_access_token(self, subject: str) -> str:
        return f"fake_token_for_{subject}"


class MockLoginNotifier(LoginNotifier):
    def __init__(self):
        self.notifications = []

    def notify_login(
        self,
        user_id: Optional[int],
        username: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        success: bool,
    ) -> None:
        self.notifications.append(
            {"user_id": user_id, "username": username, "success": success}
        )
