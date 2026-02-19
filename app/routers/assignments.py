from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.study_assignment import StudyAssignment
from app.schemas.study_assignment import AssignmentUpdate, AssignmentResponse

router = APIRouter()


@router.patch("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    data: AssignmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update assignment status (confirm, complete, no-show, etc.)."""
    result = await db.execute(
        select(StudyAssignment).where(StudyAssignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Update status
    old_status = assignment.status
    assignment.status = data.status

    # Set timestamps based on status transitions
    if data.status == "confirmed" and old_status != "confirmed":
        assignment.confirmed_at = datetime.utcnow()
    elif data.status == "completed" and old_status != "completed":
        assignment.completed_at = datetime.utcnow()
        if not assignment.confirmed_at:
            assignment.confirmed_at = datetime.utcnow()

    if data.notes is not None:
        assignment.notes = data.notes

    await db.flush()
    await db.refresh(assignment)
    return assignment


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single assignment by ID."""
    result = await db.execute(
        select(StudyAssignment).where(StudyAssignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment
