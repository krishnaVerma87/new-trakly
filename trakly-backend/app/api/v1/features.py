"""Feature management endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.schemas.feature import (
    FeatureCreate,
    FeatureUpdate,
    FeatureResponse,
    FeatureWithIssuesResponse,
)
from app.services.feature_service import FeatureService
from app.services.project_service import ProjectService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/features", tags=["Features"])


@router.post("", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_feature(
    feature_data: FeatureCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new feature in a project.
    """
    # Verify project access
    project_service = ProjectService(db)
    try:
        project = await project_service.get_project(feature_data.project_id)
        if project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    feature_service = FeatureService(db)
    feature = await feature_service.create_feature(
        feature_data.model_dump(),
        created_by=current_user.id,
    )

    # Add feature_key property
    response = FeatureResponse.model_validate(feature)
    response.feature_key = f"FEAT-{feature.feature_number}"
    return response


@router.get("", response_model=List[FeatureResponse])
async def list_features(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List features in a project.
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

    feature_service = FeatureService(db)
    features = await feature_service.list_features(
        project_id=project_id,
        skip=skip,
        limit=limit,
        status=status,
    )

    # Add feature_key to each
    result = []
    for f in features:
        response = FeatureResponse.model_validate(f)
        response.feature_key = f"FEAT-{f.feature_number}"
        result.append(response)

    return result


@router.get("/{feature_id}", response_model=FeatureWithIssuesResponse)
async def get_feature(
    feature_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get feature by ID with linked issues and bug statistics.
    """
    feature_service = FeatureService(db)

    try:
        feature = await feature_service.get_feature(feature_id)

        # Verify access
        if feature.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Get bug stats
        bug_stats = await feature_service.get_feature_bug_stats(feature_id)

        # Build response with linked issues
        response = FeatureWithIssuesResponse.model_validate(feature)
        response.feature_key = f"FEAT-{feature.feature_number}"
        response.bug_count = bug_stats["total_bugs"]
        response.open_bug_count = bug_stats["open_bugs"]

        # Add linked issues info
        linked_issues = []
        for link in feature.issue_links:
            if hasattr(link, "issue") and link.issue:
                linked_issues.append({
                    "id": link.issue.id,
                    "issue_key": link.issue.issue_key,
                    "title": link.issue.title,
                    "issue_type": link.issue.issue_type.value,
                    "status": link.issue.status.value,
                    "severity": link.issue.severity.value if link.issue.severity else None,
                    "link_type": link.link_type.value,
                })
        response.linked_issues = linked_issues

        return response
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{feature_id}", response_model=FeatureResponse)
async def update_feature(
    feature_id: str,
    feature_data: FeatureUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a feature.
    """
    feature_service = FeatureService(db)

    try:
        feature = await feature_service.get_feature(feature_id)
        if feature.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        updated_feature = await feature_service.update_feature(
            feature_id,
            feature_data.model_dump(exclude_unset=True),
        )

        response = FeatureResponse.model_validate(updated_feature)
        response.feature_key = f"FEAT-{updated_feature.feature_number}"
        return response
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(
    feature_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a feature.
    """
    feature_service = FeatureService(db)

    try:
        feature = await feature_service.get_feature(feature_id)
        if feature.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        await feature_service.delete_feature(feature_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
