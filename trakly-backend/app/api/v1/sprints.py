"""Sprint management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.schemas.sprint import SprintCreate, SprintUpdate, SprintResponse, SprintCompletion, SprintStats
from app.services.sprint_service import SprintService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/sprints", tags=["Sprints"])


@router.post("", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    sprint_data: SprintCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new sprint."""
    sprint_service = SprintService(db)
    try:
        sprint = await sprint_service.create_sprint(
            sprint_data.model_dump(),
            created_by=current_user.id,
        )
        # Calculate issue counts
        from app.models.issue import IssueStatus
        issue_count = len(sprint.issues)
        completed_count = sum(
            1 for issue in sprint.issues
            if issue.status in [IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]
        )
        return SprintResponse.from_orm_with_counts(sprint, issue_count, completed_count)
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/project/{project_id}", response_model=List[SprintResponse])
async def list_sprints(
    project_id: str,
    include_completed: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List sprints for a project."""
    from app.models.issue import IssueStatus
    sprint_service = SprintService(db)
    sprints = await sprint_service.list_sprints(
        project_id,
        include_completed=include_completed,
    )

    # Convert each sprint with counts
    sprint_responses = []
    for sprint in sprints:
        issue_count = len(sprint.issues)
        completed_count = sum(
            1 for issue in sprint.issues
            if issue.status in [IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]
        )
        sprint_responses.append(
            SprintResponse.from_orm_with_counts(sprint, issue_count, completed_count)
        )

    return sprint_responses


@router.get("/project/{project_id}/current", response_model=SprintResponse)
async def get_current_sprint(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current active sprint for a project."""
    from app.models.issue import IssueStatus
    sprint_service = SprintService(db)
    sprint = await sprint_service.get_current_sprint(project_id)

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active sprint found",
        )

    issue_count = len(sprint.issues)
    completed_count = sum(
        1 for issue in sprint.issues
        if issue.status in [IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]
    )
    return SprintResponse.from_orm_with_counts(sprint, issue_count, completed_count)


@router.patch("/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    sprint_id: str,
    sprint_data: SprintUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a sprint."""
    from app.models.issue import IssueStatus
    sprint_service = SprintService(db)
    try:
        sprint = await sprint_service.update_sprint(
            sprint_id,
            sprint_data.model_dump(exclude_unset=True),
        )
        issue_count = len(sprint.issues)
        completed_count = sum(
            1 for issue in sprint.issues
            if issue.status in [IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]
        )
        return SprintResponse.from_orm_with_counts(sprint, issue_count, completed_count)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{sprint_id}/start", response_model=SprintResponse)
async def start_sprint(
    sprint_id: str,
    sprint_data: SprintUpdate, # Reusing update schema for dates
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a sprint."""
    from app.models.issue import IssueStatus
    if not sprint_data.start_date or not sprint_data.end_date:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start and End dates required")

    sprint_service = SprintService(db)
    try:
        sprint = await sprint_service.start_sprint(
            sprint_id,
            sprint_data.start_date,
            sprint_data.end_date,
        )
        issue_count = len(sprint.issues)
        completed_count = sum(
            1 for issue in sprint.issues
            if issue.status in [IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]
        )
        return SprintResponse.from_orm_with_counts(sprint, issue_count, completed_count)
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{sprint_id}/complete", response_model=SprintResponse)
async def complete_sprint(
    sprint_id: str,
    completion_data: SprintCompletion,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark sprint as completed."""
    from app.models.issue import IssueStatus
    sprint_service = SprintService(db)
    try:
        sprint = await sprint_service.complete_sprint(
            sprint_id,
            move_issues_to=completion_data.move_issues_to,
            new_sprint_id=completion_data.new_sprint_id,
        )
        issue_count = len(sprint.issues)
        completed_count = sum(
            1 for issue in sprint.issues
            if issue.status in [IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]
        )
        return SprintResponse.from_orm_with_counts(sprint, issue_count, completed_count)
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{sprint_id}/stats", response_model=SprintStats)
async def get_sprint_stats(
    sprint_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get statistics for a sprint."""
    sprint_service = SprintService(db)
    try:
        stats = await sprint_service.get_sprint_stats(sprint_id)
        return stats
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
