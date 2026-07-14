from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base import BaseRepository
from app.models.transaction import Transaction

class TransactionRepository(BaseRepository[Transaction]):
    def get_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> list[Transaction]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_totals(self, db: Session, *, user_id: int) -> tuple[float, float]:
        """Returns (total_income, total_expense) in base currency"""
        income_sum = (
            db.query(func.sum(self.model.amount_base))
            .filter(self.model.user_id == user_id, self.model.type == "income")
            .scalar()
        ) or 0.0

        expense_sum = (
            db.query(func.sum(self.model.amount_base))
            .filter(self.model.user_id == user_id, self.model.type == "expense")
            .scalar()
        ) or 0.0

        return float(income_sum), float(expense_sum)

    def get_category_sums(self, db: Session, *, user_id: int, type: str) -> list[tuple[str, float]]:
        """Returns list of (category, total_amount) for a transaction type ('income' or 'expense')"""
        results = (
            db.query(self.model.category, func.sum(self.model.amount_base))
            .filter(self.model.user_id == user_id, self.model.type == type)
            .group_by(self.model.category)
            .all()
        )
        return [(r[0], float(r[1])) for r in results if r[0] is not None]

transaction_repository = TransactionRepository(Transaction)
