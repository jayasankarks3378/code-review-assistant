import json

from app.llm.base_llm import BaseLLM


class MockLLM(BaseLLM):
    """Return a deterministic response for local development and testing."""

    def __init__(self, response: str | None = None) -> None:
        """
        Initialize the mock provider.

        Args:
            response: Optional raw response returned by generate().
                When omitted, a valid default review response is used.
        """
        self._response = response or self._default_response()

    def generate(self, prompt: str) -> str:
        """
        Return the configured response without calling a real model.

        Args:
            prompt: Prompt supplied by the review engine.

        Returns:
            Configured mock response.
        """
        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        return self._response

    @staticmethod
    def _default_response() -> str:
        """Return a valid default JSON review response."""

        response = {
            "summary": "The code was reviewed successfully.",
            "comments": [],
        }

        return json.dumps(response)
