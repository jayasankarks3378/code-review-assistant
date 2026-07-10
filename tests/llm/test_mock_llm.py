import pytest

from app.llm.mock_llm import MockLLM


def test_generate_returns_configured_response() -> None:
    expected_response = '{"summary": "Review complete.", "comments": []}'

    llm = MockLLM(response=expected_response)

    result = llm.generate("Review this code.")

    assert result == expected_response


def test_generate_returns_default_response() -> None:
    llm = MockLLM()

    result = llm.generate("Review this code.")

    assert '"summary"' in result
    assert '"comments"' in result


def test_generate_rejects_empty_prompt() -> None:
    llm = MockLLM()

    with pytest.raises(ValueError, match="Prompt must not be empty"):
        llm.generate("   ")
