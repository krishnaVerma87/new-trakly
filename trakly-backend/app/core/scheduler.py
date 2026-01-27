"""Background job scheduler using APScheduler."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from pytz import timezone

logger = logging.getLogger(__name__)

# Configure scheduler
jobstores = {
    'default': MemoryJobStore()
}

executors = {
    'default': AsyncIOExecutor()
}

job_defaults = {
    'coalesce': True,  # Combine missed runs
    'max_instances': 1,  # Prevent concurrent execution
    'misfire_grace_time': 300  # 5 minutes grace for missed jobs
}

# Global scheduler instance
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=timezone('UTC')
)


def start_scheduler():
    """Start the background scheduler."""
    if not scheduler.running:
        scheduler.start()
        logger.info("Background scheduler started")


def shutdown_scheduler():
    """Shutdown the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Background scheduler shutdown")
