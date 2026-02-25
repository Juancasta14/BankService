from typing import Protocol

class LoginNotifier(Protocol):
    def notify_login(
        self,
        *,
        user_id: int | None,
        username: str,
        success: bool,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> None: ...