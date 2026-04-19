from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MedApp EMG API"
    database_url: str = "postgresql://medapp:medapp@localhost:5432/medapp"
    secret_key: str = "change-me-in-production-use-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    allow_registration: bool = False
    seed_doctor_email: str | None = None
    seed_doctor_password: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
