from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.transaction import transaction_repository
from app.repositories.user import user_repository
from app.repositories.budget import budget_repository
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, FinancialSummary, CategoryStat
from app.services.websocket import socket_manager
import asyncio

class TransactionService:
    async def create_transaction(self, db: Session, *, user_id: int, transaction_in: TransactionCreate) -> Transaction:
        user = user_repository.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

        # Calculate amount in base currency
        amount_base = transaction_in.amount * transaction_in.exchange_rate

        # Prepare transaction dictionary
        tx_data = transaction_in.model_dump()
        tx_data["user_id"] = user_id
        tx_data["amount_base"] = amount_base

        # Start db write
        tx = transaction_repository.create(db, obj_in=tx_data)

        # Update User Balance
        balance_change = amount_base if tx.type == "income" else -amount_base
        user_repository.update_balance(db, user_id=user_id, amount=balance_change)

        # Handle Budget alert if it's an expense
        if tx.type == "expense":
            await self._check_and_update_budget(db, user_id=user_id, category=tx.category)

        return tx

    async def delete_transaction(self, db: Session, *, user_id: int, transaction_id: int) -> Transaction:
        tx = transaction_repository.get(db, id=transaction_id)
        if not tx or tx.user_id != user_id:
            raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")

        # Revert User Balance
        balance_change = -tx.amount_base if tx.type == "income" else tx.amount_base
        user_repository.update_balance(db, user_id=user_id, amount=balance_change)

        category = tx.category
        type = tx.type

        # Remove transaction
        transaction_repository.remove(db, id=transaction_id)

        # Update budget if it was an expense
        if type == "expense":
            await self._check_and_update_budget(db, user_id=user_id, category=category)

        return tx

    async def _check_and_update_budget(self, db: Session, user_id: int, category: str):
        # Check active budget
        budget = budget_repository.get_by_category_active(db, user_id=user_id, category=category)
        if budget:
            # Recalculate spend
            new_spend = budget_repository.recalculate_spend(
                db, 
                user_id=user_id, 
                category=category, 
                start_date=budget.start_date, 
                end_date=budget.end_date
            )
            # Update budget
            budget_repository.update(db, db_obj=budget, obj_in={"current_spend": new_spend})

            # Check threshold
            limit_float = float(budget.amount_limit)
            if new_spend >= limit_float:
                alert_msg = {
                    "type": "BUDGET_ALERT",
                    "level": "CRITICAL",
                    "category": category,
                    "limit": float(budget.amount_limit),
                    "current": new_spend,
                    "message": f"Nguy cấp! Bạn đã chi tiêu {new_spend:,.0f} / {limit_float:,.0f} VND vượt hạn mức chi tiêu cho '{category}'!"
                }
                asyncio.create_task(socket_manager.send_personal_message(alert_msg, user_id))
            elif new_spend >= limit_float * 0.8:
                alert_msg = {
                    "type": "BUDGET_ALERT",
                    "level": "WARNING",
                    "category": category,
                    "limit": float(budget.amount_limit),
                    "current": new_spend,
                    "message": f"Cảnh báo: Bạn đã chi tiêu chạm mức 80% hạn mức danh mục '{category}' ({new_spend:,.0f} / {limit_float:,.0f} VND)!"
                }
                asyncio.create_task(socket_manager.send_personal_message(alert_msg, user_id))

    def get_financial_summary(self, db: Session, *, user_id: int) -> FinancialSummary:
        user = user_repository.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

        total_income, total_expense = transaction_repository.get_user_totals(db, user_id=user_id)

        # Get category expenses and incomes
        expense_cats = transaction_repository.get_category_sums(db, user_id=user_id, type="expense")
        income_cats = transaction_repository.get_category_sums(db, user_id=user_id, type="income")

        # Convert to Pydantic CategoryStat
        expense_stats = []
        for cat, amount in expense_cats:
            pct = (amount / total_expense * 100) if total_expense > 0 else 0
            expense_stats.append(CategoryStat(category=cat, total=amount, percentage=round(pct, 2)))

        income_stats = []
        for cat, amount in income_cats:
            pct = (amount / total_income * 100) if total_income > 0 else 0
            income_stats.append(CategoryStat(category=cat, total=amount, percentage=round(pct, 2)))

        # Sort stats descending by amount
        expense_stats.sort(key=lambda x: x.total, reverse=True)
        income_stats.sort(key=lambda x: x.total, reverse=True)

        return FinancialSummary(
            total_income=total_income,
            total_expense=total_expense,
            balance=user.balance,
            category_expenses=expense_stats,
            category_incomes=income_stats
        )

transaction_service = TransactionService()
