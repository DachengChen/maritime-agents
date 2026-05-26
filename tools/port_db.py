"""Mock port database tool.

TODO: Replace the mock implementation with a real port operations data source.
      This could be:
        - A SQLAlchemy query against an internal port-ops database.
        - A REST API call to a port community system (PCS).

      Set PORT_DB_URL in your .env file and implement the real query below.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from models.maritime_models import BerthStatus, PortCongestion, PortStatus


def fetch_port_status(
    port_locodes: Optional[list[str]] = None,
    db_url: Optional[str] = None,
) -> list[PortStatus]:
    """Return current status information for monitored ports.

    Currently returns mock data.  Replace with real database queries::

        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT * FROM port_status WHERE locode = ANY(:locodes)"),
                {"locodes": port_locodes},
            ).fetchall()
            return [PortStatus(**dict(row._mapping)) for row in rows]
    """

    now = datetime.now(tz=timezone.utc)

    # ── MOCK DATA ──────────────────────────────────────────────────────────────
    ports = [
        PortStatus(
            port_name="Port of Rotterdam",
            locode="NLRTM",
            congestion=PortCongestion.MODERATE,
            waiting_time_hours=4.5,
            berths=[
                BerthStatus(
                    berth_id="RTM-B01",
                    port_name="Port of Rotterdam",
                    occupied=True,
                    vessel_name="MV OCEAN STAR",
                    expected_departure=now + timedelta(hours=6),
                ),
                BerthStatus(
                    berth_id="RTM-B02",
                    port_name="Port of Rotterdam",
                    occupied=False,
                ),
            ],
            notes="Gate extension in effect; truck queue reduced.",
            last_update=now,
        ),
        PortStatus(
            port_name="Port of Singapore",
            locode="SGSIN",
            congestion=PortCongestion.CONGESTED,
            waiting_time_hours=18.0,
            berths=[
                BerthStatus(
                    berth_id="SIN-T1-B01",
                    port_name="Port of Singapore",
                    occupied=True,
                    vessel_name="MV PACIFIC TRADE",
                    expected_departure=now + timedelta(hours=10),
                ),
                BerthStatus(
                    berth_id="SIN-T1-B02",
                    port_name="Port of Singapore",
                    occupied=True,
                    vessel_name="MT SOUTHERN CROSS",
                    expected_departure=now + timedelta(hours=3),
                ),
            ],
            notes="High congestion due to increased VLCC calls.",
            last_update=now,
        ),
        PortStatus(
            port_name="Port of New Orleans",
            locode="USMSY",
            congestion=PortCongestion.MODERATE,
            waiting_time_hours=6.0,
            berths=[
                BerthStatus(
                    berth_id="MSY-B01",
                    port_name="Port of New Orleans",
                    occupied=True,
                    vessel_name="MV ATLAS PIONEER",
                    expected_departure=now + timedelta(hours=24),
                ),
            ],
            notes="Storm advisory in effect; some operations delayed.",
            last_update=now,
        ),
        PortStatus(
            port_name="Port of Hamburg",
            locode="DEHAM",
            congestion=PortCongestion.CLEAR,
            waiting_time_hours=1.0,
            berths=[
                BerthStatus(
                    berth_id="HAM-B01",
                    port_name="Port of Hamburg",
                    occupied=False,
                ),
                BerthStatus(
                    berth_id="HAM-B02",
                    port_name="Port of Hamburg",
                    occupied=False,
                ),
            ],
            notes=None,
            last_update=now,
        ),
    ]

    if port_locodes:
        ports = [p for p in ports if p.locode in port_locodes]

    return ports
