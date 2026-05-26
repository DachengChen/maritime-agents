"""Tests for the daily report workflow and individual agent functions."""

from __future__ import annotations

import pytest
from datetime import date, datetime, timezone

from models.maritime_models import (
    NewsItem,
    PortCongestion,
    PortStatus,
    VesselAlert,
    VesselInfo,
    VesselStatus,
    WeatherCondition,
    WeatherRisk,
)
from models.report_models import (
    AISAgentResult,
    DailyReport,
    DailyReportInput,
    NewsAgentResult,
    PortAgentResult,
    WeatherAgentResult,
)


# ── Model tests ────────────────────────────────────────────────────────────────


class TestMaritimeModels:
    def test_vessel_info_defaults(self):
        vessel = VesselInfo(
            mmsi="123456789",
            name="MV TEST",
            speed_knots=10.0,
            latitude=51.0,
            longitude=4.0,
        )
        assert vessel.status == VesselStatus.UNKNOWN
        assert vessel.speed_knots == 10.0

    def test_port_status_defaults(self):
        port = PortStatus(port_name="Test Port", locode="TSTPT")
        assert port.congestion == PortCongestion.CLEAR
        assert port.waiting_time_hours == 0.0
        assert port.berths == []

    def test_weather_condition_risk_classification(self):
        from tools.weather_api import _classify_risk

        assert _classify_risk(5.0, 0.5, False) == WeatherRisk.LOW
        assert _classify_risk(20.0, 2.5, False) == WeatherRisk.MEDIUM
        assert _classify_risk(35.0, 4.5, False) == WeatherRisk.HIGH
        assert _classify_risk(50.0, 7.0, True) == WeatherRisk.CRITICAL

    def test_news_item_optional_fields(self):
        item = NewsItem(title="Test Headline", source="Test Source")
        assert item.url is None
        assert item.summary is None
        assert item.keywords == []


# ── Tool tests ─────────────────────────────────────────────────────────────────


class TestTools:
    def test_fetch_maritime_news_returns_items(self):
        from tools.news_api import fetch_maritime_news

        articles = fetch_maritime_news(max_results=3)
        assert len(articles) <= 3
        assert all(isinstance(a, NewsItem) for a in articles)

    def test_fetch_maritime_news_titles_non_empty(self):
        from tools.news_api import fetch_maritime_news

        articles = fetch_maritime_news()
        assert all(a.title for a in articles)

    def test_fetch_vessel_data_returns_vessels(self):
        from tools.ais_db import fetch_vessel_data

        vessels = fetch_vessel_data()
        assert len(vessels) > 0
        assert all(isinstance(v, VesselInfo) for v in vessels)

    def test_detect_vessel_alerts_finds_delayed(self):
        from tools.ais_db import detect_vessel_alerts

        vessel = VesselInfo(
            mmsi="111",
            name="MV DELAY",
            speed_knots=3.0,
            latitude=0.0,
            longitude=0.0,
            status=VesselStatus.DELAYED,
        )
        alerts = detect_vessel_alerts([vessel])
        types = [a.alert_type for a in alerts]
        assert "DELAYED_ARRIVAL" in types

    def test_detect_vessel_alerts_finds_abnormal_speed(self):
        from tools.ais_db import detect_vessel_alerts

        vessel = VesselInfo(
            mmsi="222",
            name="MV FAST",
            speed_knots=25.0,
            latitude=0.0,
            longitude=0.0,
            status=VesselStatus.ABNORMAL_SPEED,
        )
        alerts = detect_vessel_alerts([vessel])
        types = [a.alert_type for a in alerts]
        assert "ABNORMAL_SPEED" in types

    def test_detect_vessel_alerts_empty_for_normal(self):
        from tools.ais_db import detect_vessel_alerts

        vessel = VesselInfo(
            mmsi="333",
            name="MV NORMAL",
            speed_knots=12.0,
            latitude=0.0,
            longitude=0.0,
            status=VesselStatus.ON_SCHEDULE,
        )
        alerts = detect_vessel_alerts([vessel])
        assert alerts == []

    def test_fetch_port_status_returns_ports(self):
        from tools.port_db import fetch_port_status

        ports = fetch_port_status()
        assert len(ports) > 0
        assert all(isinstance(p, PortStatus) for p in ports)

    def test_fetch_port_status_filter_by_locode(self):
        from tools.port_db import fetch_port_status

        ports = fetch_port_status(port_locodes=["NLRTM"])
        assert len(ports) == 1
        assert ports[0].locode == "NLRTM"

    def test_fetch_weather_conditions_returns_data(self):
        from tools.weather_api import fetch_weather_conditions

        conditions = fetch_weather_conditions()
        assert len(conditions) > 0
        assert all(isinstance(c, WeatherCondition) for c in conditions)

    def test_fetch_weather_storm_location_critical(self):
        from tools.weather_api import fetch_weather_conditions

        conditions = fetch_weather_conditions()
        gulf = next((c for c in conditions if "Gulf" in c.location), None)
        assert gulf is not None
        assert gulf.storm_warning is True
        assert gulf.risk_level == WeatherRisk.CRITICAL


# ── Agent tests ────────────────────────────────────────────────────────────────


class TestAgents:
    def test_news_agent_success(self):
        from agents.news_agent import run_news_agent

        result = run_news_agent()
        assert result.success is True
        assert len(result.articles) > 0
        assert result.error is None

    def test_ais_agent_success(self):
        from agents.ais_agent import run_ais_agent

        result = run_ais_agent()
        assert result.success is True
        assert result.total_vessels_checked > 0
        assert result.error is None

    def test_ais_agent_detects_alerts(self):
        from agents.ais_agent import run_ais_agent

        result = run_ais_agent()
        # Mock data contains delayed / anchored / fast vessels
        assert len(result.alerts) > 0

    def test_port_agent_success(self):
        from agents.port_agent import run_port_agent

        result = run_port_agent()
        assert result.success is True
        assert len(result.ports) > 0

    def test_weather_agent_success(self):
        from agents.weather_agent import run_weather_agent

        result = run_weather_agent()
        assert result.success is True
        assert len(result.conditions) > 0

    def test_weather_agent_high_risk_detection(self):
        from agents.weather_agent import run_weather_agent

        result = run_weather_agent()
        # Gulf of Mexico should appear in mock high-risk locations
        assert len(result.high_risk_locations) > 0

    def test_report_agent_generates_markdown(self):
        from agents.report_agent import run_report_agent
        from agents.news_agent import run_news_agent
        from agents.ais_agent import run_ais_agent
        from agents.port_agent import run_port_agent
        from agents.weather_agent import run_weather_agent

        inputs = DailyReportInput(
            news_result=run_news_agent(),
            ais_result=run_ais_agent(),
            port_result=run_port_agent(),
            weather_result=run_weather_agent(),
        )
        report = run_report_agent(inputs)
        assert isinstance(report, DailyReport)
        assert report.markdown_content.startswith("# Daily Maritime Intelligence Report")
        assert report.report_id  # non-empty UUID

    def test_report_agent_handles_missing_results(self):
        from agents.report_agent import run_report_agent

        inputs = DailyReportInput()  # All agent results are None
        report = run_report_agent(inputs)
        assert isinstance(report, DailyReport)
        assert "unavailable" in report.markdown_content.lower()

    def test_supervisor_agent_returns_report(self):
        from agents.supervisor_agent import run_supervisor

        report = run_supervisor()
        assert isinstance(report, DailyReport)
        assert report.report_id
        assert "Daily Maritime Intelligence Report" in report.markdown_content


# ── Workflow tests ─────────────────────────────────────────────────────────────


class TestDailyReportWorkflow:
    def test_workflow_builds(self):
        from workflows.daily_report_workflow import build_workflow

        graph = build_workflow()
        assert graph is not None

    def test_workflow_invoke_returns_report(self):
        from workflows.daily_report_workflow import build_workflow, WorkflowState

        graph = build_workflow()
        result = graph.invoke(WorkflowState())
        assert "report" in result
        report = result["report"]
        assert isinstance(report, DailyReport)
        assert report.markdown_content

    def test_workflow_news_result_populated(self):
        from workflows.daily_report_workflow import build_workflow, WorkflowState

        graph = build_workflow()
        result = graph.invoke(WorkflowState())
        assert "news_result" in result
        assert result["news_result"].success is True

    def test_workflow_ais_result_populated(self):
        from workflows.daily_report_workflow import build_workflow, WorkflowState

        graph = build_workflow()
        result = graph.invoke(WorkflowState())
        assert "ais_result" in result
        assert result["ais_result"].success is True

    def test_workflow_port_result_populated(self):
        from workflows.daily_report_workflow import build_workflow, WorkflowState

        graph = build_workflow()
        result = graph.invoke(WorkflowState())
        assert "port_result" in result
        assert result["port_result"].success is True

    def test_workflow_weather_result_populated(self):
        from workflows.daily_report_workflow import build_workflow, WorkflowState

        graph = build_workflow()
        result = graph.invoke(WorkflowState())
        assert "weather_result" in result
        assert result["weather_result"].success is True

    def test_workflow_skips_email_when_not_requested(self):
        from workflows.daily_report_workflow import build_workflow, WorkflowState

        graph = build_workflow()
        result = graph.invoke(WorkflowState(send_email=False))
        report = result["report"]
        assert report.email_sent is False

    def test_workflow_email_dry_run(self):
        from workflows.daily_report_workflow import build_workflow, WorkflowState

        graph = build_workflow()
        result = graph.invoke(
            WorkflowState(
                send_email=True,
                email_recipients=["test@example.com"],
                email_dry_run=True,
            )
        )
        report = result["report"]
        # Dry-run should mark email_sent=True without real SMTP
        assert report.email_sent is True
        assert "test@example.com" in report.email_recipients


# ── Email tool tests ───────────────────────────────────────────────────────────


class TestEmailTool:
    def test_dry_run_returns_true(self):
        from tools.email_tool import send_report_email

        result = send_report_email(
            subject="Test",
            body_markdown="# Test\nHello",
            recipients=["a@example.com"],
            dry_run=True,
        )
        assert result is True

    def test_real_send_fails_without_smtp_host(self):
        from tools.email_tool import send_report_email

        result = send_report_email(
            subject="Test",
            body_markdown="# Test",
            recipients=["a@example.com"],
            smtp_host=None,
            dry_run=False,
        )
        assert result is False
