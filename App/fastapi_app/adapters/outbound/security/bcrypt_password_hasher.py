from application.auth.ports.password_hasher import PasswordHasher
from security import verify_password

class BcryptPasswordHasher(PasswordHasher):
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)
