from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Category, Priority


class ReviewComment(BaseModel):
    """Represent one validated AI-generated code review comment."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        max_length=120,
        description="Concise title describing the issue.",
    )

    line: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Source-code line related to the comment. "
            "None is allowed for file-level comments."
        ),
    )

    category: Category

    priority: Priority

    explanation: str = Field(
        min_length=1,
        description="Explanation of why the issue matters.",
    )

    recommendation: str = Field(
        min_length=1,
        description="Specific action recommended to the developer.",
    )
