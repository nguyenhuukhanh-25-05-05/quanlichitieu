from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.transaction import Transaction, TransactionCreate, FinancialSummary
from app.services.auth import get_current_user
from app.services.transaction import transaction_service
from app.services.ai import ai_service
from app.repositories.transaction import transaction_repository

router = APIRouter()

@router.post("/", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await transaction_service.create_transaction(
        db, user_id=current_user.id, transaction_in=transaction_in
    )

@router.get("/", response_model=list[Transaction])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return transaction_repository.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

@router.delete("/{transaction_id}", response_model=Transaction)
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await transaction_service.delete_transaction(
        db, user_id=current_user.id, transaction_id=transaction_id
    )

@router.get("/summary", response_model=FinancialSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return transaction_service.get_financial_summary(db, user_id=current_user.id)

@router.get("/insights", response_model=list[str])
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ai_service.get_financial_insights(db, user_id=current_user.id)
