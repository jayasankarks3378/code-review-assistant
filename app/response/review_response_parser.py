from pydantic import ValidationError

from app.exceptions import ReviewResponseValidationError
from app.models.review_response import ReviewResponse


class ReviewResponseParser:
    """Parse and validate raw LLM code-review responses."""

    def parse(self, raw_response: str) -> ReviewResponse:
        """
        Convert raw model output into a validated review response.

        Raises:
            ReviewResponseValidationError:
                If the response is empty, malformed, or invalid.
        """
        cleaned_response = self._remove_json_code_fence(raw_response.strip())

        if not cleaned_response:
            raise ReviewResponseValidationError("LLM response must not be empty.")

        try:
            return ReviewResponse.model_validate_json(cleaned_response)
        except ValidationError as exc:
            raise ReviewResponseValidationError(
                "LLM response does not match the expected JSON contract."
            ) from exc

    @staticmethod
    def _remove_json_code_fence(response: str) -> str:
        """Remove one surrounding Markdown JSON code fence."""

        if response.startswith("```json") and response.endswith("```"):
            return response[len("```json") : -len("```")].strip()

        if response.startswith("```") and response.endswith("```"):
            return response[len("```") : -len("```")].strip()

        return response
