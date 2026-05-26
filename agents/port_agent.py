"""Port Agent – checks port congestion, berth availability, and waiting times."""

from __future__ import annotations

import logging
from typing import Optional

from models.report_models import PortAgentResult
from tools.port_db import fetch_port_status

logger = logging.getLogger(__name__)


def run_port_agent(
    port_locodes: Optional[list[str]] = None,
    db_url: Optional[str] = None,
) -> PortAgentResult:
    """Execute the Port Agent and return structured results.

    Args:
        port_locodes: Optional list of UN/LOCODE identifiers to filter ports.
                      Defaults to all monitored ports.
        db_url:       SQLAlchemy-compatible database URL for port data.

    Returns:
        A :class:`~models.report_models.PortAgentResult` with current port
        statuses or an error description.
    """

    logger.info(
        "PortAgent: fetching port status (locodes=%s)",
        port_locodes or "all",
    )

    try:
        ports = fetch_port_status(port_locodes=port_locodes, db_url=db_url)
        logger.info("PortAgent: retrieved status for %d ports", len(ports))
        return PortAgentResult(success=True, ports=ports)

    except Exception as exc:  # noqa: BLE001
        logger.exception("PortAgent: unexpected error")
        return PortAgentResult(success=False, error=str(exc))
