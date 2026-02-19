from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.study import Study


class ScreenerCriteria(Base):
    __tablename__ = "screener_criteria"

    id: Mapped[int] = mapped_column(primary_key=True)
    study_id: Mapped[int] = mapped_column(ForeignKey("studies.id", ondelete="CASCADE"), index=True)
    field_name: Mapped[str] = mapped_column(String(50))  # e.g. "age", "household_income", "state"
    operator: Mapped[str] = mapped_column(String(20))  # eq, neq, gte, lte, in, between
    value: Mapped[dict] = mapped_column(JSONB)  # Flexible: "NY", [25, 45], ["75k-100k", "100k+"]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    study: Mapped["Study"] = relationship("Study", back_populates="criteria")
