import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def test_settings_use_expected_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.ollama_model == "qwen2.5-coder:3b"
    assert settings.ollama_timeout_seconds == 120.0
    assert settings.max_source_lines == 500
    assert settings.max_prompt_findings == 50
    assert settings.allow_external_api is False
    assert settings.log_level == "INFO"


def test_settings_load_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CODE_REVIEW_OLLAMA_MODEL",
        "qwen2.5-coder:7b",
    )
    monkeypatch.setenv(
        "CODE_REVIEW_MAX_PROMPT_FINDINGS",
        "25",
    )

    settings = Settings(_env_file=None)

    assert settings.ollama_model == "qwen2.5-coder:7b"
    assert settings.max_prompt_findings == 25


def test_settings_reject_invalid_timeout() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            ollama_timeout_seconds=0,
        )


def test_settings_reject_invalid_log_level() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            log_level="VERBOSE",
        )
