from typing import Protocol

class PasswordHasher(Protocol):
    def verify(self, plain_password: str, hashed_password: str) -> bool: ...
