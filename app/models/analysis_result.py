from pydantic import BaseModel, Field

from app.models.finding import Finding


class AnalysisResult(BaseModel):
    """Represents the combined output of static analysis."""

    findings: list[Finding] = Field(
        default_factory=list,
        description="All normalized findings produced by the analyzers.",
    )

    analyzers_run: list[str] = Field(
        default_factory=list,
        description="Names of analyzers that completed successfully.",
    )

    errors: list[str] = Field(
        default_factory=list,
        description="Errors raised by analyzers during execution.",
    )

    execution_time_ms: float = Field(
        ge=0,
        description="Total analysis execution time in milliseconds.",
    )

    @property
    def success(self) -> bool:
        """Return True when every analyzer completed without errors."""
        return not self.errors
