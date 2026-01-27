"""Project management endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectPinResponse,
    ProjectMemberCreate,

    ProjectMemberResponse,
    ComponentCreate,
    ComponentResponse,
)
from app.schemas.label import (
    LabelCreate,
    LabelUpdate,
    LabelResponse,
)
from app.services.project_service import ProjectService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.api.project_permissions import (
    require_project_admin,
    require_project_viewer,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new project in the organization.
    """
    # Verify user is creating in their own organization
    if current_user.organization_id != project_data.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create project in another organization",
        )

    project_service = ProjectService(db)

    try:
        project = await project_service.create_project(project_data.model_dump())
        return project
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/pinned", response_model=List[ProjectResponse])
async def list_pinned_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List projects pinned by the current user."""
    project_service = ProjectService(db)
    projects = await project_service.get_pinned_projects(current_user.id)

    # Map to include is_pinned=True
    for p in projects:
        p.is_pinned = True

    return projects


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    filter_by_membership: bool = Query(True, description="Only show projects where user is a member"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List projects in the current user's organization.
    By default, only shows projects where the user is a member.
    Set filter_by_membership=false to see all organization projects (requires admin).
    """
    project_service = ProjectService(db)

    projects = await project_service.list_projects(
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        active_only=active_only,
        user_id=current_user.id if filter_by_membership else None,
    )
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get project by ID.
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(project_id)

        # Verify access
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return project
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a project. Requires project admin role.
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Check project admin permission
        await require_project_admin(db, current_user, project_id)

        updated_project = await project_service.update_project(
            project_id,
            project_data.model_dump(exclude_unset=True),
        )
        return updated_project
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a project. Requires project admin role.
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Check project admin permission
        await require_project_admin(db, current_user, project_id)

        await project_service.delete_project(project_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Project Members

@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: str,
    member_data: ProjectMemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a member to a project. Requires project admin role.
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Check project admin permission
        await require_project_admin(db, current_user, project_id)

        member = await project_service.add_member(
            project_id=project_id,
            user_id=member_data.user_id,
            role=member_data.role,
            assigned_by=current_user.id,
        )
        return member
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def list_project_members(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List members of a project. Any project member can view.
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Check project membership (any role can view members)
        await require_project_viewer(db, current_user, project_id)

        return await project_service.get_members(project_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(
    project_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a member from a project. Requires project admin role.
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Check project admin permission
        await require_project_admin(db, current_user, project_id)

        await project_service.remove_member(project_id, user_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Components

@router.post("/{project_id}/components", response_model=ComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_component(
    project_id: str,
    component_data: ComponentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a component in a project.
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        component = await project_service.create_component(
            project_id,
            component_data.model_dump(),
        )
        return component
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{project_id}/components", response_model=List[ComponentResponse])
async def list_components(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List components in a project.
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return await project_service.get_components(project_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Labels

@router.post("/{project_id}/labels", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
async def create_label(
    project_id: str,
    label_data: LabelCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a label in a project.
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        label = await project_service.create_label(
            project_id,
            label_data.model_dump(),
        )
        return label
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{project_id}/labels", response_model=List[LabelResponse])
async def list_labels(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List labels in a project.
    """
    project_service = ProjectService(db)

    try:
        project = await project_service.get_project(project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return await project_service.get_labels(project_id, skip, limit)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/labels/{label_id}", response_model=LabelResponse)
async def update_label(
    label_id: str,
    label_data: LabelUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a label.
    """
    project_service = ProjectService(db)

    try:
        label = await project_service.label_repo.get(label_id)
        if not label:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")

        # Verify access via project
        project = await project_service.get_project(label.project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        updated_label = await project_service.update_label(
            label_id,
            label_data.model_dump(exclude_unset=True),
        )
        return updated_label
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    label_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a label.
    """
    project_service = ProjectService(db)

    try:
        label = await project_service.label_repo.get(label_id)
        if not label:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")

        # Verify access via project
        project = await project_service.get_project(label.project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        await project_service.delete_label(label_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Project Pins

@router.post("/{project_id}/pin", response_model=ProjectPinResponse, status_code=status.HTTP_201_CREATED)
async def pin_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pin a project for easy navigation."""
    project_service = ProjectService(db)
    try:
        return await project_service.pin_project(project_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{project_id}/pin", status_code=status.HTTP_204_NO_CONTENT)
async def unpin_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unpin a project."""
    project_service = ProjectService(db)
    await project_service.unpin_project(project_id, current_user.id)
    return None

