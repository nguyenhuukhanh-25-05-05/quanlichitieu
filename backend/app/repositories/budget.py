from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.budget import Budget
from datetime import datetime

class BudgetRepository(BaseRepository[Budget]):
    def get_by_user(self, db: Session, *, user_id: int) -> list[Budget]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

    def get_by_category_active(self, db: Session, *, user_id: int, category: str) -> Budget | None:
        now = datetime.now()
        return (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.category == category,
                self.model.start_date <= now,
                self.model.end_date >= now
            )
            .first()
        )

    def recalculate_spend(self, db: Session, *, user_id: int, category: str, start_date: datetime, end_date: datetime) -> float:
        from app.models.transaction import Transaction
        from sqlalchemy import func
        
        spend = (
            db.query(func.sum(Transaction.amount_base))
            .filter(
                Transaction.user_id == user_id,
                Transaction.category == category,
                Transaction.type == "expense",
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
            .scalar()
        ) or 0.0
        return float(spend)

budget_repository = BudgetRepository(Budget)
