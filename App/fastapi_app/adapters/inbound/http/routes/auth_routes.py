from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db

from bankservice.adapters.outbound.persistence.sqlalchemy.user_repository_sqlalchemy import UserRepositorySqlAlchemy
from bankservice.adapters.outbound.security.jwt_token_service import JwtTokenService
from bankservice.adapters.outbound.security.bcrypt_password_hasher import BcryptPasswordHasher
from bankservice.application.auth.services.login_service import LoginService
from bankservice.domain.auth.exceptions import InvalidCredentials

router = APIRouter(prefix="/auth", tags=["auth"])

def get_login_service(db: Session = Depends(get_db)) -> LoginService:
    return LoginService(
        users=UserRepositorySqlAlchemy(db),
        hasher=BcryptPasswordHasher(),
        tokens=JwtTokenService(),
    )

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    svc: LoginService = Depends(get_login_service),
):
    try:
        return svc.login(form_data.username, form_data.password)
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
