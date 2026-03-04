from dataclasses import dataclass

from domain.auth.exceptions import InvalidCredentials
from application.auth.ports.user_repository import UserRepository
from application.auth.ports.password_hasher import PasswordHasher
from application.auth.ports.token_service import TokenService
from application.auth.ports.login_notifier import LoginNotifier


@dataclass
class LoginService:
    users: UserRepository
    hasher: PasswordHasher
    tokens: TokenService
    notifier: LoginNotifier

    def login(
        self,
        username: str,
        password: str,
        *,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        user = self.users.get_by_username(username)
        if user is None:
            self._safe_notify(
                user_id=None,
                username=username,
                ip=ip,
                user_agent=user_agent,
                success=False,
            )
            raise InvalidCredentials("Usuario o contraseña incorrectos")

        if not self.hasher.verify(password, user.hashed_password):
            self._safe_notify(
                user_id=user.id,
                username=user.username,
                ip=ip,
                user_agent=user_agent,
                success=False,
            )
            raise InvalidCredentials("Usuario o contraseña incorrectos")

        access_token = self.tokens.create_access_token(subject=user.username)

        self._safe_notify(
            user_id=user.id,
            username=user.username,
            ip=ip,
            user_agent=user_agent,
            success=True,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username,
            "user_id": user.id,
        }

    def _safe_notify(
        self,
        *,
        user_id: int | None,
        username: str,
        ip: str | None,
        user_agent: str | None,
        success: bool,
    ) -> None:
        try:
            print(
                "NOTIFY: about to send",
                {
                    "user_id": user_id,
                    "username": username,
                    "success": success,
                    "ip": ip,
                },
            )
            self.notifier.notify_login(
                user_id=user_id,
                username=username,
                ip_address=ip,
                user_agent=user_agent,
                success=success,
            )
            print("NOTIFY: sent OK")
        except Exception as e:
            print("NOTIFY: failed", repr(e))
