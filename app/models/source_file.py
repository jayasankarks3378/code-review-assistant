from pathlib import Path

from pydantic import BaseModel, Field, computed_field

from app.models.enums import Language


class SourceFile(BaseModel):
    """
    Represents a source file submitted for review.
    """

    path: Path = Field(
        ...,
        description="Path to the source file."
    )

    language: Language

    content: str = Field(
        ...,
        description="Raw source code."
    )

    encoding: str = Field(
        default="utf-8",
        description="File encoding."
    )

    @computed_field
    @property
    def line_count(self) -> int:
        """Number of lines in the source file."""
        return len(self.content.splitlines())