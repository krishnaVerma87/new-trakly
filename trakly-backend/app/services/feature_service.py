"""Feature management service."""
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.feature import Feature, FeatureStatus
from app.repositories.feature import FeatureRepository
from app.repositories.project import ProjectRepository


class FeatureService:
    """Service for feature operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.feature_repo = FeatureRepository(db)
        self.project_repo = ProjectRepository(db)

    async def create_feature(
        self,
        feature_data: Dict[str, Any],
        created_by: str,
    ) -> Feature:
        """
        Create a new feature.

        Args:
            feature_data: Feature creation data
            created_by: User ID of creator

        Returns:
            Created feature
        """
        project_id = feature_data["project_id"]

        # Verify project exists
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Get next feature number
        feature_number = await self.feature_repo.get_next_feature_number(project_id)

        feature_data["organization_id"] = project.organization_id
        feature_data["feature_number"] = feature_number
        feature_data["created_by"] = created_by

        return await self.feature_repo.create(feature_data)

    async def get_feature(self, feature_id: str) -> Feature:
        """Get feature by ID with linked issues."""
        feature = await self.feature_repo.get_with_issues(feature_id)
        if not feature:
            raise NotFoundError("Feature not found")
        return feature

    async def list_features(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Feature]:
        """List features in a project."""
        status_enum = None
        if status:
            try:
                status_enum = FeatureStatus(status)
            except ValueError:
                pass  # Invalid status, ignore filter

        return await self.feature_repo.get_by_project(
            project_id,
            skip=skip,
            limit=limit,
            status=status_enum,
        )

    async def update_feature(
        self,
        feature_id: str,
        feature_data: Dict[str, Any],
    ) -> Feature:
        """Update an existing feature."""
        feature = await self.feature_repo.get(feature_id)
        if not feature:
            raise NotFoundError("Feature not found")

        # Convert status string to enum if provided
        if "status" in feature_data:
            try:
                feature_data["status"] = FeatureStatus(feature_data["status"])
            except ValueError:
                pass

        updated_feature = await self.feature_repo.update(feature_id, feature_data)
        return updated_feature

    async def delete_feature(self, feature_id: str) -> bool:
        """Delete a feature."""
        feature = await self.feature_repo.get(feature_id)
        if not feature:
            raise NotFoundError("Feature not found")

        return await self.feature_repo.delete(feature_id)

    async def get_feature_bug_stats(
        self,
        feature_id: str,
    ) -> Dict[str, int]:
        """Get bug statistics for a feature."""
        from app.repositories.issue import IssueRepository
        from app.models.issue import IssueStatus

        issue_repo = IssueRepository(self.db)
        bugs = await issue_repo.get_bugs_by_feature(feature_id)

        total = len(bugs)
        open_bugs = sum(
            1 for b in bugs
            if b.status not in [IssueStatus.CLOSED, IssueStatus.DONE, IssueStatus.WONT_FIX]
        )

        return {
            "total_bugs": total,
            "open_bugs": open_bugs,
            "closed_bugs": total - open_bugs,
        }
