# EVOLUCION.md — Evolución del Proyecto: Añadir Notificaciones AWS Lambda al Login

> **Funcionalidad agregada:** Cuando un usuario inicia sesión (exitosamente o no), el sistema envía un evento `USER_LOGIN` a un endpoint HTTP de **AWS Lambda** con metadatos del intento (IP, User-Agent, éxito/fallo).

---

## 🎯 Objetivo de este documento

Demostrar, con **código real del repositorio**, que al agregar esta funcionalidad:

1. ✅ El **Dominio** (`domain/`) → **NO se tocó**
2. ✅ Los **Casos de Uso** (`application/services/`) → **NO se tocaron en su lógica**
3. ✅ El **Puerto** (`application/ports/`) → **Solo se definió el contrato** (una interfaz)
4. 🆕 Solo se **creó** el adaptador de infraestructura (`adapters/outbound/notifications/`)
5. 🔧 Solo se **configuró** el wiring en el punto de entrada (`adapters/inbound/http/routes/auth_routes.py`)

---

## 📁 Archivos involucrados

```
domain/auth/
  user.py                              ❌ NO MODIFICADO
  exceptions.py                        ❌ NO MODIFICADO

application/auth/
  ports/
    login_notifier.py                  🆕 NUEVO (solo el contrato/interfaz)
  services/
    login_service.py                   🔧 MODIFICADO MÍNIMAMENTE
                                          (agregó notifier como dependencia)

adapters/outbound/notifications/
  http_api_login_notifier.py           🆕 NUEVO (implementación real Lambda)

adapters/inbound/http/routes/
  auth_routes.py                       🔧 MODIFICADO (wiring del notificador)
```

---

## 1. ❌ Domain — NO SE MODIFICÓ

### `domain/auth/user.py`

```python
# SIN CAMBIOS — exactamente igual que antes de agregar la funcionalidad
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    id: int
    username: str
    hashed_password: str
```

> **Por qué:** La entidad `User` solo modela la identidad del usuario. No tiene responsabilidad de notificar eventos. Esta clase **jamás cambió** porque el dominio es independiente de si existe Lambda, email, SMS o cualquier otro canal.

### `domain/auth/exceptions.py`

```python
# SIN CAMBIOS — exactamente igual que antes de agregar la funcionalidad
class AuthError(Exception): ...
class InvalidCredentials(AuthError): ...
class Unauthorized(AuthError): ...
class UserNotFound(AuthError): ...
```

> **Por qué:** Las excepciones de negocio describen QUÉ salió mal desde el punto de vista del dominio. No saben nada de canales de notificación externos.

---

## 2. 🆕 Puerto — SOLO SE CREÓ EL CONTRATO

### `application/auth/ports/login_notifier.py` ← **ARCHIVO NUEVO**

```python
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
```

> **Qué es:** Un `Protocol` de Python — equivalente a una interfaz abstracta. NO contiene lógica. Solo declara: *"cualquiera que quiera ser un LoginNotifier debe tener este método"*.
>
> **Por qué funciona así:** El caso de uso (`LoginService`) depende de **este contrato**, no de la implementación real. Esto permite que en tests se use un `Mock` en RAM, y en producción se use la llamada a Lambda — **sin cambiar una sola línea del caso de uso**.

---

## 3. 🔧 Caso de Uso — SOLO RECIBIÓ UNA DEPENDENCIA NUEVA

### `application/auth/services/login_service.py` ← **MODIFICACIÓN MÍNIMA**

El `LoginService` existía antes para manejar login. Lo único que cambió fue:
- Se añadió `notifier: LoginNotifier` como campo del dataclass (inyección de dependencia).
- Se añadió la llamada `self._safe_notify(...)` en los tres puntos del flujo.
- La **lógica de negocio no cambió**: sigue verificando usuario, contraseña, y generando token.

```python
from dataclasses import dataclass

from domain.auth.exceptions import InvalidCredentials
from application.auth.ports.user_repository import UserRepository
from application.auth.ports.password_hasher import PasswordHasher
from application.auth.ports.token_service import TokenService
from application.auth.ports.login_notifier import LoginNotifier   # ← NUEVA IMPORTACIÓN


@dataclass
class LoginService:
    users: UserRepository
    hasher: PasswordHasher
    tokens: TokenService
    notifier: LoginNotifier   # ← NUEVA DEPENDENCIA INYECTADA

    def login(self, username: str, password: str, *, ip=None, user_agent=None) -> dict:
        user = self.users.get_by_username(username)
        if user is None:
            self._safe_notify(user_id=None, username=username,   # ← NUEVA LLAMADA
                              ip=ip, user_agent=user_agent, success=False)
            raise InvalidCredentials("Usuario o contraseña incorrectos")

        if not self.hasher.verify(password, user.hashed_password):
            self._safe_notify(user_id=user.id, username=user.username,  # ← NUEVA LLAMADA
                              ip=ip, user_agent=user_agent, success=False)
            raise InvalidCredentials("Usuario o contraseña incorrectos")

        access_token = self.tokens.create_access_token(subject=user.username)

        self._safe_notify(user_id=user.id, username=user.username,  # ← NUEVA LLAMADA
                          ip=ip, user_agent=user_agent, success=True)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username,
            "user_id": user.id,
        }

    def _safe_notify(self, *, user_id, username, ip, user_agent, success) -> None:
        # ← MÉTODO NUEVO: llama al notificador de forma silenciosa
        # Si Lambda falla, el login NO se interrumpe
        try:
            self.notifier.notify_login(
                user_id=user_id, username=username,
                ip_address=ip, user_agent=user_agent, success=success,
            )
        except Exception as e:
            print("NOTIFY: failed", repr(e))   # log, no excepción
```

> **Prueba de que la lógica NO cambió:** Las 3 llamadas a `_safe_notify` son **efectos secundarios opcionales** envueltos en `try/except`. Si el notificador explota, el usuario igual recibe su token o su error de credenciales. La regla de negocio es idéntica.

---

## 4. 🆕 Adaptador — TODO EL CÓDIGO NUEVO DE INFRAESTRUCTURA AQUÍ

### `adapters/outbound/notifications/http_api_login_notifier.py` ← **ARCHIVO NUEVO**

```python
import json, hmac, hashlib, uuid, os
from datetime import datetime, timezone
from typing import Optional
import requests


class HttpApiLoginNotifier:
    """Implementa LoginNotifier enviando eventos firmados a un endpoint HTTP (AWS Lambda URL)."""

    def __init__(self, endpoint_url, service_name, environment,
                 shared_secret, timeout_seconds=2.5, module="auth", session=None):
        self.endpoint_url = endpoint_url
        self.service_name = service_name
        self.environment = environment
        self.shared_secret = shared_secret
        self.timeout_seconds = timeout_seconds
        self.module = module
        self.session = session or requests.Session()

    def notify_login(self, *, user_id, username, success,
                     auth_method="password", ip_address=None, user_agent=None, event_id=None):
        """POSTea un evento USER_LOGIN firmado con HMAC-SHA256 a la Lambda URL."""

        payload = {
            "event_id":      event_id or str(uuid.uuid4()),
            "event_type":    "USER_LOGIN",
            "event_version": "1.0",
            "occurred_at":   datetime.now(timezone.utc).isoformat(),
            "actor": {
                "user_id":  str(user_id) if user_id else "unknown",
                "username": username,
            },
            "context": {
                "success":     bool(success),
                "auth_method": auth_method,
                "ip_address":  ip_address,
                "user_agent":  user_agent,
            },
            "source": {
                "service":     self.service_name,
                "module":      self.module,
                "environment": self.environment,
            },
        }

        # JSON canónico → firma HMAC-SHA256
        raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        signature = hmac.new(
            self.shared_secret.encode("utf-8"), raw, hashlib.sha256
        ).hexdigest()

        resp = self.session.post(
            self.endpoint_url,
            data=raw,
            headers={"Content-Type": "application/json", "X-Signature": signature},
            timeout=self.timeout_seconds,
        )

        if resp.status_code >= 400:
            raise RuntimeError(f"Login event notify failed: {resp.status_code} {resp.text}")
```

> **Este es el único lugar donde existe `requests`, `hmac`, `hashlib` y la URL de Lambda.**
> El dominio y los casos de uso **nunca saben que este archivo existe**.

---

## 5. 🔧 Wiring — Solo el punto de ensamblaje se actualizó

### `adapters/inbound/http/routes/auth_routes.py` ← **MODIFICACIÓN DE WIRING**

```python
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from adapters.outbound.persistence.sqlalchemy.database import get_db
from adapters.outbound.persistence.sqlalchemy.user_repository_sqlalchemy import UserRepositorySqlAlchemy
from adapters.outbound.security.jwt_token_service import JwtTokenService
from adapters.outbound.security.bcrypt_password_hasher import BcryptPasswordHasher
from adapters.outbound.notifications.http_api_login_notifier import HttpApiLoginNotifier  # ← NUEVA IMPORTACIÓN

from application.auth.services.login_service import LoginService
from domain.auth.exceptions import InvalidCredentials

router = APIRouter(prefix="/auth", tags=["auth"])


def get_login_service(db: Session = Depends(get_db)) -> LoginService:
    notifier = HttpApiLoginNotifier(            # ← SE CONSTRUYE EL ADAPTADOR
        endpoint_url=os.environ["LOGIN_EVENTS_URL"],
        service_name=os.environ.get("SERVICE_NAME", "bankservice"),
        environment=os.environ.get("ENVIRONMENT", "dev"),
        shared_secret=os.environ["LOGIN_EVENTS_SECRET"],
        timeout_seconds=float(os.environ.get("LOGIN_EVENTS_TIMEOUT", "2.5")),
    )

    return LoginService(
        users=UserRepositorySqlAlchemy(db),
        hasher=BcryptPasswordHasher(),
        tokens=JwtTokenService(),
        notifier=notifier,                      # ← SE INYECTA EN EL CASO DE USO
    )


@router.post("/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
          svc: LoginService = Depends(get_login_service)):
    try:
        ip = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip() or \
             (request.client.host if request.client else None)
        user_agent = request.headers.get("user-agent")
        return svc.login(form_data.username, form_data.password, ip=ip, user_agent=user_agent)
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

> **Punto clave:** Este archivo es el **único lugar en toda la aplicación** que sabe que existe Lambda. Construye el `HttpApiLoginNotifier`, lo inyecta en `LoginService`, y listo. El router de HTTP no procesa la notificación — solo la ensambla.

---

## 📊 Resumen de qué cambió y qué no

| Archivo | Estado | Detalle |
|---|---|---|
| `domain/auth/user.py` | ❌ **Sin cambios** | La entidad User no sabe que existe Lambda |
| `domain/auth/exceptions.py` | ❌ **Sin cambios** | Las excepciones de negocio no varían |
| `application/auth/services/login_service.py` | 🔧 **Modificado mínimamente** | Solo se añadió `notifier` como dependencia inyectable y `_safe_notify()` |
| `application/auth/ports/login_notifier.py` | 🆕 **Nuevo** | Solo el contrato (interfaz `Protocol`) — sin lógica |
| `adapters/outbound/notifications/http_api_login_notifier.py` | 🆕 **Nuevo** | Toda la lógica de HTTP, HMAC, JSON y Lambda aquí |
| `adapters/inbound/http/routes/auth_routes.py` | 🔧 **Modificado** | Solo wiring: construir el adaptador e inyectarlo |
| `domain/banking/`, `application/pse/`, `application/customers/` | ❌ **Sin cambios** | Nada fuera de `auth/` fue tocado |

---

## 🔄 Flujo completo de la notificación

```
POST /auth/login
      │
      ▼
auth_routes.py                  ← Adaptador Inbound (construye el servicio)
  │ get_login_service()
  │   └─ construye HttpApiLoginNotifier(endpoint_url, secret, ...)
  │   └─ construye LoginService(users, hasher, tokens, notifier=↑)
  │
  ▼
LoginService.login()            ← Caso de Uso (NO sabe de Lambda)
  │ verifica usuario y contraseña
  │ genera token JWT
  │ llama self._safe_notify(success=True/False)
  │
  ▼
LoginNotifier.notify_login()    ← Puerto (solo la firma del método)
  │
  ▼ (en producción)
HttpApiLoginNotifier.notify_login()  ← Adaptador Outbound (TODA la lógica HTTP)
  │ construye payload JSON
  │ firma con HMAC-SHA256
  │ POST → https://lambda-url.aws/
  │
  ▼
AWS Lambda recibe el evento
```

---

## ✅ Conclusión: La Arquitectura Hexagonal cumplió su promesa

> La única regla que impuso la arquitectura fue:
> **"Si quieres añadir infraestructura nueva, crea un adaptador. El núcleo no se toca."**

Y eso es exactamente lo que ocurrió:
- Se necesitaban **0 cambios** en `domain/`.
- Se necesitaban **0 cambios en la lógica** de `application/` — solo se registró una nueva dependencia.
- Toda la complejidad de HTTP, firma HMAC, JSON canónico y timeouts vive **aislada** en `adapters/outbound/notifications/`.
- Si mañana se cambia Lambda por SNS de AWS o un webhook de Slack, **solo se crea un nuevo adaptador** y se cambia una línea del wiring en `auth_routes.py`.
