from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class RespondentBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    age: Optional[int] = Field(None, ge=18, le=120)
    gender: Optional[str] = Field(None, max_length=20)
    ethnicity: Optional[str] = Field(None, max_length=50)
    household_income: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)


class RespondentCreate(RespondentBase):
    pass


class RespondentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    age: Optional[int] = Field(None, ge=18, le=120)
    gender: Optional[str] = Field(None, max_length=20)
    ethnicity: Optional[str] = Field(None, max_length=50)
    household_income: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class RespondentResponse(RespondentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RespondentListResponse(BaseModel):
    items: List[RespondentResponse]
    total: int
    limit: int
    offset: int
