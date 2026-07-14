from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.recurring import RecurringTransaction, RecurringTransactionCreate
from app.services.auth import get_current_user
from app.repositories.recurring import recurring_repository

router = APIRouter()

@router.post("/", response_model=RecurringTransaction, status_code=status.HTTP_201_CREATED)
def create_recurring(
    recurring_in: RecurringTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recurring_data = recurring_in.model_dump()
    recurring_data["user_id"] = current_user.id
    recurring_data["is_active"] = True
    return recurring_repository.create(db, obj_in=recurring_data)

@router.get("/", response_model=list[RecurringTransaction])
def read_recurrings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return recurring_repository.get_by_user(db, user_id=current_user.id)

@router.delete("/{recurring_id}", response_model=RecurringTransaction)
def delete_recurring(
    recurring_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = recurring_repository.get(db, id=recurring_id)
    if not rec or rec.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch định kỳ này")
    
    return recurring_repository.remove(db, id=recurring_id)
