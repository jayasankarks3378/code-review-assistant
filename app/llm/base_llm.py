from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Define the contract for LLM provider implementations."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a raw text response from a prompt.

        Raises:
            app.exceptions.LLMGenerationError:
                If response generation fails.
        """
        raise NotImplementedError
