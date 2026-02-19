from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.study import Study
    from app.models.respondent import Respondent


class StudyAssignment(Base):
    __tablename__ = "study_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    study_id: Mapped[int] = mapped_column(ForeignKey("studies.id", ondelete="CASCADE"), index=True)
    respondent_id: Mapped[int] = mapped_column(ForeignKey("respondents.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="invited", index=True)  # invited, confirmed, completed, no_show, rejected
    invited_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    study: Mapped["Study"] = relationship("Study", back_populates="assignments")
    respondent: Mapped["Respondent"] = relationship("Respondent", back_populates="assignments")

    __table_args__ = (
        UniqueConstraint("study_id", "respondent_id", name="uq_study_respondent"),
    )
