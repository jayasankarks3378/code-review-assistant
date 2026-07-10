from pydantic import BaseModel, ConfigDict, Field

from app.models.review_comment import ReviewComment


class ReviewResponse(BaseModel):
    """Represent the complete validated response from the LLM."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(
        min_length=1,
        max_length=1000,
        description="Brief overall assessment of the reviewed code.",
    )

    comments: list[ReviewComment] = Field(
        default_factory=list,
        description="Validated AI-generated review comments.",
    )
