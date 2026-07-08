from pydantic import BaseModel, Field

from app.models.enums import Category, Severity


class Finding(BaseModel):
    """
    Represents a single issue detected by a static analysis tool.
    """

    analyzer: str = Field(
        ...,
        description="Name of the analyzer that detected the issue."
    )

    rule_id: str = Field(
        ...,
        description="Unique rule identifier (e.g., F401, B602)."
    )

    severity: Severity

    category: Category

    line: int = Field(
        ...,
        ge=1,
        description="Line number where the issue occurs."
    )

    column: int | None = Field(
        default=None,
        ge=1,
        description="Column number where the issue occurs."
    )

    message: str = Field(
        ...,
        description="Human-readable description of the issue."
    )

    suggestion: str | None = Field(
        default=None,
        description="Optional recommendation for resolving the issue."
    )
    