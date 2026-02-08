from dataclasses import dataclass
from bankservice.domain.auth.exceptions import InvalidCredentials
from bankservice.application.auth.ports.user_repository import UserRepository
from bankservice.application.auth.ports.password_hasher import PasswordHasher
from bankservice.application.auth.ports.token_service import TokenService

@dataclass
class LoginService:
    users: UserRepository
    hasher: PasswordHasher
    tokens: TokenService

    def login(self, username: str, password: str) -> dict:
        user = self.users.get_by_username(username)
        if user is None:
            raise InvalidCredentials("Usuario o contraseña incorrectos")

        if not self.hasher.verify(password, user.hashed_password):
            raise InvalidCredentials("Usuario o contraseña incorrectos")

        access_token = self.tokens.create_access_token(subject=user.username)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username,
            "user_id": user.id,
        }
