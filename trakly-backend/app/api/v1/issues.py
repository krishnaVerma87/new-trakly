"""Issue management endpoints with duplicate detection."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueWithDetailsResponse,
    DuplicateCheckRequest,
    DuplicateCheckResponse,
)
from app.services.issue_service import IssueService
from app.services.project_service import ProjectService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post("/check-duplicates", response_model=DuplicateCheckResponse)
async def check_duplicates(
    check_data: DuplicateCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check for duplicate issues before creation.

    Returns similar issues and a suggested deduplication hash.
    This is called during issue creation for real-time duplicate detection.
    """
    # Verify project access
    project_service = ProjectService(db)
    try:
        project = await project_service.get_project(check_data.project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    issue_service = IssueService(db)
    result = await issue_service.check_duplicates(
        project_id=check_data.project_id,
        title=check_data.title,
        description=check_data.description,
    )

    return result


@router.post("", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_data: IssueCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new issue (bug, task, story, etc.).
    """
    # Verify project access
    project_service = ProjectService(db)
    try:
        project = await project_service.get_project(issue_data.project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    issue_service = IssueService(db)
    issue = await issue_service.create_issue(
        issue_data.model_dump(),
        reporter_id=current_user.id,
    )

    return issue


@router.get("", response_model=List[IssueResponse])
async def list_issues(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    issue_type: Optional[str] = None,
    assignee_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List issues in a project with optional filters.
    """
    # Verify project access
    project_service = ProjectService(db)
    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    issue_service = IssueService(db)
    issues = await issue_service.list_issues(
        project_id=project_id,
        skip=skip,
        limit=limit,
        status=status,
        issue_type=issue_type,
        assignee_id=assignee_id,
    )

    return issues


@router.get("/search", response_model=List[IssueResponse])
async def search_issues(
    project_id: str,
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search issues by title, description, or key.
    """
    # Verify project access
    project_service = ProjectService(db)
    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    issue_service = IssueService(db)
    return await issue_service.search_issues(project_id, q, limit)


@router.get("/{issue_id}", response_model=IssueWithDetailsResponse)
async def get_issue(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get issue by ID with full details.
    """
    issue_service = IssueService(db)

    try:
        issue = await issue_service.get_issue(issue_id)

        # Verify access
        if issue.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return issue
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/key/{issue_key}", response_model=IssueWithDetailsResponse)
async def get_issue_by_key(
    issue_key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get issue by key (e.g., TRAK-123).
    """
    issue_service = IssueService(db)

    try:
        issue = await issue_service.get_issue_by_key(issue_key)

        # Verify access
        if issue.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return issue
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: str,
    issue_data: IssueUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an issue.
    """
    issue_service = IssueService(db)

    try:
        issue = await issue_service.get_issue(issue_id)
        if issue.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        updated_issue = await issue_service.update_issue(
            issue_id,
            issue_data.model_dump(exclude_unset=True),
            updated_by=current_user.id,
        )
        return updated_issue
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an issue.
    """
    issue_service = IssueService(db)

    try:
        issue = await issue_service.get_issue(issue_id)
        if issue.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        await issue_service.delete_issue(issue_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
