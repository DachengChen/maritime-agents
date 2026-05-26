"""Report Agent – assembles individual agent outputs into a Markdown report."""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, timezone

from models.report_models import DailyReport, DailyReportInput

logger = logging.getLogger(__name__)


# ── Section formatters ─────────────────────────────────────────────────────────


def _format_news_section(result) -> str:
    """Render the news section of the report."""
    if result is None or not result.success:
        return "_News data unavailable._\n"
    if not result.articles:
        return "_No maritime news retrieved._\n"

    lines = []
    for article in result.articles:
        pub = (
            article.published_at.strftime("%Y-%m-%d %H:%M UTC")
            if article.published_at
            else "unknown date"
        )
        lines.append(f"- **{article.title}** ({article.source}, {pub})")
        if article.summary:
            lines.append(f"  {article.summary}")
    return "\n".join(lines) + "\n"


def _format_ais_section(result) -> str:
    """Render the AIS/vessel section of the report."""
    if result is None or not result.success:
        return "_AIS data unavailable._\n"

    summary_lines = [
        f"- **Vessels checked:** {result.total_vessels_checked}",
        f"- **Alerts generated:** {len(result.alerts)}",
    ]

    if result.alerts:
        summary_lines.append("\n**Vessel Alerts:**\n")
        for alert in result.alerts:
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                alert.severity.lower(), "⚪"
            )
            summary_lines.append(
                f"- {severity_icon} `[{alert.alert_type}]` {alert.description}"
            )

    return "\n".join(summary_lines) + "\n"


def _format_port_section(result) -> str:
    """Render the port section of the report."""
    if result is None or not result.success:
        return "_Port data unavailable._\n"
    if not result.ports:
        return "_No port data retrieved._\n"

    lines = []
    for port in result.ports:
        congestion_icon = {
            "clear": "🟢",
            "moderate": "🟡",
            "congested": "🔴",
            "closed": "⛔",
        }.get(port.congestion.value, "⚪")
        occupied = sum(1 for b in port.berths if b.occupied)
        total = len(port.berths)
        lines.append(
            f"- **{port.port_name}** ({port.locode}) "
            f"{congestion_icon} {port.congestion.value.capitalize()} | "
            f"Wait: {port.waiting_time_hours:.1f}h | "
            f"Berths: {occupied}/{total} occupied"
        )
        if port.notes:
            lines.append(f"  _{port.notes}_")

    return "\n".join(lines) + "\n"


def _format_weather_section(result) -> str:
    """Render the weather section of the report."""
    if result is None or not result.success:
        return "_Weather data unavailable._\n"
    if not result.conditions:
        return "_No weather data retrieved._\n"

    lines = []
    for cond in result.conditions:
        risk_icon = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🔴",
            "critical": "🆘",
        }.get(cond.risk_level.value, "⚪")
        warning_tag = " ⚠️ STORM WARNING" if cond.storm_warning else ""
        lines.append(
            f"- **{cond.location}** {risk_icon} {cond.risk_level.value.upper()}{warning_tag} | "
            f"Wind: {cond.wind_speed_knots:.0f} kts | "
            f"Wave: {cond.wave_height_meters:.1f} m | "
            f"Vis: {cond.visibility_km:.0f} km"
        )
        if cond.description:
            lines.append(f"  _{cond.description}_")

    return "\n".join(lines) + "\n"


# ── Main report builder ────────────────────────────────────────────────────────


def run_report_agent(inputs: DailyReportInput) -> DailyReport:
    """Build the daily maritime intelligence report from agent outputs.

    Args:
        inputs: Combined outputs from all specialist agents.

    Returns:
        A :class:`~models.report_models.DailyReport` with full Markdown content.
    """

    logger.info("ReportAgent: assembling daily report for %s", inputs.report_date)

    report_date = inputs.report_date or date.today()
    now = datetime.now(tz=timezone.utc)

    news_section = _format_news_section(inputs.news_result)
    ais_section = _format_ais_section(inputs.ais_result)
    port_section = _format_port_section(inputs.port_result)
    weather_section = _format_weather_section(inputs.weather_result)

    high_risk_weather = (
        inputs.weather_result.high_risk_locations if inputs.weather_result else []
    )
    vessel_alerts = (
        len(inputs.ais_result.alerts) if inputs.ais_result and inputs.ais_result.success else 0
    )
    congested_ports = (
        [
            p.port_name
            for p in inputs.port_result.ports
            if p.congestion.value in ("congested", "closed")
        ]
        if inputs.port_result and inputs.port_result.success
        else []
    )

    # Build executive summary
    exec_summary_parts = []
    if vessel_alerts:
        exec_summary_parts.append(f"**{vessel_alerts} vessel alert(s)** detected.")
    if congested_ports:
        exec_summary_parts.append(
            f"**Congested ports:** {', '.join(congested_ports)}."
        )
    if high_risk_weather:
        exec_summary_parts.append(
            f"**High-risk weather regions:** {', '.join(high_risk_weather)}."
        )
    if not exec_summary_parts:
        exec_summary_parts.append("No significant incidents reported.")

    exec_summary = "  \n".join(exec_summary_parts)

    markdown = (
        f"# Daily Maritime Intelligence Report\n"
        f"**Date:** {report_date.strftime('%B %d, %Y')}\n"
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"\n---\n\n"
        f"## Executive Summary\n"
        f"{exec_summary}\n"
        f"\n---\n\n"
        f"## \U0001f4f0 Maritime News\n"
        f"{news_section}\n"
        f"---\n\n"
        f"## \U0001f6a2 Vessel & AIS Status\n"
        f"{ais_section}\n"
        f"---\n\n"
        f"## \U0001f3ed Port Conditions\n"
        f"{port_section}\n"
        f"---\n\n"
        f"## \U0001f30a Weather Conditions\n"
        f"{weather_section}\n"
        f"---\n\n"
        f"*Report generated by Maritime Agents v0.1.0*\n"
    )

    return DailyReport(
        report_id=str(uuid.uuid4()),
        report_date=report_date,
        generated_at=now,
        markdown_content=markdown,
        news_summary=news_section,
        ais_summary=ais_section,
        port_summary=port_section,
        weather_summary=weather_section,
    )
