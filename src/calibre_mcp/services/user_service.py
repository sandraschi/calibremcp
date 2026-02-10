from ..db.user_data import get_user_data_db
from ..db.repositories.user_repository import UserRepository
from .base_service import BaseService


class UserService(BaseService):
    def __init__(self):
        super().__init__()
        self.db = get_user_data_db()

    async def get_user_by_id(self, user_id: str) -> dict | None:
        with self.db.session_scope() as session:
            repo = UserRepository(session)
            user = repo.get_by_id(user_id)
            return self._to_dict(user) if user else None

    async def get_user_by_username(self, username: str) -> dict | None:
        with self.db.session_scope() as session:
            repo = UserRepository(session)
            user = repo.get_by_username(username)
            return self._to_dict(user) if user else None

    async def list_users(self) -> list[dict]:
        with self.db.session_scope() as session:
            repo = UserRepository(session)
            users = repo.list_all()
            return [self._to_dict(u) for u in users]

    async def create_user(
        self, user_id: str, username: str, email: str = None, role: str = "user"
    ) -> dict:
        with self.db.session_scope() as session:
            repo = UserRepository(session)
            user = repo.create(user_id, username, email, role)
            return self._to_dict(user)

    async def delete_user(self, user_id: str) -> bool:
        with self.db.session_scope() as session:
            repo = UserRepository(session)
            return repo.delete(user_id)

    def _to_dict(self, user) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
