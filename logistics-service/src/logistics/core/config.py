from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field
from functools import lru_cache
import os

class Settings(BaseSettings):
    """
    Application Settings.
    Validation is performed automatically by Pydantic.
    """
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True,
        extra="ignore"
    )

    # App Config
    APP_NAME: str = "Logistics Service"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Database Config
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # Database Pool Settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg", # Using asyncpg for high-throughput async SQLAlchemy
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def SQLALCHEMY_TEST_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host="db_test" if os.getenv("DOCKER_ENV") else "localhost",
            port=5433 if not os.getenv("DOCKER_ENV") else 5432,
            path=f"{self.POSTGRES_DB}_test",
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()