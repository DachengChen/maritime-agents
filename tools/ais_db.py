"""Mock AIS / vessel database tool.

TODO: Replace the mock implementation with a real AIS data source.
      Options include:
        - MarineTraffic API  (https://www.marinetraffic.com/en/ais-api-services)
        - VesselFinder API
        - An internal SQLAlchemy model that queries a live AIS feed database.

      Set AIS_API_KEY and AIS_API_URL in your .env file and implement the real
      query inside ``fetch_vessel_data``.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from models.maritime_models import VesselAlert, VesselInfo, VesselStatus


def fetch_vessel_data(
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
) -> list[VesselInfo]:
    """Return a list of vessel snapshots from AIS.

    Currently returns mock data.  Replace with a real API/DB query::

        import httpx
        response = httpx.get(
            f"{api_url}/exportvessels/v:8",
            params={"v": 8, "apikey": api_key},
            timeout=15,
        )
        response.raise_for_status()
        # parse and return VesselInfo objects

    SQLAlchemy example::

        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM ais_positions")).fetchall()
            return [VesselInfo(**dict(row._mapping)) for row in rows]
    """

    now = datetime.now(tz=timezone.utc)

    # ── MOCK DATA ──────────────────────────────────────────────────────────────
    return [
        VesselInfo(
            mmsi="123456789",
            name="MV OCEAN STAR",
            flag="LR",
            vessel_type="Container Ship",
            speed_knots=14.2,
            latitude=51.9,
            longitude=4.1,
            destination="NLRTM",
            eta=now + timedelta(hours=6),
            status=VesselStatus.ON_SCHEDULE,
        ),
        VesselInfo(
            mmsi="987654321",
            name="MV ATLAS PIONEER",
            flag="PA",
            vessel_type="Bulk Carrier",
            speed_knots=2.1,  # abnormally slow
            latitude=29.5,
            longitude=-89.0,
            destination="USMSY",
            eta=now + timedelta(hours=20),
            status=VesselStatus.DELAYED,
        ),
        VesselInfo(
            mmsi="555000111",
            name="MT GULF TRADER",
            flag="BS",
            vessel_type="Tanker",
            speed_knots=0.0,
            latitude=25.8,
            longitude=55.0,
            destination="AEJEA",
            eta=now + timedelta(hours=12),
            status=VesselStatus.ANCHORED,
        ),
        VesselInfo(
            mmsi="444222333",
            name="MV NORDIC HORIZON",
            flag="NO",
            vessel_type="Container Ship",
            speed_knots=22.5,  # abnormally fast
            latitude=57.0,
            longitude=10.5,
            destination="DEHAM",
            eta=now + timedelta(hours=8),
            status=VesselStatus.ABNORMAL_SPEED,
        ),
    ]


def detect_vessel_alerts(vessels: list[VesselInfo]) -> list[VesselAlert]:
    """Analyse vessel data and return a list of operational alerts."""

    alerts: list[VesselAlert] = []
    now = datetime.now(tz=timezone.utc)

    for vessel in vessels:
        # Delayed arrival
        if vessel.status == VesselStatus.DELAYED:
            alerts.append(
                VesselAlert(
                    vessel=vessel,
                    alert_type="DELAYED_ARRIVAL",
                    description=(
                        f"{vessel.name} is delayed en route to "
                        f"{vessel.destination or 'unknown destination'}."
                    ),
                    severity="medium",
                    detected_at=now,
                )
            )

        # Abnormal speed
        if vessel.status == VesselStatus.ABNORMAL_SPEED or vessel.speed_knots > 20:
            alerts.append(
                VesselAlert(
                    vessel=vessel,
                    alert_type="ABNORMAL_SPEED",
                    description=(
                        f"{vessel.name} is operating at an unusual speed of "
                        f"{vessel.speed_knots:.1f} knots."
                    ),
                    severity="low",
                    detected_at=now,
                )
            )

        # Long anchor
        if vessel.status == VesselStatus.ANCHORED:
            alerts.append(
                VesselAlert(
                    vessel=vessel,
                    alert_type="VESSEL_ANCHORED",
                    description=f"{vessel.name} is anchored near {vessel.destination or 'N/A'}.",
                    severity="low",
                    detected_at=now,
                )
            )

        # ETA overdue (ETA in the past)
        if vessel.eta and vessel.eta < now and vessel.status != VesselStatus.ON_SCHEDULE:
            alerts.append(
                VesselAlert(
                    vessel=vessel,
                    alert_type="ETA_OVERDUE",
                    description=(
                        f"{vessel.name} has missed its ETA of "
                        f"{vessel.eta.strftime('%Y-%m-%d %H:%M')} UTC."
                    ),
                    severity="high",
                    detected_at=now,
                )
            )

    return alerts
