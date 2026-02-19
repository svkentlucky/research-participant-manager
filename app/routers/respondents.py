from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.respondent import (
    RespondentCreate,
    RespondentUpdate,
    RespondentResponse,
    RespondentListResponse,
)
from app.services.respondent_service import RespondentService

router = APIRouter()


@router.post("", response_model=RespondentResponse, status_code=201)
async def create_respondent(
    data: RespondentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new respondent."""
    service = RespondentService(db)

    # Check for duplicate email
    existing = await service.get_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    respondent = await service.create(data)
    return respondent


@router.get("", response_model=RespondentListResponse)
async def list_respondents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    state: Optional[str] = None,
    age_min: Optional[int] = Query(None, ge=18),
    age_max: Optional[int] = Query(None, le=120),
    household_income: Optional[str] = None,
    gender: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
):
    """List respondents with optional filters and pagination."""
    service = RespondentService(db)
    respondents, total = await service.list(
        limit=limit,
        offset=offset,
        state=state,
        age_min=age_min,
        age_max=age_max,
        household_income=household_income,
        gender=gender,
        is_active=is_active,
    )
    return RespondentListResponse(
        items=respondents,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{respondent_id}", response_model=RespondentResponse)
async def get_respondent(
    respondent_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single respondent by ID."""
    service = RespondentService(db)
    respondent = await service.get_by_id(respondent_id)
    if not respondent:
        raise HTTPException(status_code=404, detail="Respondent not found")
    return respondent


@router.put("/{respondent_id}", response_model=RespondentResponse)
async def update_respondent(
    respondent_id: int,
    data: RespondentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a respondent."""
    service = RespondentService(db)
    respondent = await service.get_by_id(respondent_id)
    if not respondent:
        raise HTTPException(status_code=404, detail="Respondent not found")

    # Check email uniqueness if changing email
    if data.email and data.email != respondent.email:
        existing = await service.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    updated = await service.update(respondent, data)
    return updated


@router.delete("/{respondent_id}", response_model=RespondentResponse)
async def delete_respondent(
    respondent_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a respondent (set is_active=false)."""
    service = RespondentService(db)
    respondent = await service.get_by_id(respondent_id)
    if not respondent:
        raise HTTPException(status_code=404, detail="Respondent not found")

    deleted = await service.soft_delete(respondent)
    return deleted
