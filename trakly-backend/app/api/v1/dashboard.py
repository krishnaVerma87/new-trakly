"""Dashboard endpoints for analytics."""
from typing import Dict, List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.issue import Issue, IssueStatus, IssueType, Priority
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


@router.get("/developer")
async def get_developer_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get dashboard data for developers - focuses on their assigned tasks.
    """
    from sqlalchemy.orm import selectinload

    user_id = current_user.id

    # Get my assigned issues
    my_issues_result = await db.execute(
        select(Issue)
        .where(Issue.assignee_id == user_id)
        .where(Issue.status.not_in([IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]))
        .options(selectinload(Issue.project))
        .order_by(Issue.priority.desc(), Issue.created_at.desc())
    )
    my_issues = my_issues_result.scalars().all()

    # Count by priority
    priority_counts = {}
    for issue in my_issues:
        priority = issue.priority.value
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    # Count by status
    status_counts = {}
    for issue in my_issues:
        status = issue.status.value
        status_counts[status] = status_counts.get(status, 0) + 1

    # Get recent issues assigned to me
    recent_assigned = [
        {
            "id": issue.id,
            "issue_key": issue.issue_key,
            "title": issue.title,
            "issue_type": issue.issue_type.value,
            "status": issue.status.value,
            "priority": issue.priority.value,
            "project_name": issue.project.name if issue.project else None,
            "created_at": issue.created_at.isoformat(),
        }
        for issue in my_issues[:10]
    ]

    # Time tracking stats
    total_time_spent = sum(issue.time_spent_minutes for issue in my_issues)
    total_time_estimated = sum(issue.time_estimate_minutes or 0 for issue in my_issues)

    return {
        "my_issues": {
            "total": len(my_issues),
            "by_priority": priority_counts,
            "by_status": status_counts,
            "critical_count": priority_counts.get("critical", 0),
            "high_count": priority_counts.get("high", 0),
        },
        "recent_assigned": recent_assigned,
        "time_tracking": {
            "total_spent_minutes": total_time_spent,
            "total_estimated_minutes": total_time_estimated,
            "total_spent_hours": round(total_time_spent / 60, 1),
            "total_estimated_hours": round(total_time_estimated / 60, 1),
        },
    }


@router.get("/project-manager")
async def get_project_manager_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get dashboard data for project managers/scrum masters - focuses on team and sprint metrics.
    """
    from sqlalchemy.orm import selectinload
    from app.models.sprint import Sprint

    org_id = current_user.organization_id

    # Get active sprints
    active_sprints_result = await db.execute(
        select(Sprint)
        .where(Sprint.is_active == True)
        .join(Project, Sprint.project_id == Project.id)
        .where(Project.organization_id == org_id)
        .options(selectinload(Sprint.issues))
    )
    active_sprints = active_sprints_result.scalars().all()

    sprint_stats = []
    for sprint in active_sprints:
        total_issues = len(sprint.issues)
        completed_issues = sum(
            1 for issue in sprint.issues
            if issue.status in [IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]
        )
        sprint_stats.append({
            "id": sprint.id,
            "name": sprint.name,
            "goal": sprint.goal,
            "start_date": sprint.start_date.isoformat(),
            "end_date": sprint.end_date.isoformat(),
            "total_issues": total_issues,
            "completed_issues": completed_issues,
            "progress_percentage": round((completed_issues / total_issues * 100) if total_issues > 0 else 0, 1),
        })

    # Get team workload - issues by assignee
    team_workload_result = await db.execute(
        select(
            User.id,
            User.full_name,
            func.count(Issue.id).label("issue_count"),
        )
        .join(Issue, User.id == Issue.assignee_id)
        .where(User.organization_id == org_id)
        .where(Issue.status.not_in([IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]))
        .group_by(User.id, User.full_name)
        .order_by(func.count(Issue.id).desc())
    )
    team_workload = [
        {
            "user_id": row.id,
            "user_name": row.full_name,
            "active_issues": row.issue_count,
        }
        for row in team_workload_result.fetchall()
    ]

    # Get pending issues (unassigned)
    pending_issues_result = await db.execute(
        select(func.count(Issue.id))
        .where(Issue.organization_id == org_id)
        .where(Issue.assignee_id == None)
        .where(Issue.status.not_in([IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]))
    )
    pending_issues_count = pending_issues_result.scalar_one()

    # Get blocked issues (you can add a 'blocked' field to issues if needed)
    # For now, we'll use issues in review status as proxy
    blocked_issues_result = await db.execute(
        select(func.count(Issue.id))
        .where(Issue.organization_id == org_id)
        .where(Issue.status == IssueStatus.REVIEW)
    )
    blocked_issues_count = blocked_issues_result.scalar_one()

    return {
        "active_sprints": sprint_stats,
        "team_workload": team_workload,
        "pending_issues": pending_issues_count,
        "blocked_issues": blocked_issues_count,
        "summary": {
            "active_sprint_count": len(active_sprints),
            "team_members": len(team_workload),
        },
    }


@router.get("/bug-trends")
async def get_bug_trends(
    project_id: str = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get bug trend analysis over time.
    Shows creation and resolution trends grouped by day.
    """
    from datetime import datetime, timedelta
    from sqlalchemy import and_, cast, Date

    org_id = current_user.organization_id
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Build base query
    base_query = (
        select(
            cast(Issue.created_at, Date).label("date"),
            func.count(Issue.id).label("count"),
        )
        .where(Issue.organization_id == org_id)
        .where(Issue.issue_type == IssueType.BUG)
    )

    if project_id:
        base_query = base_query.where(Issue.project_id == project_id)

    # Get bugs created per day
    created_query = (
        base_query
        .where(Issue.created_at >= start_date)
        .group_by(cast(Issue.created_at, Date))
        .order_by(cast(Issue.created_at, Date))
    )
    created_result = await db.execute(created_query)
    created_data = {str(row.date): row.count for row in created_result.fetchall()}

    # Get bugs resolved per day
    resolved_query = (
        select(
            cast(Issue.resolved_at, Date).label("date"),
            func.count(Issue.id).label("count"),
        )
        .where(Issue.organization_id == org_id)
        .where(Issue.issue_type == IssueType.BUG)
        .where(Issue.resolved_at.isnot(None))
        .where(Issue.resolved_at >= start_date)
    )

    if project_id:
        resolved_query = resolved_query.where(Issue.project_id == project_id)

    resolved_query = (
        resolved_query
        .group_by(cast(Issue.resolved_at, Date))
        .order_by(cast(Issue.resolved_at, Date))
    )
    resolved_result = await db.execute(resolved_query)
    resolved_data = {str(row.date): row.count for row in resolved_result.fetchall()}

    # Get current bug counts by severity
    severity_query = (
        select(Issue.severity, func.count(Issue.id))
        .where(Issue.organization_id == org_id)
        .where(Issue.issue_type == IssueType.BUG)
        .where(Issue.status.not_in([IssueStatus.CLOSED, IssueStatus.DONE, IssueStatus.WONT_FIX]))
    )

    if project_id:
        severity_query = severity_query.where(Issue.project_id == project_id)

    severity_query = severity_query.group_by(Issue.severity)
    severity_result = await db.execute(severity_query)
    by_severity = {
        (row[0].value if row[0] else "unset"): row[1]
        for row in severity_result.fetchall()
    }

    # Get current bug counts by priority
    priority_query = (
        select(Issue.priority, func.count(Issue.id))
        .where(Issue.organization_id == org_id)
        .where(Issue.issue_type == IssueType.BUG)
        .where(Issue.status.not_in([IssueStatus.CLOSED, IssueStatus.DONE, IssueStatus.WONT_FIX]))
    )

    if project_id:
        priority_query = priority_query.where(Issue.project_id == project_id)

    priority_query = priority_query.group_by(Issue.priority)
    priority_result = await db.execute(priority_query)
    by_priority = {row[0].value: row[1] for row in priority_result.fetchall()}

    # Build timeline with all dates in range
    timeline = []
    current_date = start_date.date()
    while current_date <= end_date.date():
        date_str = str(current_date)
        timeline.append({
            "date": date_str,
            "created": created_data.get(date_str, 0),
            "resolved": resolved_data.get(date_str, 0),
        })
        current_date += timedelta(days=1)

    return {
        "timeline": timeline,
        "by_severity": by_severity,
        "by_priority": by_priority,
        "total_open": sum(by_severity.values()),
        "start_date": start_date.date().isoformat(),
        "end_date": end_date.date().isoformat(),
    }
