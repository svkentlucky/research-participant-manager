from typing import List, Tuple, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.respondent import Respondent
from app.models.study import Study
from app.models.screener_criteria import ScreenerCriteria
from app.models.study_assignment import StudyAssignment


class MatchingService:
    """Service for matching respondents to study criteria."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_matching_respondents(
        self,
        study_id: int,
        exclude_assigned: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Respondent], int]:
        """
        Find respondents matching all screener criteria for a study.

        Args:
            study_id: The study to match against
            exclude_assigned: If True, exclude respondents already assigned to this study
            limit: Max results to return
            offset: Pagination offset

        Returns:
            Tuple of (matching respondents, total count)
        """
        # Get study criteria
        criteria_result = await self.db.execute(
            select(ScreenerCriteria).where(ScreenerCriteria.study_id == study_id)
        )
        criteria_list = list(criteria_result.scalars().all())

        # Build base query for active respondents
        query = select(Respondent).where(Respondent.is_active == True)

        # Exclude already assigned respondents if requested
        if exclude_assigned:
            assigned_subquery = (
                select(StudyAssignment.respondent_id)
                .where(StudyAssignment.study_id == study_id)
            )
            query = query.where(Respondent.id.not_in(assigned_subquery))

        # Apply each criterion
        for criterion in criteria_list:
            condition = self._build_condition(criterion)
            if condition is not None:
                query = query.where(condition)

        # Get total count (before pagination)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.order_by(Respondent.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        respondents = list(result.scalars().all())

        return respondents, total

    def _build_condition(self, criterion: ScreenerCriteria):
        """Build a SQLAlchemy condition from a screener criterion."""
        field_name = criterion.field_name
        operator = criterion.operator
        value = criterion.value

        # Get the column from the Respondent model
        if not hasattr(Respondent, field_name):
            return None

        column = getattr(Respondent, field_name)

        # Handle different operators
        if operator == "eq":
            return column == value

        elif operator == "neq":
            return column != value

        elif operator == "gte":
            return column >= value

        elif operator == "lte":
            return column <= value

        elif operator == "in":
            if isinstance(value, list):
                return column.in_(value)
            return column == value

        elif operator == "between":
            if isinstance(value, list) and len(value) == 2:
                return and_(column >= value[0], column <= value[1])
            return None

        return None

    async def check_respondent_matches(
        self,
        respondent_id: int,
        study_id: int,
    ) -> bool:
        """Check if a specific respondent matches a study's criteria."""
        # Get the respondent
        respondent_result = await self.db.execute(
            select(Respondent).where(
                Respondent.id == respondent_id,
                Respondent.is_active == True,
            )
        )
        respondent = respondent_result.scalar_one_or_none()
        if not respondent:
            return False

        # Get study criteria
        criteria_result = await self.db.execute(
            select(ScreenerCriteria).where(ScreenerCriteria.study_id == study_id)
        )
        criteria_list = list(criteria_result.scalars().all())

        # Check each criterion
        for criterion in criteria_list:
            if not self._respondent_matches_criterion(respondent, criterion):
                return False

        return True

    def _respondent_matches_criterion(
        self,
        respondent: Respondent,
        criterion: ScreenerCriteria,
    ) -> bool:
        """Check if a respondent matches a single criterion."""
        field_name = criterion.field_name
        operator = criterion.operator
        value = criterion.value

        if not hasattr(respondent, field_name):
            return False

        respondent_value = getattr(respondent, field_name)
        if respondent_value is None:
            return False

        if operator == "eq":
            return respondent_value == value

        elif operator == "neq":
            return respondent_value != value

        elif operator == "gte":
            return respondent_value >= value

        elif operator == "lte":
            return respondent_value <= value

        elif operator == "in":
            if isinstance(value, list):
                return respondent_value in value
            return respondent_value == value

        elif operator == "between":
            if isinstance(value, list) and len(value) == 2:
                return value[0] <= respondent_value <= value[1]
            return False

        return False
