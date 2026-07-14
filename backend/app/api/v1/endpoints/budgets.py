from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.budget import Budget, BudgetCreate, BudgetStatus
from app.services.auth import get_current_user
from app.services.budget import budget_service
from app.repositories.budget import budget_repository

router = APIRouter()

@router.post("/", response_model=Budget, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return budget_service.create_budget(db, user_id=current_user.id, budget_in=budget_in)

@router.get("/", response_model=list[BudgetStatus])
def read_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return budget_service.get_budget_statuses(db, user_id=current_user.id)

@router.delete("/{budget_id}", response_model=Budget)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = budget_repository.get(db, id=budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Không tìm thấy hạn mức ngân sách này")
    
    return budget_repository.remove(db, id=budget_id)
