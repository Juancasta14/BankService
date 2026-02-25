from typing import Protocol

class LoginNotifier(Protocol):
    def notify_login(
        self,
        *,
        user_id: int,
        username: str,
        ip: str | None,
        user_agent: str | None,
        success: bool = True,
    ) -> None:
        ...