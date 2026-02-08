from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db

from fastapi_app.adapters.outbound.persistence.sqlalchemy.user_repository_sqlalchemy import UserRepositorySqlAlchemy
from fastapi_app.adapters.outbound.security.jwt_token_service import JwtTokenService
from fastapi_app.application.auth.services.authenticate_service import AuthenticateService
from fastapi_app.domain.auth.exceptions import Unauthorized

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    svc = AuthenticateService(
        users=UserRepositorySqlAlchemy(db),
        tokens=JwtTokenService(),
    )
    try:
        return svc.authenticate(token)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
