from decimal import Decimal
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    fullname: str | None = Field(default=None, max_length=100)
    currency: str = Field(default="VND", min_length=3, max_length=5)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserUpdate(BaseModel):
    fullname: str | None = Field(default=None, max_length=100)
    currency: str | None = Field(default=None, min_length=3, max_length=5)
    balance: Decimal | None = Field(default=None, decimal_places=2)

class UserInDBBase(UserBase):
    id: int
    balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    pass
