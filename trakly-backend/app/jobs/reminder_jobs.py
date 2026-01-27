"""Background jobs for reminder system."""
import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.scheduler import scheduler
from app.db.session import async_session_maker
from app.services.reminder_service import ReminderService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_db_session():
    """Get standalone DB session for background jobs."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def execute_reminder_rules():
    """
    Background job to execute all enabled reminder rules.

    Runs every 15 minutes to check for issues matching rule conditions.
    """
    logger.info("Starting reminder rule execution")

    async with get_db_session() as db:
        try:
            reminder_service = ReminderService(db)

            # Get all rules that need execution
            from app.repositories.reminder_rule import ReminderRuleRepository
            rule_repo = ReminderRuleRepository(db)
            rules = await rule_repo.get_rules_to_execute()

            logger.info(f"Found {len(rules)} rules to execute")

            # Execute each rule
            for rule in rules:
                try:
                    matching_issues = await reminder_service.evaluate_rule(rule.id)
                    logger.info(
                        f"Rule '{rule.name}' (ID: {rule.id}) matched {len(matching_issues)} issues"
                    )
                except Exception as e:
                    logger.error(f"Error executing rule {rule.id}: {str(e)}", exc_info=True)

            logger.info("Reminder rule execution completed")

        except Exception as e:
            logger.error(f"Error in reminder job: {str(e)}", exc_info=True)


async def schedule_reminder_jobs():
    """Schedule all reminder-related background jobs."""
    # Execute reminder rules every 15 minutes
    scheduler.add_job(
        execute_reminder_rules,
        trigger='interval',
        minutes=15,
        id='reminder_rules_execution',
        replace_existing=True,
        max_instances=1,
    )

    logger.info("Reminder jobs scheduled")
