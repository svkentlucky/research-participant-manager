from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, Date, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.screener_criteria import ScreenerCriteria
    from app.models.study_assignment import StudyAssignment


class Study(Base):
    __tablename__ = "studies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    client_name: Mapped[str] = mapped_column(String(255), index=True)
    methodology: Mapped[str] = mapped_column(String(50))  # focus_group, idi, survey, ethnography
    target_count: Mapped[int] = mapped_column(Integer)
    incentive_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)  # draft, recruiting, in_field, completed
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    criteria: Mapped[List["ScreenerCriteria"]] = relationship(
        "ScreenerCriteria", back_populates="study", cascade="all, delete-orphan"
    )
    assignments: Mapped[List["StudyAssignment"]] = relationship(
        "StudyAssignment", back_populates="study", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_studies_status_start", "status", "start_date"),
    )
