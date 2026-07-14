from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(self.model).filter(self.model.email == email).first()

    def update_balance(self, db: Session, *, user_id: int, amount: float) -> User | None:
        user = self.get(db, id=user_id)
        if user:
            user.balance += amount
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

user_repository = UserRepository(User)
