from dataclasses import dataclass
from bankservice.domain.auth.exceptions import Unauthorized
from bankservice.application.auth.ports.user_repository import UserRepository
from bankservice.application.auth.ports.token_service import TokenService

@dataclass
class AuthenticateService:
    users: UserRepository
    tokens: TokenService

    def authenticate(self, token: str):
        subject = self.tokens.decode_subject(token)
        if not subject:
            raise Unauthorized("Token inválido o expirado")

        user = self.users.get_by_username(subject)
        if user is None:
            raise Unauthorized("Usuario no encontrado")

        return user
