import json
import hmac
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional

import requests


class HttpApiLoginNotifier:
    def __init__(
        self,
        endpoint_url: str,
        service_name: str,
        environment: str,
        shared_secret: str,
        timeout_seconds: float = 2.5,
        module: str = "auth",
        session: Optional[requests.Session] = None,
    ):
        self.endpoint_url = endpoint_url
        self.service_name = service_name
        self.environment = environment
        self.shared_secret = shared_secret
        self.timeout_seconds = timeout_seconds
        self.module = module
        self.session = session or requests.Session()

    def notify_login(
        self,
        *,
        user_id: int | None,
        username: str,
        success: bool,
        auth_method: str = "password",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> None:
        """
        Sends a signed USER_LOGIN event to an HTTP endpoint (Lambda Function URL / API Gateway).

        Signature:
          X-Signature = HMAC-SHA256 hex digest of the *raw request body bytes*
        """

        # Keep Lambda validation happy: actor.user_id must exist
        user_id_value = str(user_id) if user_id is not None else "unknown"

        payload = {
            "event_id": event_id or str(uuid.uuid4()),
            "event_type": "USER_LOGIN",
            "event_version": "1.0",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "actor": {"user_id": user_id_value, "username": username},
            "context": {
                "success": bool(success),
                "auth_method": auth_method,
                "ip_address": ip_address,
                "user_agent": user_agent,
            },
            "source": {
                "service": self.service_name,
                "module": self.module,
                "environment": self.environment,
            },
        }

        # Canonical JSON (prevents signature mismatches due to whitespace/key ordering)
        raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )

        signature = hmac.new(
            self.shared_secret.encode("utf-8"),
            raw,
            hashlib.sha256,
        ).hexdigest()

        resp = self.session.post(
            self.endpoint_url,
            data=raw,  # IMPORTANT: send the exact bytes you signed
            headers={
                "Content-Type": "application/json",
                "X-Signature": signature,
            },
            timeout=self.timeout_seconds,
        )

        if resp.status_code >= 400:
            raise RuntimeError(
                f"Login event notify failed: {resp.status_code} {resp.text}"
            )
