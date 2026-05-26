"""Weather Agent – fetches meteorological data and assesses maritime risk."""

from __future__ import annotations

import logging
from typing import Optional

from models.maritime_models import WeatherRisk
from models.report_models import WeatherAgentResult
from tools.weather_api import fetch_weather_conditions

logger = logging.getLogger(__name__)


def run_weather_agent(
    locations: Optional[list[dict]] = None,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
) -> WeatherAgentResult:
    """Execute the Weather Agent and return structured results.

    Args:
        locations: Optional list of ``{"name": ..., "lat": ..., "lon": ...}``
                   dicts specifying the locations to check.  Defaults to a set
                   of predefined key maritime regions.
        api_key:   Weather API key (falls back to mock data if not provided).
        api_url:   Base URL of the weather provider.

    Returns:
        A :class:`~models.report_models.WeatherAgentResult` with conditions
        and a list of high-risk location names, or an error description.
    """

    logger.info("WeatherAgent: fetching weather conditions")

    try:
        conditions = fetch_weather_conditions(
            locations=locations,
            api_key=api_key,
            api_url=api_url,
        )
        logger.info("WeatherAgent: received %d location snapshots", len(conditions))

        high_risk = [
            c.location
            for c in conditions
            if c.risk_level in (WeatherRisk.HIGH, WeatherRisk.CRITICAL)
        ]
        if high_risk:
            logger.warning("WeatherAgent: high-risk locations detected: %s", high_risk)

        return WeatherAgentResult(
            success=True,
            conditions=conditions,
            high_risk_locations=high_risk,
        )

    except Exception as exc:  # noqa: BLE001
        logger.exception("WeatherAgent: unexpected error")
        return WeatherAgentResult(success=False, error=str(exc))
