from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "maritime-agent-saas"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/maritime_agent_saas"

    email_delivery_mode: str = "mock"
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = False
    smtp_sender: str = "reports@maritime-agent-saas.local"

    default_report_language: str = "en"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
