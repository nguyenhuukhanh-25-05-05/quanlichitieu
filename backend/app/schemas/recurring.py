from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Literal

class RecurringTransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    type: Literal['income', 'expense']
    category: str = Field(..., min_length=1, max_length=100)
    currency: str = Field(default="VND", min_length=3, max_length=5)
    description: str | None = Field(default=None, max_length=500)
    frequency: Literal['daily', 'weekly', 'monthly']
    next_run_date: datetime

class RecurringTransactionCreate(RecurringTransactionBase):
    pass

class RecurringTransactionUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    description: str | None = Field(default=None, max_length=500)
    frequency: Literal['daily', 'weekly', 'monthly'] | None = None
    next_run_date: datetime | None = None
    is_active: bool | None = None

class RecurringTransactionInDBBase(RecurringTransactionBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RecurringTransaction(RecurringTransactionInDBBase):
    pass
