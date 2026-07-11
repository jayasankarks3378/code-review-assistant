from app.exceptions import LLMGenerationError
from app.llm.base_llm import BaseLLM
from app.models.analysis_result import AnalysisResult
from app.models.review_response import ReviewResponse
from app.models.source_file import SourceFile
from app.prompts.review_prompt_builder import ReviewPromptBuilder
from app.response.review_response_parser import ReviewResponseParser


class ReviewService:
    """Coordinate prompt construction, LLM generation, and validation."""

    def __init__(
        self,
        prompt_builder: ReviewPromptBuilder,
        llm: BaseLLM,
        response_parser: ReviewResponseParser,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._llm = llm
        self._response_parser = response_parser

    def review(
        self,
        source_file: SourceFile,
        analysis_result: AnalysisResult,
    ) -> ReviewResponse:
        """
        Generate and validate an AI-assisted code review.

        Args:
            source_file: Source code being reviewed.
            analysis_result: Normalized static-analysis output.

        Returns:
            Validated AI review response.

        Raises:
            LLMGenerationError: If response generation fails.
            ReviewResponseValidationError:
                If the LLM response does not satisfy the contract.
        """
        prompt = self._prompt_builder.build(
            source_file=source_file,
            analysis_result=analysis_result,
        )

        try:
            raw_response = self._llm.generate(prompt)
        except LLMGenerationError:
            raise
        except RuntimeError as exc:
            raise LLMGenerationError(
                "The LLM provider failed to generate a response."
            ) from exc

        return self._response_parser.parse(raw_response)
