from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Literal

class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    type: Literal['income', 'expense']
    category: str = Field(..., min_length=1, max_length=100)
    currency: str = Field(default="VND", min_length=3, max_length=5)
    exchange_rate: Decimal = Field(default=1.0, gt=0)
    description: str | None = Field(default=None, max_length=500)
    date: datetime | None = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    type: Literal['income', 'expense'] | None = None
    category: str | None = Field(default=None, min_length=1, max_length=100)
    currency: str | None = Field(default=None, min_length=3, max_length=5)
    exchange_rate: Decimal | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=500)
    date: datetime | None = None

class TransactionInDBBase(TransactionBase):
    id: int
    user_id: int
    amount_base: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Transaction(TransactionInDBBase):
    pass

class CategoryStat(BaseModel):
    category: str
    total: Decimal
    percentage: float

class FinancialSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    category_expenses: list[CategoryStat]
    category_incomes: list[CategoryStat]
