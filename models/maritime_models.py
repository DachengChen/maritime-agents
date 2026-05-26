"""Pydantic models shared across the maritime domain."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class VesselStatus(str, Enum):
    """Operational status of a vessel."""

    ON_SCHEDULE = "on_schedule"
    DELAYED = "delayed"
    ANCHORED = "anchored"
    ABNORMAL_SPEED = "abnormal_speed"
    UNKNOWN = "unknown"


class WeatherRisk(str, Enum):
    """Risk level derived from weather conditions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PortCongestion(str, Enum):
    """Current congestion state of a port."""

    CLEAR = "clear"
    MODERATE = "moderate"
    CONGESTED = "congested"
    CLOSED = "closed"


# ─── Vessel / AIS ─────────────────────────────────────────────────────────────


class VesselInfo(BaseModel):
    """Basic AIS data for a single vessel."""

    mmsi: str = Field(..., description="Maritime Mobile Service Identity")
    name: str
    flag: Optional[str] = None
    vessel_type: Optional[str] = None
    speed_knots: float = Field(0.0, ge=0)
    latitude: float
    longitude: float
    destination: Optional[str] = None
    eta: Optional[datetime] = None
    status: VesselStatus = VesselStatus.UNKNOWN
    last_update: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


class VesselAlert(BaseModel):
    """An alert generated for an anomalous vessel event."""

    vessel: VesselInfo
    alert_type: str
    description: str
    severity: str = "medium"
    detected_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


# ─── Port ─────────────────────────────────────────────────────────────────────


class BerthStatus(BaseModel):
    """Availability status of a single berth."""

    berth_id: str
    port_name: str
    occupied: bool
    vessel_name: Optional[str] = None
    expected_departure: Optional[datetime] = None


class PortStatus(BaseModel):
    """Aggregated status for a port."""

    port_name: str
    locode: str = Field(..., description="UN/LOCODE identifier")
    congestion: PortCongestion = PortCongestion.CLEAR
    waiting_time_hours: float = Field(0.0, ge=0)
    berths: list[BerthStatus] = Field(default_factory=list)
    notes: Optional[str] = None
    last_update: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


# ─── Weather ──────────────────────────────────────────────────────────────────


class WeatherCondition(BaseModel):
    """Meteorological snapshot for a geographic location."""

    location: str
    latitude: float
    longitude: float
    wind_speed_knots: float = Field(0.0, ge=0)
    wave_height_meters: float = Field(0.0, ge=0)
    visibility_km: float = Field(ge=0, default=10.0)
    storm_warning: bool = False
    risk_level: WeatherRisk = WeatherRisk.LOW
    description: Optional[str] = None
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


# ─── News ─────────────────────────────────────────────────────────────────────


class NewsItem(BaseModel):
    """A single news article relevant to maritime operations."""

    title: str
    source: str
    url: Optional[str] = None
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    keywords: list[str] = Field(default_factory=list)
