import logging
from datetime import datetime, time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="UTC")


async def daily_report(app: Application):
    """Send daily summary to all active users."""
    logger.info("Running daily report job...")
    # In production: fetch active users from DB and send report
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    logger.info(f"Daily report sent at {now}")


async def cleanup_old_messages(app: Application):
    """Clean up messages older than 30 days."""
    logger.info("Running cleanup job...")
    # In production: delete old records from DB
    logger.info("Cleanup complete")


async def health_ping(app: Application):
    """Internal health check job."""
    logger.debug("Health ping OK")


def setup_scheduler(app: Application):
    # Daily report at 09:00 UTC
    scheduler.add_job(
        daily_report,
        CronTrigger(hour=9, minute=0),
        args=[app],
        id="daily_report",
        replace_existing=True,
    )

    # Cleanup every Sunday at 02:00 UTC
    scheduler.add_job(
        cleanup_old_messages,
        CronTrigger(day_of_week="sun", hour=2, minute=0),
        args=[app],
        id="cleanup",
        replace_existing=True,
    )

    # Health ping every 5 minutes
    scheduler.add_job(
        health_ping,
        "interval",
        minutes=5,
        args=[app],
        id="health_ping",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f"Scheduler started with {len(scheduler.get_jobs())} jobs")
