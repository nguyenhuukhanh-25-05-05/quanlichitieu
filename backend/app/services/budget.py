from sqlalchemy.orm import Session
from app.repositories.budget import budget_repository
from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetStatus
from datetime import datetime

class BudgetService:
    def create_budget(self, db: Session, *, user_id: int, budget_in: BudgetCreate) -> Budget:
        # Calculate initial spend for the budget period
        initial_spend = budget_repository.recalculate_spend(
            db, 
            user_id=user_id, 
            category=budget_in.category, 
            start_date=budget_in.start_date, 
            end_date=budget_in.end_date
        )

        budget_data = budget_in.model_dump()
        budget_data["user_id"] = user_id
        budget_data["current_spend"] = initial_spend

        return budget_repository.create(db, obj_in=budget_data)

    def get_budget_statuses(self, db: Session, *, user_id: int) -> list[BudgetStatus]:
        budgets = budget_repository.get_by_user(db, user_id=user_id)
        statuses = []
        for b in budgets:
            pct = (b.current_spend / b.amount_limit * 100) if b.amount_limit > 0 else 0
            is_exceeded = b.current_spend >= b.amount_limit
            statuses.append(
                BudgetStatus(
                    budget=b,
                    percent_used=round(pct, 2),
                    is_exceeded=is_exceeded
                )
            )
        return statuses

budget_service = BudgetService()
