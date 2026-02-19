from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.respondent import Respondent
from app.schemas.respondent import RespondentCreate, RespondentUpdate


class RespondentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: RespondentCreate) -> Respondent:
        respondent = Respondent(**data.model_dump())
        self.db.add(respondent)
        await self.db.flush()
        await self.db.refresh(respondent)
        return respondent

    async def get_by_id(self, respondent_id: int) -> Optional[Respondent]:
        result = await self.db.execute(
            select(Respondent).where(Respondent.id == respondent_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Respondent]:
        result = await self.db.execute(
            select(Respondent).where(Respondent.email == email)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        state: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        household_income: Optional[str] = None,
        gender: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> Tuple[List[Respondent], int]:
        query = select(Respondent)
        count_query = select(func.count(Respondent.id))

        # Apply filters
        if is_active is not None:
            query = query.where(Respondent.is_active == is_active)
            count_query = count_query.where(Respondent.is_active == is_active)

        if state:
            query = query.where(Respondent.state == state)
            count_query = count_query.where(Respondent.state == state)

        if age_min is not None:
            query = query.where(Respondent.age >= age_min)
            count_query = count_query.where(Respondent.age >= age_min)

        if age_max is not None:
            query = query.where(Respondent.age <= age_max)
            count_query = count_query.where(Respondent.age <= age_max)

        if household_income:
            query = query.where(Respondent.household_income == household_income)
            count_query = count_query.where(Respondent.household_income == household_income)

        if gender:
            query = query.where(Respondent.gender == gender)
            count_query = count_query.where(Respondent.gender == gender)

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.order_by(Respondent.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        respondents = list(result.scalars().all())

        return respondents, total

    async def update(self, respondent: Respondent, data: RespondentUpdate) -> Respondent:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(respondent, field, value)
        await self.db.flush()
        await self.db.refresh(respondent)
        return respondent

    async def soft_delete(self, respondent: Respondent) -> Respondent:
        respondent.is_active = False
        await self.db.flush()
        await self.db.refresh(respondent)
        return respondent
