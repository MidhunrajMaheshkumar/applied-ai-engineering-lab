from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Task Management Microservice"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Async PostgreSQL connection string using asyncpg driver
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgrespassword@localhost:5433/core_db"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()