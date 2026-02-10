from typing import Optional
from sqlalchemy.orm import Session
from ..user_data import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.username == username).first()

    def list_all(self) -> list[User]:
        return self.session.query(User).all()

    def create(self, user_id: str, username: str, email: str = None, role: str = "user") -> User:
        user = User(id=user_id, username=username, email=email, role=role)
        self.session.add(user)
        self.session.commit()
        return user

    def delete(self, user_id: str) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False
