from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    cors_origins: list[str] = ["http://localhost:5173"]
    database_path: Path = Path(__file__).resolve().parents[2] / "data" / "orders.sqlite3"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
