from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.recurring import RecurringTransaction
from datetime import datetime

class RecurringTransactionRepository(BaseRepository[RecurringTransaction]):
    def get_by_user(self, db: Session, *, user_id: int) -> list[RecurringTransaction]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

    def get_active_due(self, db: Session) -> list[RecurringTransaction]:
        now = datetime.now()
        return (
            db.query(self.model)
            .filter(
                self.model.is_active == True,
                self.model.next_run_date <= now
            )
            .all()
        )

recurring_repository = RecurringTransactionRepository(RecurringTransaction)
