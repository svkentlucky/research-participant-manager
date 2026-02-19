from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

from app.schemas.respondent import RespondentResponse


class AssignmentBase(BaseModel):
    notes: Optional[str] = None


class AssignmentCreate(AssignmentBase):
    respondent_ids: List[int] = Field(..., min_length=1)


class AssignmentUpdate(BaseModel):
    status: Literal["invited", "confirmed", "completed", "no_show", "rejected"]
    notes: Optional[str] = None


class AssignmentResponse(BaseModel):
    id: int
    study_id: int
    respondent_id: int
    status: str
    invited_at: datetime
    confirmed_at: Optional[datetime]
    completed_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


class AssignmentDetailResponse(AssignmentResponse):
    respondent: RespondentResponse
