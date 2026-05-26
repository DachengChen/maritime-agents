"""Supervisor Agent – orchestrates the daily maritime intelligence workflow.

The supervisor provides a high-level entry point that:
1. Runs each specialist agent (News, AIS, Port, Weather).
2. Passes the combined results to the Report Agent.
3. Optionally sends the report by email.

For a more complex orchestration (e.g. conditional branching, retries, or
parallel fan-out), consider replacing the sequential calls here with a
LangGraph ``StateGraph``; see ``workflows/daily_report_workflow.py`` for the
graph-based implementation.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Optional

from agents.ais_agent import run_ais_agent
from agents.news_agent import run_news_agent
from agents.port_agent import run_port_agent
from agents.report_agent import run_report_agent
from agents.weather_agent import run_weather_agent
from models.report_models import DailyReport, DailyReportInput
from tools.email_tool import send_report_email

logger = logging.getLogger(__name__)


def run_supervisor(
    report_date: Optional[date] = None,
    send_email: bool = False,
    email_recipients: Optional[list[str]] = None,
    # ── per-agent config (passed through to tools) ─────────────────────────────
    news_api_key: Optional[str] = None,
    news_api_url: Optional[str] = None,
    ais_api_key: Optional[str] = None,
    ais_api_url: Optional[str] = None,
    port_db_url: Optional[str] = None,
    weather_api_key: Optional[str] = None,
    weather_api_url: Optional[str] = None,
    # ── email config ───────────────────────────────────────────────────────────
    smtp_host: Optional[str] = None,
    smtp_port: int = 587,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    email_sender: Optional[str] = None,
    email_dry_run: bool = True,
) -> DailyReport:
    """Coordinate all agents and produce the daily maritime intelligence report.

    Args:
        report_date:       Override the report date (defaults to today).
        send_email:        Whether to email the finished report.
        email_recipients:  List of recipient email addresses.
        news_api_key:      News API credential.
        news_api_url:      News API base URL.
        ais_api_key:       AIS provider credential.
        ais_api_url:       AIS provider base URL.
        port_db_url:       SQLAlchemy URL for the port database.
        weather_api_key:   Weather API credential.
        weather_api_url:   Weather API base URL.
        smtp_host:         SMTP server hostname.
        smtp_port:         SMTP server port.
        smtp_user:         SMTP login username.
        smtp_password:     SMTP login password.
        email_sender:      Email "From" address.
        email_dry_run:     When ``True``, simulate email sending without SMTP.

    Returns:
        The assembled :class:`~models.report_models.DailyReport`.
    """

    logger.info("Supervisor: starting daily maritime intelligence workflow")

    # ── Step 1: Run specialist agents ──────────────────────────────────────────
    news_result = run_news_agent(api_key=news_api_key, api_url=news_api_url)
    ais_result = run_ais_agent(api_key=ais_api_key, api_url=ais_api_url)
    port_result = run_port_agent(db_url=port_db_url)
    weather_result = run_weather_agent(api_key=weather_api_key, api_url=weather_api_url)

    # ── Step 2: Assemble report ────────────────────────────────────────────────
    inputs = DailyReportInput(
        report_date=report_date or date.today(),
        news_result=news_result,
        ais_result=ais_result,
        port_result=port_result,
        weather_result=weather_result,
    )
    report = run_report_agent(inputs)
    logger.info("Supervisor: report generated (id=%s)", report.report_id)

    # ── Step 3: Optionally send email ──────────────────────────────────────────
    if send_email and email_recipients:
        subject = f"{report.title} – {report.report_date.strftime('%Y-%m-%d')}"
        sent = send_report_email(
            subject=subject,
            body_markdown=report.markdown_content,
            recipients=email_recipients,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            sender=email_sender,
            dry_run=email_dry_run,
        )
        report.email_sent = sent
        if sent:
            report.email_recipients = email_recipients

    logger.info("Supervisor: workflow complete")
    return report
