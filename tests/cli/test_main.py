from pathlib import Path
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from app.cli.main import app
from app.models.analysis_result import AnalysisResult
from app.models.review_response import ReviewResponse

runner = CliRunner()


def test_review_rejects_non_python_file(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "sample.txt"
    source_path.write_text("not Python", encoding="utf-8")

    result = runner.invoke(
        app,
        [str(source_path)],
    )

    assert result.exit_code == 1
    assert "Only Python files are currently supported" in result.output


def test_review_rejects_missing_file() -> None:
    result = runner.invoke(
        app,
        ["missing.py"],
    )

    assert result.exit_code != 0


def test_review_prints_generated_report(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "sample.py"
    source_path.write_text(
        "print('Hello')\n",
        encoding="utf-8",
    )

    mock_container = Mock()

    analysis_result = AnalysisResult(
        findings=[],
        analyzers_run=[
            "RuffAnalyzer",
            "BanditAnalyzer",
        ],
        errors=[],
        execution_time_ms=2.0,
    )

    review_response = ReviewResponse(
        summary="No significant issues were identified.",
        comments=[],
    )

    mock_container.parser.parse.return_value = None
    mock_container.analysis_service.analyze.return_value = analysis_result
    mock_container.review_service.review.return_value = review_response
    mock_container.report_service.generate.return_value = (
        "# Code Review Report\n\nNo significant issues."
    )

    with patch(
        "app.cli.main.ApplicationContainer",
        return_value=mock_container,
    ):
        result = runner.invoke(
            app,
            [str(source_path)],
        )

    assert result.exit_code == 0
    assert "# Code Review Report" in result.output

    mock_container.parser.parse.assert_called_once()
    mock_container.analysis_service.analyze.assert_called_once()
    mock_container.review_service.review.assert_called_once()
    mock_container.report_service.generate.assert_called_once()


def test_review_saves_generated_report(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "sample.py"
    output_path = tmp_path / "review.md"

    source_path.write_text(
        "print('Hello')\n",
        encoding="utf-8",
    )

    mock_container = Mock()

    analysis_result = AnalysisResult(
        findings=[],
        analyzers_run=["RuffAnalyzer", "BanditAnalyzer"],
        errors=[],
        execution_time_ms=2.0,
    )

    review_response = ReviewResponse(
        summary="Review complete.",
        comments=[],
    )

    mock_container.parser.parse.return_value = None
    mock_container.analysis_service.analyze.return_value = analysis_result
    mock_container.review_service.review.return_value = review_response
    mock_container.report_service.generate.return_value = "# Code Review Report\n"
    mock_container.report_service.write.return_value = output_path.resolve()

    with patch(
        "app.cli.main.ApplicationContainer",
        return_value=mock_container,
    ):
        result = runner.invoke(
            app,
            [
                str(source_path),
                "--output",
                str(output_path),
            ],
        )

    assert result.exit_code == 0
    assert "Report saved to" in result.output

    mock_container.report_service.write.assert_called_once_with(
        report_content="# Code Review Report\n",
        output_path=output_path,
        overwrite=False,
    )


def test_review_passes_requested_format_to_report_service(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "sample.py"
    source_path.write_text(
        "print('Hello')\n",
        encoding="utf-8",
    )

    mock_container = Mock()

    analysis_result = AnalysisResult(
        findings=[],
        analyzers_run=[],
        errors=[],
        execution_time_ms=1.0,
    )

    review_response = ReviewResponse(
        summary="Review complete.",
        comments=[],
    )

    mock_container.analysis_service.analyze.return_value = analysis_result
    mock_container.review_service.review.return_value = review_response
    mock_container.report_service.generate.return_value = "{}"

    with patch(
        "app.cli.main.ApplicationContainer",
        return_value=mock_container,
    ):
        result = runner.invoke(
            app,
            [
                str(source_path),
                "--format",
                "json",
            ],
        )

    assert result.exit_code == 0

    call_arguments = mock_container.report_service.generate.call_args.kwargs

    assert call_arguments["report_format"].value == "json"
