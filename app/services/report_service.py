from pathlib import Path

from app.models.analysis_result import AnalysisResult
from app.models.enums import ReportFormat
from app.models.review_response import ReviewResponse
from app.models.source_file import SourceFile
from app.reports.base_report_generator import BaseReportGenerator


class ReportService:
    """Generate and persist code-review reports."""

    def __init__(
        self,
        generators: dict[ReportFormat, BaseReportGenerator],
    ) -> None:
        if not generators:
            raise ValueError("At least one report generator must be configured.")

        self._generators = generators

    def generate(
        self,
        report_format: ReportFormat,
        source_file: SourceFile,
        analysis_result: AnalysisResult,
        review_response: ReviewResponse,
    ) -> str:
        """
        Generate a report in the requested format.

        Raises:
            ValueError: If the requested format is not configured.
        """
        generator = self._generators.get(report_format)

        if generator is None:
            raise ValueError(f"Unsupported report format: {report_format.value}")

        return generator.generate(
            source_file=source_file,
            analysis_result=analysis_result,
            review_response=review_response,
        )

    @staticmethod
    def write(
        report_content: str,
        output_path: Path,
        *,
        overwrite: bool = False,
    ) -> Path:
        """
        Write generated report content to disk.

        Args:
            report_content: Formatted report text.
            output_path: Destination file path.
            overwrite: Whether an existing file may be replaced.

        Returns:
            Resolved path of the written report.

        Raises:
            ValueError: If the report content is empty.
            FileExistsError: If the destination exists and overwrite is false.
        """
        if not report_content.strip():
            raise ValueError("Report content must not be empty.")

        resolved_path = output_path.expanduser().resolve()

        if resolved_path.exists() and not overwrite:
            raise FileExistsError(f"Output file already exists: {resolved_path}")

        resolved_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        resolved_path.write_text(
            report_content,
            encoding="utf-8",
        )

        return resolved_path
