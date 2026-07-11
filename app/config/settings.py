from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime configuration for the application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CODE_REVIEW_",
        extra="ignore",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL of the local Ollama server.",
    )

    ollama_model: str = Field(
        default="qwen2.5-coder:3b",
        min_length=1,
        description="Ollama model used for AI code review.",
    )

    ollama_timeout_seconds: float = Field(
        default=120.0,
        gt=0,
        description="Maximum time allowed for one Ollama request.",
    )

    max_source_lines: int = Field(
        default=500,
        ge=1,
        description="Maximum number of source-code lines accepted.",
    )

    max_prompt_findings: int = Field(
        default=50,
        ge=1,
        description="Maximum findings included in an LLM prompt.",
    )

    allow_external_api: bool = Field(
        default=False,
        description=("Whether user code may be transmitted to an external API."),
    )

    log_level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Application logging level.",
    )


@lru_cache
def get_settings() -> Settings:
    """Return one cached Settings instance for the application."""

    return Settings()
