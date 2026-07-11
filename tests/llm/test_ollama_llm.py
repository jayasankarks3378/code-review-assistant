from unittest.mock import Mock, patch

import pytest
import requests

from app.exceptions import LLMGenerationError
from app.llm.ollama_llm import OllamaLLM


def test_generate_returns_ollama_response_text() -> None:
    fake_http_response = Mock()
    fake_http_response.status_code = 200
    fake_http_response.json.return_value = {
        "response": '{"summary": "Review complete.", "comments": []}',
        "done": True,
    }

    with patch(
        "app.llm.ollama_llm.requests.post",
        return_value=fake_http_response,
    ) as mocked_post:
        llm = OllamaLLM(
            base_url="http://localhost:11434",
            model="qwen2.5-coder:3b",
            timeout=120,
        )

        result = llm.generate("Review this Python code.")

    assert result == ('{"summary": "Review complete.", "comments": []}')

    mocked_post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5-coder:3b",
            "prompt": "Review this Python code.",
            "stream": False,
        },
        timeout=120,
    )


def test_generate_raises_clear_error_when_ollama_is_unavailable() -> None:
    with patch(
        "app.llm.ollama_llm.requests.post",
        side_effect=requests.ConnectionError,
    ):
        llm = OllamaLLM(
            base_url="http://localhost:11434",
            model="qwen2.5-coder:3b",
            timeout=120,
        )

        with pytest.raises(
            LLMGenerationError,
            match="Could not connect",
        ):
            llm.generate("Review this code.")


def test_generate_raises_clear_error_when_request_times_out() -> None:
    with patch(
        "app.llm.ollama_llm.requests.post",
        side_effect=requests.Timeout,
    ):
        llm = OllamaLLM(
            base_url="http://localhost:11434",
            model="qwen2.5-coder:3b",
            timeout=120,
        )

        with pytest.raises(
            LLMGenerationError,
            match="timed out",
        ):
            llm.generate("Review this code.")


def test_generate_raises_error_when_model_is_not_found() -> None:
    fake_http_response = Mock()
    fake_http_response.status_code = 404

    with patch(
        "app.llm.ollama_llm.requests.post",
        return_value=fake_http_response,
    ):
        llm = OllamaLLM(
            base_url="http://localhost:11434",
            model="missing-model",
            timeout=120,
        )

        with pytest.raises(
            LLMGenerationError,
            match="model was not found",
        ):
            llm.generate("Review this code.")


def test_generate_raises_error_for_server_failure() -> None:
    fake_http_response = Mock()
    fake_http_response.status_code = 500

    with patch(
        "app.llm.ollama_llm.requests.post",
        return_value=fake_http_response,
    ):
        llm = OllamaLLM(
            base_url="http://localhost:11434",
            model="qwen2.5-coder:3b",
            timeout=120,
        )

        with pytest.raises(
            LLMGenerationError,
            match="HTTP 500",
        ):
            llm.generate("Review this code.")


def test_generate_rejects_missing_response_field() -> None:
    fake_http_response = Mock()
    fake_http_response.status_code = 200
    fake_http_response.json.return_value = {
        "done": True,
    }

    with patch(
        "app.llm.ollama_llm.requests.post",
        return_value=fake_http_response,
    ):
        llm = OllamaLLM(
            base_url="http://localhost:11434",
            model="qwen2.5-coder:3b",
            timeout=120,
        )

        with pytest.raises(
            LLMGenerationError,
            match="valid 'response' field",
        ):
            llm.generate("Review this code.")


def test_generate_rejects_invalid_json_response() -> None:
    fake_http_response = Mock()
    fake_http_response.status_code = 200
    fake_http_response.json.side_effect = requests.exceptions.JSONDecodeError(
        "Invalid JSON",
        "",
        0,
    )

    with patch(
        "app.llm.ollama_llm.requests.post",
        return_value=fake_http_response,
    ):
        llm = OllamaLLM(
            base_url="http://localhost:11434",
            model="qwen2.5-coder:3b",
            timeout=120,
        )

        with pytest.raises(
            LLMGenerationError,
            match="invalid JSON",
        ):
            llm.generate("Review this code.")
