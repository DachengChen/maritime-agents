"""Daily Report Workflow – LangGraph-based orchestration.

This module implements the same daily maritime intelligence pipeline as the
supervisor agent, but expressed as a LangGraph ``StateGraph``.  Using a graph
enables:

- Visualisation of the pipeline as a directed graph.
- Future conditional branching (e.g. skip weather if no vessels at sea).
- Parallel fan-out with ``Send`` API for concurrent agent execution.
- Built-in retry / error handling nodes.

Usage::

    from workflows.daily_report_workflow import build_workflow, WorkflowState
    graph = build_workflow()
    result = graph.invoke(WorkflowState())
    print(result["report"].markdown_content)
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Annotated, Optional

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from agents.ais_agent import run_ais_agent
from agents.news_agent import run_news_agent
from agents.port_agent import run_port_agent
from agents.report_agent import run_report_agent
from agents.weather_agent import run_weather_agent
from models.report_models import (
    AISAgentResult,
    DailyReport,
    DailyReportInput,
    NewsAgentResult,
    PortAgentResult,
    WeatherAgentResult,
)
from tools.email_tool import send_report_email

logger = logging.getLogger(__name__)


# ── Graph State ────────────────────────────────────────────────────────────────


class WorkflowState(TypedDict, total=False):
    """Mutable state shared across all nodes in the workflow graph."""

    # Configuration (set before invoking the graph)
    report_date: Optional[date]
    send_email: bool
    email_recipients: list[str]
    email_dry_run: bool

    # API / DB credentials
    news_api_key: Optional[str]
    news_api_url: Optional[str]
    ais_api_key: Optional[str]
    ais_api_url: Optional[str]
    port_db_url: Optional[str]
    weather_api_key: Optional[str]
    weather_api_url: Optional[str]

    # SMTP credentials
    smtp_host: Optional[str]
    smtp_port: int
    smtp_user: Optional[str]
    smtp_password: Optional[str]
    email_sender: Optional[str]

    # Agent outputs (populated during execution)
    news_result: Optional[NewsAgentResult]
    ais_result: Optional[AISAgentResult]
    port_result: Optional[PortAgentResult]
    weather_result: Optional[WeatherAgentResult]

    # Final output
    report: Optional[DailyReport]


# ── Node functions ─────────────────────────────────────────────────────────────


def node_news(state: WorkflowState) -> dict:
    """Run the News Agent node."""
    result = run_news_agent(
        api_key=state.get("news_api_key"),
        api_url=state.get("news_api_url"),
    )
    return {"news_result": result}


def node_ais(state: WorkflowState) -> dict:
    """Run the AIS Agent node."""
    result = run_ais_agent(
        api_key=state.get("ais_api_key"),
        api_url=state.get("ais_api_url"),
    )
    return {"ais_result": result}


def node_port(state: WorkflowState) -> dict:
    """Run the Port Agent node."""
    result = run_port_agent(
        db_url=state.get("port_db_url"),
    )
    return {"port_result": result}


def node_weather(state: WorkflowState) -> dict:
    """Run the Weather Agent node."""
    result = run_weather_agent(
        api_key=state.get("weather_api_key"),
        api_url=state.get("weather_api_url"),
    )
    return {"weather_result": result}


def node_report(state: WorkflowState) -> dict:
    """Assemble the final report from all agent outputs."""
    inputs = DailyReportInput(
        report_date=state.get("report_date") or date.today(),
        news_result=state.get("news_result"),
        ais_result=state.get("ais_result"),
        port_result=state.get("port_result"),
        weather_result=state.get("weather_result"),
    )
    report = run_report_agent(inputs)
    return {"report": report}


def node_email(state: WorkflowState) -> dict:
    """Optionally send the finished report by email."""
    report: Optional[DailyReport] = state.get("report")
    if not report:
        logger.warning("EmailNode: no report found in state; skipping email.")
        return {}

    recipients: list[str] = state.get("email_recipients") or []
    if not recipients:
        logger.info("EmailNode: no recipients configured; skipping email.")
        return {}

    subject = f"{report.title} – {report.report_date.strftime('%Y-%m-%d')}"
    sent = send_report_email(
        subject=subject,
        body_markdown=report.markdown_content,
        recipients=recipients,
        smtp_host=state.get("smtp_host"),
        smtp_port=state.get("smtp_port") or 587,
        smtp_user=state.get("smtp_user"),
        smtp_password=state.get("smtp_password"),
        sender=state.get("email_sender"),
        dry_run=state.get("email_dry_run", True),
    )
    report.email_sent = sent
    if sent:
        report.email_recipients = recipients
    return {"report": report}


def _should_send_email(state: WorkflowState) -> str:
    """Routing function: branch to email node only when requested."""
    if state.get("send_email") and state.get("email_recipients"):
        return "send_email"
    return END


# ── Graph builder ──────────────────────────────────────────────────────────────


def build_workflow() -> StateGraph:
    """Construct and compile the daily report workflow graph.

    Graph topology::

        START
          ├─► node_news ──────────┐
          ├─► node_ais ───────────┤
          ├─► node_port ──────────┤► node_report ──► [email?] ──► END
          └─► node_weather ───────┘

    Note: LangGraph executes independent nodes sequentially by default.
    To run news / AIS / port / weather in parallel, wrap them in a
    ``langgraph.graph.Send`` fan-out when using the async API.

    Returns:
        A compiled :class:`langgraph.graph.StateGraph` ready to ``.invoke()``.
    """

    builder = StateGraph(WorkflowState)

    # Register nodes
    builder.add_node("news", node_news)
    builder.add_node("ais", node_ais)
    builder.add_node("port", node_port)
    builder.add_node("weather", node_weather)
    builder.add_node("report", node_report)
    builder.add_node("email", node_email)

    # Entry edges: run all data-collection agents after START
    builder.add_edge(START, "news")
    builder.add_edge(START, "ais")
    builder.add_edge(START, "port")
    builder.add_edge(START, "weather")

    # Converge on the report node once all agents finish
    builder.add_edge("news", "report")
    builder.add_edge("ais", "report")
    builder.add_edge("port", "report")
    builder.add_edge("weather", "report")

    # Conditional: send email or finish
    builder.add_conditional_edges("report", _should_send_email, {"send_email": "email", END: END})
    builder.add_edge("email", END)

    return builder.compile()
