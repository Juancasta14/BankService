import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from adapters.outbound.persistence.sqlalchemy.user_repository_sqlalchemy import UserRepositorySqlAlchemy
from adapters.outbound.security.jwt_token_service import JwtTokenService
from adapters.outbound.security.bcrypt_password_hasher import BcryptPasswordHasher
from adapters.outbound.notifications.http_api_login_notifier import HttpApiLoginNotifier

from application.auth.services.login_service import LoginService
from domain.auth.exceptions import InvalidCredentials

router = APIRouter(prefix="/auth", tags=["auth"])

def get_login_service(db: Session = Depends(get_db)) -> LoginService:
    notifier = HttpApiLoginNotifier(
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
        notifier=notifier,
    )

@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    svc: LoginService = Depends(get_login_service),
):
    try:
        # IP real si estás detrás de proxy: X-Forwarded-For
        ip = request.headers.get("x-forwarded-for")
        if ip:
            ip = ip.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else None

        user_agent = request.headers.get("user-agent")

        return svc.login(
            form_data.username,
            form_data.password,
            ip=ip,
            user_agent=user_agent,
        )
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))