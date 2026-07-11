class CodeReviewAssistantError(Exception):
    """Base exception for application-level failures."""


class LLMGenerationError(CodeReviewAssistantError):
    """Raised when an LLM provider cannot generate a response."""


class ReviewResponseValidationError(CodeReviewAssistantError):
    """Raised when an LLM response does not match the expected contract."""
