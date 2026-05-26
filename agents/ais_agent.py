"""AIS Agent – checks vessel positions, speeds, and ETA anomalies."""

from __future__ import annotations

import logging

from models.report_models import AISAgentResult
from tools.ais_db import detect_vessel_alerts, fetch_vessel_data

logger = logging.getLogger(__name__)


def run_ais_agent(
    api_key: str | None = None,
    api_url: str | None = None,
) -> AISAgentResult:
    """Execute the AIS Agent and return structured results.

    The agent:
    1. Fetches current vessel positions from the AIS tool.
    2. Passes the snapshot through the anomaly-detection logic.
    3. Returns all generated alerts.

    Args:
        api_key: AIS provider API key (falls back to mock data if not provided).
        api_url: Base URL of the AIS provider.

    Returns:
        A :class:`~models.report_models.AISAgentResult` with any detected
        vessel alerts or an error description.
    """

    logger.info("AISAgent: fetching vessel data")

    try:
        vessels = fetch_vessel_data(api_key=api_key, api_url=api_url)
        logger.info("AISAgent: %d vessels loaded", len(vessels))

        alerts = detect_vessel_alerts(vessels)
        logger.info("AISAgent: %d alerts detected", len(alerts))

        return AISAgentResult(
            success=True,
            alerts=alerts,
            total_vessels_checked=len(vessels),
        )

    except Exception as exc:  # noqa: BLE001
        logger.exception("AISAgent: unexpected error")
        return AISAgentResult(success=False, error=str(exc))
