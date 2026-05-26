"""Mock Weather API tool.

TODO: Replace the mock implementation with a real weather data provider.
      Good options include:
        - OpenWeatherMap Marine API
        - StormGlass API (https://stormglass.io)
        - NOAA / Copernicus Marine Services

      Set WEATHER_API_KEY and WEATHER_API_URL in your .env file and implement
      the real call inside ``fetch_weather_conditions``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from models.maritime_models import WeatherCondition, WeatherRisk


def _classify_risk(
    wind_speed_knots: float,
    wave_height_meters: float,
    storm_warning: bool,
) -> WeatherRisk:
    """Derive a risk level from meteorological parameters."""

    if storm_warning or wind_speed_knots >= 48 or wave_height_meters >= 6:
        return WeatherRisk.CRITICAL
    if wind_speed_knots >= 34 or wave_height_meters >= 4:
        return WeatherRisk.HIGH
    if wind_speed_knots >= 17 or wave_height_meters >= 2:
        return WeatherRisk.MEDIUM
    return WeatherRisk.LOW


def fetch_weather_conditions(
    locations: Optional[list[dict]] = None,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
) -> list[WeatherCondition]:
    """Return weather conditions for key maritime locations.

    The ``locations`` parameter is a list of dicts with keys
    ``name``, ``lat``, and ``lon``.

    Currently returns mock data.  Replace with a real API call, e.g.::

        import httpx
        results = []
        for loc in locations:
            resp = httpx.get(
                f"{api_url}/weather",
                params={"lat": loc["lat"], "lon": loc["lon"], "appid": api_key},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            wind_knots = data["wind"]["speed"] * 1.944  # m/s → knots
            results.append(WeatherCondition(
                location=loc["name"],
                latitude=loc["lat"],
                longitude=loc["lon"],
                wind_speed_knots=wind_knots,
                wave_height_meters=data.get("waves", {}).get("height", 0),
                storm_warning="Thunderstorm" in data["weather"][0]["main"],
                risk_level=_classify_risk(wind_knots, 0, False),
                description=data["weather"][0]["description"],
            ))
        return results
    """

    now = datetime.now(tz=timezone.utc)

    # ── MOCK DATA ──────────────────────────────────────────────────────────────
    raw = [
        {
            "location": "North Sea",
            "latitude": 56.0,
            "longitude": 3.0,
            "wind_speed_knots": 22.0,
            "wave_height_meters": 2.5,
            "visibility_km": 8.0,
            "storm_warning": False,
            "description": "Moderate swell, gusty winds",
        },
        {
            "location": "Gulf of Mexico",
            "latitude": 25.0,
            "longitude": -90.0,
            "wind_speed_knots": 52.0,
            "wave_height_meters": 7.0,
            "visibility_km": 2.0,
            "storm_warning": True,
            "description": "Tropical storm conditions; gale-force winds and heavy swell",
        },
        {
            "location": "Strait of Malacca",
            "latitude": 2.5,
            "longitude": 101.0,
            "wind_speed_knots": 10.0,
            "wave_height_meters": 0.8,
            "visibility_km": 12.0,
            "storm_warning": False,
            "description": "Calm seas, light winds",
        },
        {
            "location": "English Channel",
            "latitude": 50.5,
            "longitude": 1.0,
            "wind_speed_knots": 18.0,
            "wave_height_meters": 1.5,
            "visibility_km": 10.0,
            "storm_warning": False,
            "description": "Fresh breeze, slight swell",
        },
        {
            "location": "Suez Canal approaches",
            "latitude": 29.9,
            "longitude": 32.5,
            "wind_speed_knots": 8.0,
            "wave_height_meters": 0.5,
            "visibility_km": 15.0,
            "storm_warning": False,
            "description": "Clear conditions",
        },
    ]

    conditions = []
    for entry in raw:
        risk = _classify_risk(
            entry["wind_speed_knots"],
            entry["wave_height_meters"],
            entry["storm_warning"],
        )
        conditions.append(
            WeatherCondition(
                location=entry["location"],
                latitude=entry["latitude"],
                longitude=entry["longitude"],
                wind_speed_knots=entry["wind_speed_knots"],
                wave_height_meters=entry["wave_height_meters"],
                visibility_km=entry["visibility_km"],
                storm_warning=entry["storm_warning"],
                risk_level=risk,
                description=entry["description"],
                recorded_at=now,
            )
        )

    return conditions
