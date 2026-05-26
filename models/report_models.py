"""Pydantic models for the daily maritime intelligence report."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from models.maritime_models import (
    NewsItem,
    PortStatus,
    VesselAlert,
    WeatherCondition,
)


class AgentResult(BaseModel):
    """Generic wrapper for the output of a single agent run."""

    agent_name: str
    success: bool = True
    error: Optional[str] = None
    executed_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


class NewsAgentResult(AgentResult):
    """Output produced by the News Agent."""

    agent_name: str = "news_agent"
    articles: list[NewsItem] = Field(default_factory=list)


class AISAgentResult(AgentResult):
    """Output produced by the AIS Agent."""

    agent_name: str = "ais_agent"
    alerts: list[VesselAlert] = Field(default_factory=list)
    total_vessels_checked: int = 0


class PortAgentResult(AgentResult):
    """Output produced by the Port Agent."""

    agent_name: str = "port_agent"
    ports: list[PortStatus] = Field(default_factory=list)


class WeatherAgentResult(AgentResult):
    """Output produced by the Weather Agent."""

    agent_name: str = "weather_agent"
    conditions: list[WeatherCondition] = Field(default_factory=list)
    high_risk_locations: list[str] = Field(default_factory=list)


class DailyReportInput(BaseModel):
    """Aggregated inputs passed to the Report Agent."""

    report_date: date = Field(default_factory=date.today)
    news_result: Optional[NewsAgentResult] = None
    ais_result: Optional[AISAgentResult] = None
    port_result: Optional[PortAgentResult] = None
    weather_result: Optional[WeatherAgentResult] = None


class DailyReport(BaseModel):
    """The final daily maritime intelligence report."""

    report_id: str
    report_date: date
    generated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    title: str = "Daily Maritime Intelligence Report"
    markdown_content: str = ""
    news_summary: str = ""
    ais_summary: str = ""
    port_summary: str = ""
    weather_summary: str = ""
    email_sent: bool = False
    email_recipients: list[str] = Field(default_factory=list)
