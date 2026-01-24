"""Dashboard endpoints for analytics."""
from typing import Dict, List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.issue import Issue, IssueStatus, IssueType
from app.models.feature import Feature
from app.models.project import Project

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/statistics")
async def get_dashboard_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get overall dashboard statistics for the organization.
    """
    org_id = current_user.organization_id

    # Get project count
    project_count = await db.execute(
        select(func.count(Project.id))
        .where(Project.organization_id == org_id)
        .where(Project.is_active == True)
    )
    total_projects = project_count.scalar_one()

    # Get issue counts by status
    issue_counts = await db.execute(
        select(Issue.status, func.count(Issue.id))
        .where(Issue.organization_id == org_id)
        .group_by(Issue.status)
    )
    status_counts = {status.value: count for status, count in issue_counts.fetchall()}

    # Get issue counts by type
    type_counts = await db.execute(
        select(Issue.issue_type, func.count(Issue.id))
        .where(Issue.organization_id == org_id)
        .group_by(Issue.issue_type)
    )
    issue_type_counts = {itype.value: count for itype, count in type_counts.fetchall()}

    # Get feature count
    feature_count = await db.execute(
        select(func.count(Feature.id))
        .where(Feature.organization_id == org_id)
    )
    total_features = feature_count.scalar_one()

    # Calculate totals
    total_issues = sum(status_counts.values())
    open_issues = sum(
        status_counts.get(s, 0)
        for s in ["new", "in_progress", "review"]
    )
    closed_issues = sum(
        status_counts.get(s, 0)
        for s in ["done", "closed", "wont_fix"]
    )

    return {
        "projects": {
            "total": total_projects,
        },
        "issues": {
            "total": total_issues,
            "open": open_issues,
            "closed": closed_issues,
            "by_status": status_counts,
            "by_type": issue_type_counts,
        },
        "features": {
            "total": total_features,
        },
        "bugs": {
            "total": issue_type_counts.get("bug", 0),
            "open": 0,  # Would need additional query
        },
    }


@router.get("/bugs-per-feature")
async def get_bugs_per_feature(
    project_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get bug count per feature for analytics.
    """
    from app.models.feature_issue_link import FeatureIssueLink

    org_id = current_user.organization_id

    # Query features with their bug counts
    query = (
        select(
            Feature.id,
            Feature.title,
            Feature.feature_number,
            Feature.status,
            func.count(Issue.id).filter(Issue.issue_type == IssueType.BUG).label("bug_count"),
            func.count(Issue.id).filter(
                Issue.issue_type == IssueType.BUG,
                Issue.status.not_in([IssueStatus.CLOSED, IssueStatus.DONE, IssueStatus.WONT_FIX])
            ).label("open_bug_count"),
        )
        .outerjoin(FeatureIssueLink, Feature.id == FeatureIssueLink.feature_id)
        .outerjoin(Issue, FeatureIssueLink.issue_id == Issue.id)
        .where(Feature.organization_id == org_id)
        .group_by(Feature.id)
        .order_by(func.count(Issue.id).desc())
    )

    if project_id:
        query = query.where(Feature.project_id == project_id)

    result = await db.execute(query)
    rows = result.fetchall()

    return [
        {
            "feature_id": row.id,
            "feature_key": f"FEAT-{row.feature_number}",
            "title": row.title,
            "status": row.status.value if row.status else None,
            "bug_count": row.bug_count or 0,
            "open_bug_count": row.open_bug_count or 0,
        }
        for row in rows
    ]


@router.get("/recent-issues")
async def get_recent_issues(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get recently created issues.
    """
    from sqlalchemy.orm import selectinload

    org_id = current_user.organization_id

    result = await db.execute(
        select(Issue)
        .where(Issue.organization_id == org_id)
        .options(
            selectinload(Issue.reporter),
            selectinload(Issue.assignee),
        )
        .order_by(Issue.created_at.desc())
        .limit(limit)
    )
    issues = result.scalars().all()

    return [
        {
            "id": issue.id,
            "issue_key": issue.issue_key,
            "title": issue.title,
            "issue_type": issue.issue_type.value,
            "status": issue.status.value,
            "priority": issue.priority.value,
            "reporter_name": issue.reporter.full_name if issue.reporter else None,
            "assignee_name": issue.assignee.full_name if issue.assignee else None,
            "created_at": issue.created_at.isoformat(),
        }
        for issue in issues
    ]
