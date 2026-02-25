import uuid
from datetime import datetime, timezone
import requests

from application.auth.ports.login_notifier import LoginNotifier

class HttpApiLoginNotifier(LoginNotifier):
    def __init__(self, *, endpoint_url: str, service_name: str, environment: str, timeout_seconds: float = 3.0):
        self.endpoint_url = endpoint_url.rstrip("/")
        self.service_name = service_name
        self.environment = environment
        self.timeout_seconds = timeout_seconds

    def notify_login(self, *, user_id: int, username: str, ip: str | None, user_agent: str | None, success: bool = True) -> None:
        payload = {
            "event_id": f"evt_{uuid.uuid4().hex}",
            "event_type": "USER_LOGIN",
            "event_version": "1.0",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "actor": {"user_id": user_id, "username": username},
            "context": {
                "success": success,
                "auth_method": "password",
                "ip_address": ip,
                "user_agent": user_agent,
            },
            "source": {"service": self.service_name, "module": "auth", "environment": self.environment},
        }

        requests.post(self.endpoint_url, json=payload, timeout=self.timeout_seconds)