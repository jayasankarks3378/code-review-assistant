import json
from pathlib import Path

import pytest

from app.models.analysis_result import AnalysisResult
from app.models.enums import Language, ReportFormat
from app.models.review_response import ReviewResponse
from app.models.source_file import SourceFile
from app.reports.json_report_generator import JsonReportGenerator
from app.reports.markdown_report_generator import (
    MarkdownReportGenerator,
)
from app.services.report_service import ReportService


def create_report_service() -> ReportService:
    return ReportService(
        generators={
            ReportFormat.MARKDOWN: MarkdownReportGenerator(),
            ReportFormat.JSON: JsonReportGenerator(),
        }
    )


def create_source_file() -> SourceFile:
    return SourceFile(
        path=Path("sample.py"),
        language=Language.PYTHON,
        content="print('Hello')\n",
    )


def create_analysis_result() -> AnalysisResult:
    return AnalysisResult(
        findings=[],
        analyzers_run=[
            "RuffAnalyzer",
            "BanditAnalyzer",
        ],
        errors=[],
        execution_time_ms=2.5,
    )


def create_review_response() -> ReviewResponse:
    return ReviewResponse(
        summary="No significant issues were identified.",
        comments=[],
    )


def test_generate_returns_markdown_report() -> None:
    service = create_report_service()

    result = service.generate(
        report_format=ReportFormat.MARKDOWN,
        source_file=create_source_file(),
        analysis_result=create_analysis_result(),
        review_response=create_review_response(),
    )

    assert "# Code Review Report" in result
    assert "No significant issues were identified." in result


def test_generate_returns_json_report() -> None:
    service = create_report_service()

    result = service.generate(
        report_format=ReportFormat.JSON,
        source_file=create_source_file(),
        analysis_result=create_analysis_result(),
        review_response=create_review_response(),
    )

    data = json.loads(result)

    assert data["source_file"]["language"] == "python"
    assert data["ai_review"]["summary"] == "No significant issues were identified."


def test_constructor_rejects_empty_generator_configuration() -> None:
    with pytest.raises(
        ValueError,
        match="At least one report generator",
    ):
        ReportService(generators={})


def test_generate_rejects_unconfigured_format() -> None:
    service = ReportService(
        generators={
            ReportFormat.MARKDOWN: MarkdownReportGenerator(),
        }
    )

    with pytest.raises(
        ValueError,
        match="Unsupported report format",
    ):
        service.generate(
            report_format=ReportFormat.JSON,
            source_file=create_source_file(),
            analysis_result=create_analysis_result(),
            review_response=create_review_response(),
        )


def test_write_creates_report_file(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "reports" / "review.md"

    written_path = ReportService.write(
        report_content="# Review\n",
        output_path=output_path,
    )

    assert written_path == output_path.resolve()
    assert output_path.read_text(encoding="utf-8") == "# Review\n"


def test_write_rejects_existing_file_without_overwrite(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "review.md"
    output_path.write_text(
        "Existing report",
        encoding="utf-8",
    )

    with pytest.raises(
        FileExistsError,
        match="already exists",
    ):
        ReportService.write(
            report_content="New report",
            output_path=output_path,
        )

    assert output_path.read_text(encoding="utf-8") == "Existing report"


def test_write_replaces_existing_file_when_overwrite_is_enabled(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "review.md"
    output_path.write_text(
        "Old content",
        encoding="utf-8",
    )

    ReportService.write(
        report_content="New content",
        output_path=output_path,
        overwrite=True,
    )

    assert output_path.read_text(encoding="utf-8") == "New content"


def test_write_rejects_empty_report_content(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        ReportService.write(
            report_content="   ",
            output_path=tmp_path / "review.md",
        )
