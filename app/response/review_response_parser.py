from pydantic import ValidationError

from app.models.review_response import ReviewResponse


class ReviewResponseParser:
    """Parse and validate raw LLM code-review responses."""

    def parse(self, raw_response: str) -> ReviewResponse:
        """
        Convert raw model output into a validated review response.

        Args:
            raw_response: Raw text returned by an LLM provider.

        Returns:
            Validated ReviewResponse.

        Raises:
            ValueError: If the response is empty, malformed, or does not
                satisfy the expected response contract.
        """
        cleaned_response = self._remove_json_code_fence(raw_response.strip())

        if not cleaned_response:
            raise ValueError("LLM response must not be empty.")

        try:
            return ReviewResponse.model_validate_json(cleaned_response)
        except ValidationError as exc:
            raise ValueError(
                "LLM response does not match the expected JSON contract."
            ) from exc

    @staticmethod
    def _remove_json_code_fence(response: str) -> str:
        """
        Remove one surrounding Markdown JSON code fence.

        The prompt asks models not to return Markdown fences, but some
        models may still wrap otherwise valid JSON in one.
        """
        if response.startswith("```json") and response.endswith("```"):
            return response[len("```json") : -len("```")].strip()

        if response.startswith("```") and response.endswith("```"):
            return response[len("```") : -len("```")].strip()

        return response
