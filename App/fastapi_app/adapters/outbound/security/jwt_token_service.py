from application.auth.ports.token_service import TokenService
from security import create_access_token, decode_token  

class JwtTokenService(TokenService):
    def create_access_token(self, subject: str) -> str:
        return create_access_token(data={"sub": subject})

    def decode_subject(self, token: str):
        payload = decode_token(token)
        if payload is None:
            return None
        return payload.get("sub")
