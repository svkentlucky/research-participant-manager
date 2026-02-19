from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://rpm_user:rpm_password@localhost:5434/rpm_db"
    test_database_url: str = "postgresql+asyncpg://rpm_user:rpm_password@localhost:5435/rpm_db_test"
    debug: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert postgresql:// to postgresql+asyncpg:// for Railway/Render
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
