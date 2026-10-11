from functools import lru_cache
from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

if TYPE_CHECKING:
    from app.core.llm import GemmaLLM


class Settings(BaseSettings):
    """Reads real environment variables first, then a local `.env` file (dev only).

    In production there is no .env in the image: docker compose injects these variables
    (non-secret values from deploy/env/prod.env, secrets from AWS Secrets Manager).
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "chatbot"
    log_level: str = "INFO"

    # MySQL parts (preferred): the password is URL-escaped for you
    mysql_host: str = ""
    mysql_port: int = 3306
    mysql_database: str = "chatbot"
    mysql_user: str = "chatbot"
    mysql_password: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemma-4-26b-a4b-it"
    # Full URL override, e.g. for tests or another DB
    database_url: str = ""

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.mysql_host:
            return URL.create(
                "mysql+pymysql",
                username=self.mysql_user,
                password=self.mysql_password,
                host=self.mysql_host,
                port=self.mysql_port,
                database=self.mysql_database,
            ).render_as_string(hide_password=False)
        return "sqlite:///./dev.db"


settings = Settings()


@lru_cache
def get_model() -> "GemmaLLM":
    """Chat model built from settings (GEMINI_MODEL / GEMINI_API_KEY)."""
    from app.core.llm import GemmaLLM  # lazy: keeps langchain out of plain config imports

    return GemmaLLM(model=settings.gemini_model, api_key=settings.gemini_api_key)
