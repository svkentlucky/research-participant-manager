from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://rpm_user:rpm_password@localhost:5432/rpm_db"
    test_database_url: str = "postgresql+asyncpg://rpm_user:rpm_password@localhost:5433/rpm_db_test"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
