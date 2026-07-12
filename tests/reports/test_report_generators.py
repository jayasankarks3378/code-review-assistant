import json
from pathlib import Path

from app.models.analysis_result import AnalysisResult
from app.models.enums import Category, Language, Priority, Severity
from app.models.finding import Finding
from app.models.review_comment import ReviewComment
from app.models.review_response import ReviewResponse
from app.models.source_file import SourceFile
from app.reports.json_report_generator import JsonReportGenerator
from app.reports.markdown_report_generator import (
    MarkdownReportGenerator,
)


def create_source_file() -> SourceFile:
    return SourceFile(
        path=Path("sample.py"),
        language=Language.PYTHON,
        content="import os\n",
    )


def create_analysis_result() -> AnalysisResult:
    return AnalysisResult(
        findings=[
            Finding(
                analyzer="ruff",
                rule_id="F401",
                severity=Severity.ERROR,
                category=Category.BUG,
                line=1,
                column=8,
                message="`os` imported but unused",
                suggestion=None,
            )
        ],
        analyzers_run=["RuffAnalyzer", "BanditAnalyzer"],
        errors=[],
        execution_time_ms=4.5,
    )


def create_review_response() -> ReviewResponse:
    return ReviewResponse(
        summary="One issue should be addressed.",
        comments=[
            ReviewComment(
                title="Remove unused import",
                line=1,
                category=Category.READABILITY,
                priority=Priority.LOW,
                explanation="The import is not used.",
                recommendation="Remove the unused import.",
            )
        ],
    )


def test_markdown_report_contains_review_information() -> None:
    report = MarkdownReportGenerator().generate(
        create_source_file(),
        create_analysis_result(),
        create_review_response(),
    )

    assert "# Code Review Report" in report
    assert "sample.py" in report
    assert "F401" in report
    assert "One issue should be addressed." in report
    assert "Remove unused import" in report


def test_json_report_contains_structured_information() -> None:
    report = JsonReportGenerator().generate(
        create_source_file(),
        create_analysis_result(),
        create_review_response(),
    )

    data = json.loads(report)

    assert data["source_file"]["path"] == "sample.py"
    assert data["source_file"]["language"] == "python"
    assert data["static_analysis"]["findings"][0]["rule_id"] == "F401"
    assert data["ai_review"]["comments"][0]["line"] == 1


def test_markdown_report_includes_analyzer_errors() -> None:
    analysis_result = AnalysisResult(
        findings=[],
        analyzers_run=["RuffAnalyzer"],
        errors=["BanditAnalyzer: Bandit is unavailable"],
        execution_time_ms=2.0,
    )

    report = MarkdownReportGenerator().generate(
        create_source_file(),
        analysis_result,
        ReviewResponse(
            summary="The review had incomplete analyzer coverage.",
            comments=[],
        ),
    )

    assert "Partial failure" in report
    assert "BanditAnalyzer: Bandit is unavailable" in report


def test_markdown_report_handles_empty_review_comments() -> None:
    report = MarkdownReportGenerator().generate(
        create_source_file(),
        create_analysis_result(),
        ReviewResponse(
            summary="No additional AI issues were found.",
            comments=[],
        ),
    )

    assert "No actionable review comments were generated." in report
