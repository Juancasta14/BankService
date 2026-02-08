from sqlalchemy.orm import Session
from application.auth.ports.user_repository import UserRepository
from domain.auth.user import User
from adapters.outbound.persistence.sqlalchemy.models import UserDB

class UserRepositorySqlAlchemy(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str):
        row = self.db.query(UserDB).filter(UserDB.username == username).first()
        if not row:
            return None
        return User(id=row.id, username=row.username, hashed_password=row.hashed_password)

    def get_by_id(self, user_id: int):
        row = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not row:
            return None
        return User(id=row.id, username=row.username, hashed_password=row.hashed_password)
