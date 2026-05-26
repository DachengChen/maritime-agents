"""Application configuration via Pydantic Settings.

Values are read from environment variables and the `.env` file (if present).
All settings have sensible defaults so the application works out-of-the-box
with mock data; override them in `.env` for production use.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime settings for the maritime-agents application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # ── News API ───────────────────────────────────────────────────────────────
    # TODO: Set NEWS_API_KEY to your real News API key.
    news_api_key: Optional[str] = None
    news_api_url: str = "https://newsapi.org/v2/everything"

    # ── AIS API ────────────────────────────────────────────────────────────────
    # TODO: Set AIS_API_KEY to your real AIS provider key.
    ais_api_key: Optional[str] = None
    ais_api_url: str = "https://services.marinetraffic.com/api"

    # ── Port database ──────────────────────────────────────────────────────────
    # TODO: Set PORT_DB_URL to your real database connection string.
    port_db_url: str = "sqlite:///./maritime.db"

    # ── Weather API ────────────────────────────────────────────────────────────
    # TODO: Set WEATHER_API_KEY to your real weather API key.
    weather_api_key: Optional[str] = None
    weather_api_url: str = "https://api.openweathermap.org/data/2.5"

    # ── Email / SMTP ───────────────────────────────────────────────────────────
    # TODO: Configure SMTP settings for production report delivery.
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: str = "reports@maritime-agents.local"
    email_to: str = ""  # Comma-separated list of recipients

    # ── Report storage ─────────────────────────────────────────────────────────
    reports_dir: str = "./reports"

    @property
    def email_recipients(self) -> list[str]:
        """Parse the comma-separated EMAIL_TO value into a list."""
        return [addr.strip() for addr in self.email_to.split(",") if addr.strip()]

    @property
    def reports_path(self) -> Path:
        """Resolved Path object for the reports directory."""
        return Path(self.reports_dir).resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
