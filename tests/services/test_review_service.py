from pathlib import Path

import pytest

from app.exceptions import (
    LLMGenerationError,
    ReviewResponseValidationError,
)
from app.llm.base_llm import BaseLLM
from app.llm.mock_llm import MockLLM
from app.models.analysis_result import AnalysisResult
from app.models.enums import Language
from app.models.source_file import SourceFile
from app.prompts.review_prompt_builder import ReviewPromptBuilder
from app.response.review_response_parser import ReviewResponseParser
from app.services.review_service import ReviewService


def create_source_file() -> SourceFile:
    """Create a simple Python source file for tests."""

    return SourceFile(
        path=Path("sample.py"),
        language=Language.PYTHON,
        content="print('Hello')\n",
    )


def create_analysis_result() -> AnalysisResult:
    """Create a successful empty static-analysis result."""

    return AnalysisResult(
        findings=[],
        analyzers_run=[
            "RuffAnalyzer",
            "BanditAnalyzer",
        ],
        errors=[],
        execution_time_ms=1.0,
    )


def test_review_returns_validated_response() -> None:
    llm = MockLLM(
        response=('{"summary": "No significant issues were found.", ' '"comments": []}')
    )

    service = ReviewService(
        prompt_builder=ReviewPromptBuilder(),
        llm=llm,
        response_parser=ReviewResponseParser(),
    )

    result = service.review(
        source_file=create_source_file(),
        analysis_result=create_analysis_result(),
    )

    assert result.summary == "No significant issues were found."
    assert result.comments == []


def test_review_raises_error_for_invalid_llm_response() -> None:
    service = ReviewService(
        prompt_builder=ReviewPromptBuilder(),
        llm=MockLLM(response="not valid JSON"),
        response_parser=ReviewResponseParser(),
    )

    with pytest.raises(ReviewResponseValidationError):
        service.review(
            source_file=create_source_file(),
            analysis_result=create_analysis_result(),
        )


class FailingLLM(BaseLLM):
    """Simulate an operational LLM provider failure."""

    def generate(self, prompt: str) -> str:
        raise RuntimeError("Provider unavailable")


def test_review_translates_provider_failure() -> None:
    service = ReviewService(
        prompt_builder=ReviewPromptBuilder(),
        llm=FailingLLM(),
        response_parser=ReviewResponseParser(),
    )

    with pytest.raises(
        LLMGenerationError,
        match="failed to generate",
    ):
        service.review(
            source_file=create_source_file(),
            analysis_result=create_analysis_result(),
        )


class RecordingLLM(BaseLLM):
    """Record the received prompt and return valid JSON."""

    def __init__(self) -> None:
        self.received_prompt: str | None = None

    def generate(self, prompt: str) -> str:
        self.received_prompt = prompt

        return '{"summary": "Review complete.", ' '"comments": []}'


def test_review_passes_built_prompt_to_llm() -> None:
    llm = RecordingLLM()

    service = ReviewService(
        prompt_builder=ReviewPromptBuilder(),
        llm=llm,
        response_parser=ReviewResponseParser(),
    )

    service.review(
        source_file=create_source_file(),
        analysis_result=create_analysis_result(),
    )

    assert llm.received_prompt is not None
    assert "print('Hello')" in llm.received_prompt
    assert "No static-analysis findings were detected" in (llm.received_prompt)
