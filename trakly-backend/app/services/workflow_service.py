"""Service for managing workflow templates and columns."""
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.orm import selectinload

from app.models.workflow import WorkflowTemplate, WorkflowColumn
from app.models.issue import Issue
from app.models.project import Project
from app.schemas.workflow import (
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate,
    WorkflowColumnBatchUpdate,
    ColumnMigrationWarning,
    WorkflowMigrationPreview,
    ColumnChange,
    WorkflowColumnResponse,
)


class WorkflowService:
    """Service for workflow template operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template(
        self,
        data: WorkflowTemplateCreate,
        organization_id: str,
        user_id: str,
    ) -> WorkflowTemplate:
        """Create a new workflow template with columns."""
        # If setting as default, unset other defaults
        if data.is_default:
            await self._unset_default_templates(organization_id)

        # Create template
        template = WorkflowTemplate(
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            is_default=data.is_default,
            is_system=False,
            created_by=user_id,
        )
        self.db.add(template)
        await self.db.flush()

        # Create columns
        for col_data in data.columns:
            column = WorkflowColumn(
                template_id=template.id,
                name=col_data.name,
                position=col_data.position,
                wip_limit=col_data.wip_limit,
                color=col_data.color,
            )
            self.db.add(column)

        await self.db.commit()
        await self.db.refresh(template)

        # Load relationships
        stmt = (
            select(WorkflowTemplate)
            .where(WorkflowTemplate.id == template.id)
            .options(
                selectinload(WorkflowTemplate.columns),
                selectinload(WorkflowTemplate.projects)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a workflow template by ID with columns."""
        stmt = (
            select(WorkflowTemplate)
            .where(WorkflowTemplate.id == template_id)
            .options(
                selectinload(WorkflowTemplate.columns),
                selectinload(WorkflowTemplate.projects)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        organization_id: str,
        include_system: bool = True,
    ) -> List[WorkflowTemplate]:
        """List all workflow templates for an organization."""
        stmt = (
            select(WorkflowTemplate)
            .where(WorkflowTemplate.organization_id == organization_id)
            .options(
                selectinload(WorkflowTemplate.columns),
                selectinload(WorkflowTemplate.projects)
            )
            .order_by(WorkflowTemplate.is_default.desc(), WorkflowTemplate.name)
        )

        if not include_system:
            stmt = stmt.where(WorkflowTemplate.is_system == False)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_template(
        self,
        template_id: str,
        data: WorkflowTemplateUpdate,
    ) -> WorkflowTemplate:
        """Update workflow template metadata (not columns)."""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")

        if template.is_system:
            raise ValueError("Cannot modify system templates")

        # Update fields
        if data.name is not None:
            template.name = data.name
        if data.description is not None:
            template.description = data.description
        if data.is_default is not None:
            if data.is_default:
                await self._unset_default_templates(template.organization_id)
            template.is_default = data.is_default

        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def delete_template(self, template_id: str) -> None:
        """Delete a workflow template if not in use."""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")

        if template.is_system:
            raise ValueError("Cannot delete system templates")

        # Check if any projects are using this template
        stmt = select(func.count(Project.id)).where(Project.workflow_template_id == template_id)
        result = await self.db.execute(stmt)
        project_count = result.scalar()

        if project_count > 0:
            raise ValueError(
                f"Cannot delete template: {project_count} project(s) are using it. "
                "Please migrate projects to another template first."
            )

        await self.db.delete(template)
        await self.db.commit()

    async def preview_column_changes(
        self,
        template_id: str,
        new_columns: List[Dict[str, Any]],
    ) -> WorkflowMigrationPreview:
        """
        Preview changes to workflow columns and detect issues that need migration.

        Returns warnings for columns being removed that contain issues.
        """
        template = await self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")

        # Get current columns
        current_columns = {col.id: col for col in template.columns}
        current_names = {col.name: col for col in template.columns}

        # Map new columns by name to detect renames/changes
        new_column_map = {col["name"]: col for col in new_columns}

        # Detect changes
        changes: List[ColumnChange] = []
        warnings: List[ColumnMigrationWarning] = []

        # Find removed columns
        removed_column_ids = []
        for col_id, col in current_columns.items():
            if col.name not in new_column_map:
                # Column removed
                changes.append(
                    ColumnChange(
                        column_id=col_id,
                        old_name=col.name,
                        new_name="",
                        action="removed"
                    )
                )
                removed_column_ids.append(col_id)

        # Find added columns
        for new_col in new_columns:
            if new_col["name"] not in current_names:
                changes.append(
                    ColumnChange(
                        column_id="",
                        old_name="",
                        new_name=new_col["name"],
                        action="added"
                    )
                )

        # Check for renamed columns (same position, different name)
        # This is a simplified check - in practice, we might need more sophisticated detection

        # For removed columns, check if they have issues
        if removed_column_ids:
            for col_id in removed_column_ids:
                col = current_columns[col_id]

                # Count issues in this column
                stmt = select(func.count(Issue.id)).where(Issue.workflow_column_id == col_id)
                result = await self.db.execute(stmt)
                issue_count = result.scalar()

                if issue_count > 0:
                    # Get suggested target columns (existing columns that will remain)
                    suggested_columns = []
                    for new_col_data in new_columns:
                        # Find matching column in current set
                        if new_col_data["name"] in current_names:
                            existing_col = current_names[new_col_data["name"]]
                            suggested_columns.append(
                                WorkflowColumnResponse(
                                    id=existing_col.id,
                                    template_id=template_id,
                                    name=existing_col.name,
                                    position=existing_col.position,
                                    wip_limit=existing_col.wip_limit,
                                    color=existing_col.color,
                                    created_at=existing_col.created_at,
                                    updated_at=existing_col.updated_at,
                                )
                            )

                    warnings.append(
                        ColumnMigrationWarning(
                            column_id=col_id,
                            column_name=col.name,
                            issue_count=issue_count,
                            action="removed",
                            suggested_target_columns=suggested_columns,
                        )
                    )

        safe_to_apply = len(warnings) == 0

        return WorkflowMigrationPreview(
            template_id=template_id,
            template_name=template.name,
            changes=changes,
            warnings=warnings,
            safe_to_apply=safe_to_apply,
        )

    async def update_columns(
        self,
        template_id: str,
        data: WorkflowColumnBatchUpdate,
    ) -> WorkflowTemplate:
        """
        Update workflow columns with optional issue migration.

        This handles:
        1. Removing old columns
        2. Creating new columns
        3. Migrating issues from removed columns to new columns
        """
        template = await self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")

        if template.is_system:
            raise ValueError("Cannot modify system template columns")

        # Get preview to validate migration
        preview = await self.preview_column_changes(
            template_id,
            [col.model_dump() for col in data.columns]
        )

        # If there are warnings and no migration actions provided, raise error
        if preview.warnings and not data.migration_actions:
            raise ValueError(
                f"Column changes affect {len(preview.warnings)} column(s) with existing issues. "
                "Please provide migration_actions to specify where to move the issues."
            )

        # Validate migration actions cover all warnings
        if preview.warnings and data.migration_actions:
            warned_column_ids = {w.column_id for w in preview.warnings}
            migration_column_ids = {a.old_column_id for a in data.migration_actions}

            missing = warned_column_ids - migration_column_ids
            if missing:
                raise ValueError(
                    f"Migration actions required for columns: {', '.join(missing)}"
                )

        # Execute migrations first (before deleting columns)
        if data.migration_actions:
            for action in data.migration_actions:
                # Migrate all issues from old column to new column
                stmt = (
                    Issue.__table__.update()
                    .where(Issue.workflow_column_id == action.old_column_id)
                    .values(workflow_column_id=action.new_column_id)
                )
                await self.db.execute(stmt)

        # Delete all existing columns
        stmt = delete(WorkflowColumn).where(WorkflowColumn.template_id == template_id)
        await self.db.execute(stmt)
        await self.db.flush()

        # Create new columns
        for col_data in data.columns:
            column = WorkflowColumn(
                template_id=template_id,
                name=col_data.name,
                position=col_data.position,
                wip_limit=col_data.wip_limit,
                color=col_data.color,
            )
            self.db.add(column)

        await self.db.commit()

        # Reload template with new columns
        return await self.get_template(template_id)

    async def get_column_issue_counts(
        self,
        template_id: str,
    ) -> Dict[str, int]:
        """Get issue count for each column in a template."""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")

        counts = {}
        for column in template.columns:
            stmt = select(func.count(Issue.id)).where(Issue.workflow_column_id == column.id)
            result = await self.db.execute(stmt)
            counts[column.id] = result.scalar()

        return counts

    async def create_default_templates(
        self,
        organization_id: str,
        user_id: str,
    ) -> List[WorkflowTemplate]:
        """
        Create default workflow templates for a new organization.

        Creates:
        1. Software Development (default) - Backlog, To Do, In Progress, Review, Done
        2. Simple Kanban - To Do, In Progress, Done
        3. Support Tickets - New, In Progress, Waiting, Resolved, Closed
        """
        templates_data = [
            {
                "name": "Software Development",
                "description": "Standard software development workflow with review stage",
                "is_default": True,
                "is_system": True,
                "columns": [
                    {"name": "Backlog", "position": 0, "wip_limit": None, "color": "#gray"},
                    {"name": "To Do", "position": 1, "wip_limit": 10, "color": "#blue"},
                    {"name": "In Progress", "position": 2, "wip_limit": 5, "color": "#yellow"},
                    {"name": "Review", "position": 3, "wip_limit": 3, "color": "#purple"},
                    {"name": "Done", "position": 4, "wip_limit": None, "color": "#green"},
                ],
            },
            {
                "name": "Simple Kanban",
                "description": "Basic three-column workflow",
                "is_default": False,
                "is_system": True,
                "columns": [
                    {"name": "To Do", "position": 0, "wip_limit": None, "color": "#blue"},
                    {"name": "In Progress", "position": 1, "wip_limit": 5, "color": "#yellow"},
                    {"name": "Done", "position": 2, "wip_limit": None, "color": "#green"},
                ],
            },
            {
                "name": "Support Tickets",
                "description": "Workflow for customer support and issue resolution",
                "is_default": False,
                "is_system": True,
                "columns": [
                    {"name": "New", "position": 0, "wip_limit": None, "color": "#red"},
                    {"name": "In Progress", "position": 1, "wip_limit": 10, "color": "#yellow"},
                    {"name": "Waiting", "position": 2, "wip_limit": None, "color": "#orange"},
                    {"name": "Resolved", "position": 3, "wip_limit": None, "color": "#blue"},
                    {"name": "Closed", "position": 4, "wip_limit": None, "color": "#green"},
                ],
            },
        ]

        created_templates = []
        for template_data in templates_data:
            columns_data = template_data.pop("columns")
            is_system = template_data.pop("is_system")

            template = WorkflowTemplate(
                organization_id=organization_id,
                created_by=user_id,
                is_system=is_system,
                **template_data
            )
            self.db.add(template)
            await self.db.flush()

            for col_data in columns_data:
                column = WorkflowColumn(
                    template_id=template.id,
                    **col_data
                )
                self.db.add(column)

            created_templates.append(template)

        await self.db.commit()

        # Reload with relationships
        result_templates = []
        for template in created_templates:
            reloaded = await self.get_template(template.id)
            result_templates.append(reloaded)

        return result_templates

    async def get_default_template(
        self,
        organization_id: str,
    ) -> Optional[WorkflowTemplate]:
        """Get the default workflow template for an organization."""
        stmt = (
            select(WorkflowTemplate)
            .where(
                and_(
                    WorkflowTemplate.organization_id == organization_id,
                    WorkflowTemplate.is_default == True
                )
            )
            .options(
                selectinload(WorkflowTemplate.columns),
                selectinload(WorkflowTemplate.projects)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _unset_default_templates(self, organization_id: str) -> None:
        """Unset all default templates for an organization."""
        stmt = (
            WorkflowTemplate.__table__.update()
            .where(
                and_(
                    WorkflowTemplate.organization_id == organization_id,
                    WorkflowTemplate.is_default == True
                )
            )
            .values(is_default=False)
        )
        await self.db.execute(stmt)
