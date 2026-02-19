from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.study import Study
from app.models.screener_criteria import ScreenerCriteria
from app.models.study_assignment import StudyAssignment
from app.schemas.study import (
    StudyCreate,
    StudyUpdate,
    StudyResponse,
    StudyDetailResponse,
    StudyListResponse,
    AssignmentCounts,
)
from app.schemas.respondent import RespondentResponse
from app.schemas.study_assignment import AssignmentCreate, AssignmentResponse
from app.services.matching_service import MatchingService

router = APIRouter()


@router.post("", response_model=StudyResponse, status_code=201)
async def create_study(
    data: StudyCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new study with optional screener criteria."""
    study = Study(
        title=data.title,
        client_name=data.client_name,
        methodology=data.methodology,
        target_count=data.target_count,
        incentive_amount=data.incentive_amount,
        status=data.status,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    db.add(study)
    await db.flush()

    # Add criteria
    for criterion_data in data.criteria:
        criterion = ScreenerCriteria(
            study_id=study.id,
            field_name=criterion_data.field_name,
            operator=criterion_data.operator,
            value=criterion_data.value,
        )
        db.add(criterion)

    await db.flush()
    await db.refresh(study)
    return study


@router.get("", response_model=StudyListResponse)
async def list_studies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    client_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List studies with optional filters and pagination."""
    query = select(Study)
    count_query = select(func.count(Study.id))

    if status:
        query = query.where(Study.status == status)
        count_query = count_query.where(Study.status == status)

    if client_name:
        query = query.where(Study.client_name.ilike(f"%{client_name}%"))
        count_query = count_query.where(Study.client_name.ilike(f"%{client_name}%"))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    query = query.order_by(Study.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    studies = list(result.scalars().all())

    return StudyListResponse(
        items=studies,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{study_id}", response_model=StudyDetailResponse)
async def get_study(
    study_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a study with criteria and assignment counts."""
    result = await db.execute(
        select(Study)
        .options(selectinload(Study.criteria))
        .where(Study.id == study_id)
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Get assignment counts by status
    counts_result = await db.execute(
        select(
            StudyAssignment.status,
            func.count(StudyAssignment.id).label("count"),
        )
        .where(StudyAssignment.study_id == study_id)
        .group_by(StudyAssignment.status)
    )
    counts_raw = {row.status: row.count for row in counts_result}

    assignment_counts = AssignmentCounts(
        invited=counts_raw.get("invited", 0),
        confirmed=counts_raw.get("confirmed", 0),
        completed=counts_raw.get("completed", 0),
        no_show=counts_raw.get("no_show", 0),
        rejected=counts_raw.get("rejected", 0),
        total=sum(counts_raw.values()),
    )

    return StudyDetailResponse(
        id=study.id,
        title=study.title,
        client_name=study.client_name,
        methodology=study.methodology,
        target_count=study.target_count,
        incentive_amount=study.incentive_amount,
        status=study.status,
        start_date=study.start_date,
        end_date=study.end_date,
        created_at=study.created_at,
        criteria=study.criteria,
        assignment_counts=assignment_counts,
    )


@router.put("/{study_id}", response_model=StudyResponse)
async def update_study(
    study_id: int,
    data: StudyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a study."""
    result = await db.execute(
        select(Study)
        .options(selectinload(Study.criteria))
        .where(Study.id == study_id)
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    update_data = data.model_dump(exclude_unset=True, exclude={"criteria"})
    for field, value in update_data.items():
        setattr(study, field, value)

    # Update criteria if provided
    if data.criteria is not None:
        # Remove existing criteria
        for criterion in study.criteria:
            await db.delete(criterion)

        # Add new criteria
        for criterion_data in data.criteria:
            criterion = ScreenerCriteria(
                study_id=study.id,
                field_name=criterion_data.field_name,
                operator=criterion_data.operator,
                value=criterion_data.value,
            )
            db.add(criterion)

    await db.flush()
    await db.refresh(study)
    return study


@router.get("/{study_id}/match", response_model=dict)
async def find_matching_respondents(
    study_id: int,
    exclude_assigned: bool = Query(True),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Find respondents matching the study's screener criteria."""
    # Verify study exists
    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    service = MatchingService(db)
    respondents, total = await service.find_matching_respondents(
        study_id=study_id,
        exclude_assigned=exclude_assigned,
        limit=limit,
        offset=offset,
    )

    return {
        "items": [RespondentResponse.model_validate(r) for r in respondents],
        "total": total,
        "limit": limit,
        "offset": offset,
        "study_id": study_id,
    }


@router.post("/{study_id}/assign", response_model=List[AssignmentResponse], status_code=201)
async def assign_respondents(
    study_id: int,
    data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Assign respondent(s) to a study."""
    # Verify study exists
    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    assignments = []
    for respondent_id in data.respondent_ids:
        # Check if already assigned
        existing_result = await db.execute(
            select(StudyAssignment).where(
                StudyAssignment.study_id == study_id,
                StudyAssignment.respondent_id == respondent_id,
            )
        )
        if existing_result.scalar_one_or_none():
            continue  # Skip already assigned

        assignment = StudyAssignment(
            study_id=study_id,
            respondent_id=respondent_id,
            notes=data.notes,
        )
        db.add(assignment)
        assignments.append(assignment)

    await db.flush()
    for assignment in assignments:
        await db.refresh(assignment)

    return assignments
