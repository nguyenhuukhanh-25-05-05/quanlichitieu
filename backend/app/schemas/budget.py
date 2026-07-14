from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Literal

class BudgetBase(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    amount_limit: Decimal = Field(..., gt=0, decimal_places=2)
    period: Literal['daily', 'weekly', 'monthly', 'yearly'] = "monthly"
    start_date: datetime
    end_date: datetime

    @classmethod
    def validate_dates(cls, values):
        if values.get('start_date') and values.get('end_date'):
            if values['start_date'] >= values['end_date']:
                raise ValueError('start_date must be before end_date')
        return values

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    amount_limit: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    current_spend: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    start_date: datetime | None = None
    end_date: datetime | None = None

class BudgetInDBBase(BudgetBase):
    id: int
    user_id: int
    current_spend: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Budget(BudgetInDBBase):
    pass

class BudgetStatus(BaseModel):
    budget: Budget
    percent_used: float
    is_exceeded: bool
