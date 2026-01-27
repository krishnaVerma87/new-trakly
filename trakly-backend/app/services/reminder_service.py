"""Reminder service for evaluating rules and triggering notifications."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.reminder_rule import ReminderRule
from app.models.notification import NotificationType
from app.repositories.reminder_rule import ReminderRuleRepository
from app.repositories.issue import IssueRepository
from app.repositories.sprint import SprintRepository
from app.repositories.watcher import WatcherRepository
from app.repositories.project import ProjectRepository
from app.services.notification_service import NotificationService


class ReminderService:
    """Service for reminder rule management and execution."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rule_repo = ReminderRuleRepository(db)
        self.issue_repo = IssueRepository(db)
        self.sprint_repo = SprintRepository(db)
        self.watcher_repo = WatcherRepository(db)
        self.project_repo = ProjectRepository(db)
        self.notification_service = NotificationService(db)

    async def create_rule(
        self,
        rule_data: Dict[str, Any],
        created_by: str,
    ) -> ReminderRule:
        """Create a new reminder rule."""
        project_id = rule_data["project_id"]

        # Verify project exists
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Validate conditions schema
        self._validate_conditions(rule_data["conditions"])

        return await self.rule_repo.create(rule_data)

    async def list_rules(
        self,
        project_id: str,
        include_disabled: bool = False,
    ) -> List[ReminderRule]:
        """List all reminder rules for a project."""
        rules = await self.rule_repo.get_by_project(project_id)

        if not include_disabled:
            rules = [r for r in rules if r.is_enabled]

        return rules

    async def get_rule(self, rule_id: str) -> ReminderRule:
        """Get a reminder rule by ID."""
        rule = await self.rule_repo.get(rule_id)
        if not rule:
            raise NotFoundError("Reminder rule not found")
        return rule

    async def update_rule(
        self,
        rule_id: str,
        update_data: Dict[str, Any],
    ) -> ReminderRule:
        """Update a reminder rule."""
        rule = await self.rule_repo.get(rule_id)
        if not rule:
            raise NotFoundError("Reminder rule not found")

        # Validate conditions if being updated
        if "conditions" in update_data:
            self._validate_conditions(update_data["conditions"])

        return await self.rule_repo.update(rule_id, update_data)

    async def delete_rule(self, rule_id: str) -> None:
        """Delete a reminder rule."""
        rule = await self.rule_repo.get(rule_id)
        if not rule:
            raise NotFoundError("Reminder rule not found")

        await self.rule_repo.delete(rule_id)

    def _validate_conditions(self, conditions: Dict[str, Any]) -> None:
        """Validate reminder rule conditions schema."""
        required_keys = ["days_without_update"]
        for key in required_keys:
            if key not in conditions:
                raise ValidationError(f"Missing required condition: {key}")

        # Validate days_without_update
        if not isinstance(conditions["days_without_update"], int) or conditions["days_without_update"] < 1:
            raise ValidationError("days_without_update must be a positive integer")

    async def evaluate_rule(self, rule_id: str) -> List[str]:
        """
        Evaluate a reminder rule and trigger notifications.

        Returns:
            List of issue IDs that matched the rule
        """
        rule = await self.rule_repo.get(rule_id)
        if not rule or not rule.is_enabled:
            return []

        # Find issues matching conditions
        matching_issues = await self._find_matching_issues(rule)

        # Send notifications for each matching issue
        for issue in matching_issues:
            await self._send_reminder_notifications(rule, issue)

        # Update last executed timestamp
        await self.rule_repo.update(rule_id, {
            "last_executed_at": datetime.utcnow(),
        })

        return [issue.id for issue in matching_issues]

    async def _find_matching_issues(self, rule: ReminderRule) -> List:
        """Find issues matching rule conditions."""
        conditions = rule.conditions

        # Start with base query for project
        issues = await self.issue_repo.get_by_project(
            project_id=rule.project_id,
            skip=0,
            limit=1000,  # Process in batches
        )

        # Filter by sprint
        if "sprint" in conditions and conditions["sprint"] == "current":
            current_sprint = await self.sprint_repo.get_current_sprint(rule.project_id)
            if current_sprint:
                issues = [i for i in issues if i.sprint_id == current_sprint.id]

        # Filter by status
        if "status" in conditions:
            allowed_statuses = conditions["status"]
            issues = [i for i in issues if i.status.value in allowed_statuses]

        # Filter by priority
        if "priority" in conditions:
            allowed_priorities = conditions["priority"]
            issues = [i for i in issues if i.priority.value in allowed_priorities]

        # Filter by assignee existence
        if conditions.get("assignee_exists"):
            issues = [i for i in issues if i.assignee_id is not None]

        # Filter by issue type
        if "issue_type" in conditions:
            allowed_types = conditions["issue_type"]
            issues = [i for i in issues if i.issue_type.value in allowed_types]

        # Filter by days without update
        days_threshold = conditions["days_without_update"]
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
        issues = [i for i in issues if i.updated_at < cutoff_date]

        return issues

    async def _send_reminder_notifications(
        self,
        rule: ReminderRule,
        issue,
    ) -> None:
        """Send notifications for a matching issue."""
        notification_type = NotificationType.REMINDER_STALE

        # Build notification message
        title = rule.notification_title.format(
            issue_key=issue.issue_key,
            issue_title=issue.title,
        )
        message = rule.notification_message.format(
            issue_key=issue.issue_key,
            issue_title=issue.title,
            days=rule.conditions["days_without_update"],
        )

        meta_data = {
            "reminder_rule_id": rule.id,
            "days_without_update": rule.conditions["days_without_update"],
        }

        recipients = set()

        # Notify assignee
        if rule.notify_assignee and issue.assignee_id:
            recipients.add(issue.assignee_id)

        # Notify watchers
        if rule.notify_watchers:
            watchers = await self.watcher_repo.get_watchers_for_issue(issue.id)
            recipients.update([w.id for w in watchers])

        # Send notifications
        for user_id in recipients:
            await self.notification_service.send_notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                issue_id=issue.id,
                project_id=issue.project_id,
                meta_data=meta_data,
            )
