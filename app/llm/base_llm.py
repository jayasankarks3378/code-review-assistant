from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Define the contract for LLM provider implementations."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a raw text response from a prompt.

        Args:
            prompt: Complete prompt prepared for the language model.

        Returns:
            Raw text returned by the language model.

        Raises:
            RuntimeError: If response generation fails.
        """
        raise NotImplementedError
