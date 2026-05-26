"""FastAPI application entry point for the Maritime Agents system.

Endpoints:
    GET  /health               – Liveness check.
    POST /run/daily-report     – Manually trigger the daily report workflow.
    GET  /reports/latest       – Retrieve the most recently generated report.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel

from app.config import get_settings
from app.scheduler import start_scheduler, stop_scheduler
from agents.supervisor_agent import run_supervisor
from models.report_models import DailyReport

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start and stop the background scheduler with the application."""
    start_scheduler()
    yield
    stop_scheduler()


# ── App factory ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Maritime Agents API",
    description=(
        "Multi-agent maritime intelligence system.  "
        "Collects news, AIS, port and weather data and generates daily reports."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# In-memory store for the last generated report (replace with a DB in production)
_latest_report: Optional[DailyReport] = None


# ── Request / Response schemas ─────────────────────────────────────────────────


class RunDailyReportRequest(BaseModel):
    """Optional parameters for the POST /run/daily-report endpoint."""

    report_date: Optional[date] = None
    send_email: bool = False
    email_recipients: list[str] = []
    email_dry_run: bool = True


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


# ── Endpoints ─────────────────────────────────────────────────────────────────


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health() -> HealthResponse:
    """Return a simple liveness response."""
    return HealthResponse()


@app.post("/run/daily-report", response_model=DailyReport, tags=["Reports"])
async def run_daily_report(request: RunDailyReportRequest = RunDailyReportRequest()):
    """Trigger the daily maritime intelligence report workflow.

    The workflow runs all specialist agents (News, AIS, Port, Weather) and
    assembles a Markdown report.  Set ``send_email=true`` and provide
    ``email_recipients`` to also dispatch the report by email.

    Returns the completed :class:`~models.report_models.DailyReport`.
    """
    global _latest_report  # noqa: PLW0603

    settings = get_settings()

    try:
        report = run_supervisor(
            report_date=request.report_date,
            send_email=request.send_email,
            email_recipients=request.email_recipients or settings.email_recipients,
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
            email_dry_run=request.email_dry_run,
        )

        # Persist to disk
        reports_dir = settings.reports_path
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = reports_dir / f"report_{report.report_date}.md"
        report_file.write_text(report.markdown_content, encoding="utf-8")
        logger.info("Report saved to %s", report_file)

        _latest_report = report
        return report

    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to run daily report workflow")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/reports/latest", tags=["Reports"])
async def get_latest_report(format: str = "json"):
    """Return the most recently generated report.

    Query parameters:
        format: ``json`` (default) or ``markdown``.

    Raises:
        404 if no report has been generated yet in this session.
    """
    settings = get_settings()

    # Try to load the most recent report from disk if not cached in memory
    if _latest_report is None:
        reports_dir = settings.reports_path
        if reports_dir.exists():
            report_files = sorted(reports_dir.glob("report_*.md"), reverse=True)
            if report_files:
                # Return the raw Markdown of the latest file
                content = report_files[0].read_text(encoding="utf-8")
                if format == "markdown":
                    return PlainTextResponse(content, media_type="text/markdown")
                return JSONResponse(
                    {"report_date": report_files[0].stem.replace("report_", ""), "content": content}
                )

        raise HTTPException(
            status_code=404,
            detail="No report has been generated yet. Call POST /run/daily-report first.",
        )

    if format == "markdown":
        return PlainTextResponse(
            _latest_report.markdown_content, media_type="text/markdown"
        )

    return _latest_report
