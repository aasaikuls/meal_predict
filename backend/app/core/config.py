from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_title: str = "Airline Meal Prediction API"
    app_version: str = "1.0.0"

    # Database
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "meal_user"
    mysql_password: str = "meal_password"
    mysql_database: str = "meal_prediction"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def sync_database_url(self) -> str:
        """Sync URL for Alembic migrations"""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    session_ttl_seconds: int = 86400  # 24 hours

    # LLM Provider — "kariba" or "bedrock"
    llm_provider: str = "kariba"

    # Kariba LLM
    kariba_api_url: str = (
        "https://api.nonprod.kariba.de.sin.auto2.nonprod.c0.sq.com.sg/api/v2/call-llm/"
    )
    kariba_model: str = "GPT5-mini"

    # AWS Bedrock
    bedrock_base_url: str = "https://bedrock-runtime.ap-southeast-1.amazonaws.com"
    bedrock_model: str = "apac.anthropic.claude-sonnet-4-20250514-v1:0"

    # Shared LLM token
    llm_user_token: str = ""

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
