from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Any, Literal
from pydantic import BaseModel, Field


class ScreenerCriteriaBase(BaseModel):
    field_name: str = Field(..., max_length=50)
    operator: Literal["eq", "neq", "gte", "lte", "in", "between"]
    value: Any  # Can be string, number, or list


class ScreenerCriteriaCreate(ScreenerCriteriaBase):
    pass


class ScreenerCriteriaResponse(ScreenerCriteriaBase):
    id: int
    study_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StudyBase(BaseModel):
    title: str = Field(..., max_length=255)
    client_name: str = Field(..., max_length=255)
    methodology: Literal["focus_group", "idi", "survey", "ethnography"]
    target_count: int = Field(..., ge=1)
    incentive_amount: Optional[Decimal] = Field(None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class StudyCreate(StudyBase):
    status: Literal["draft", "recruiting", "in_field", "completed"] = "draft"
    criteria: List[ScreenerCriteriaCreate] = []


class StudyUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    client_name: Optional[str] = Field(None, max_length=255)
    methodology: Optional[Literal["focus_group", "idi", "survey", "ethnography"]] = None
    target_count: Optional[int] = Field(None, ge=1)
    incentive_amount: Optional[Decimal] = Field(None, ge=0)
    status: Optional[Literal["draft", "recruiting", "in_field", "completed"]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    criteria: Optional[List[ScreenerCriteriaCreate]] = None


class StudyResponse(StudyBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AssignmentCounts(BaseModel):
    invited: int = 0
    confirmed: int = 0
    completed: int = 0
    no_show: int = 0
    rejected: int = 0
    total: int = 0


class StudyDetailResponse(StudyResponse):
    criteria: List[ScreenerCriteriaResponse] = []
    assignment_counts: AssignmentCounts = AssignmentCounts()


class StudyListResponse(BaseModel):
    items: List[StudyResponse]
    total: int
    limit: int
    offset: int
