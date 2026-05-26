"""APScheduler-based scheduler for the daily maritime intelligence workflow.

The scheduler is started when the FastAPI application starts up and stopped
when it shuts down.  By default it runs the daily report workflow at 06:00 UTC
every day.

TODO: Adjust the ``hour`` / ``minute`` parameters in ``add_daily_report_job``
      to match your preferred report generation time.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from agents.supervisor_agent import run_supervisor

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(timezone="UTC")


def _run_daily_report_job() -> None:
    """Scheduled job: run the full daily report workflow and save the output."""
    settings = get_settings()
    logger.info("Scheduler: triggering daily report job")

    try:
        report = run_supervisor(
            send_email=bool(settings.email_recipients),
            email_recipients=settings.email_recipients,
            news_api_key=settings.news_api_key,
            news_api_url=settings.news_api_url,
            ais_api_key=settings.ais_api_key,
            ais_api_url=settings.ais_api_url,
            port_db_url=settings.port_db_url,
            weather_api_key=settings.weather_api_key,
            weather_api_url=settings.weather_api_url,
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_user=settings.smtp_user,
            smtp_password=settings.smtp_password,
            email_sender=settings.email_from,
            # Use dry_run unless SMTP is fully configured
            email_dry_run=not settings.smtp_host,
        )

        # Persist the report to disk
        reports_dir = settings.reports_path
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = reports_dir / f"report_{report.report_date}.md"
        report_file.write_text(report.markdown_content, encoding="utf-8")
        logger.info("Scheduler: report saved to %s", report_file)

    except Exception:  # noqa: BLE001
        logger.exception("Scheduler: daily report job failed")


def add_daily_report_job(hour: int = 6, minute: int = 0) -> None:
    """Register the daily report cron job with the scheduler.

    Args:
        hour:   UTC hour at which to run the job (0–23).
        minute: UTC minute at which to run the job (0–59).
    """
    _scheduler.add_job(
        _run_daily_report_job,
        trigger=CronTrigger(hour=hour, minute=minute, timezone="UTC"),
        id="daily_maritime_report",
        name="Daily Maritime Intelligence Report",
        replace_existing=True,
    )
    logger.info("Scheduler: daily report job scheduled at %02d:%02d UTC", hour, minute)


def start_scheduler() -> None:
    """Start the background scheduler."""
    add_daily_report_job()
    _scheduler.start()
    logger.info("Scheduler: started")


def stop_scheduler() -> None:
    """Shut down the background scheduler gracefully."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler: stopped")


def get_scheduler() -> BackgroundScheduler:
    """Return the shared scheduler instance (for testing / inspection)."""
    return _scheduler
