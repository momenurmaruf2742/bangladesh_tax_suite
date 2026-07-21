from typing import List
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    PROJECT_NAME: str = "Bangladesh Tax Suite"
    API_V1_STR: str = "/api/v1"

    # POSTGRES
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "tax_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        # Use asyncpg for async SQLModel/SQLAlchemy
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field
    @property
    def SYNC_DATABASE_URL(self) -> str:
        # For migration/alembic tools that run synchronously
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # REDIS
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # JWT SECURITY
    # In production, change this secret!
    JWT_SECRET_KEY: str = "supersecretaccesskeyforbangladeshtaxsuite2026!!!"
    JWT_REFRESH_SECRET_KEY: str = "supersecretrefreshkeyforbangladeshtaxsuite2026!!!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]


settings = Settings()
