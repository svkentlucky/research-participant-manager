from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.study_assignment import StudyAssignment


class Respondent(Base):
    __tablename__ = "respondents"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(2), index=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(10))
    age: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    ethnicity: Mapped[Optional[str]] = mapped_column(String(50))
    household_income: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    assignments: Mapped[List["StudyAssignment"]] = relationship(
        "StudyAssignment", back_populates="respondent"
    )

    __table_args__ = (
        Index("ix_respondents_state_age", "state", "age"),
        Index("ix_respondents_active_state", "is_active", "state"),
    )
