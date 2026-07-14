import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from app.analyzers.bandit_analyzer import BanditAnalyzer
from app.analyzers.ruff_analyzer import RuffAnalyzer
from app.cli.main import app
from app.llm.mock_llm import MockLLM
from app.models.enums import ReportFormat
from app.parser.python_parser import PythonParser
from app.prompts.review_prompt_builder import ReviewPromptBuilder
from app.reports.json_report_generator import JsonReportGenerator
from app.reports.markdown_report_generator import (
    MarkdownReportGenerator,
)
from app.response.review_response_parser import ReviewResponseParser
from app.services.analysis_service import AnalysisService
from app.services.report_service import ReportService
from app.services.review_service import ReviewService

runner = CliRunner()


class IntegrationApplicationContainer:
    """Wire real components with a deterministic mock LLM."""

    def __init__(self) -> None:
        self.parser = PythonParser(max_lines=500)

        self.analysis_service = AnalysisService(
            analyzers=[
                RuffAnalyzer(),
                BanditAnalyzer(),
            ]
        )

        self.review_service = ReviewService(
            prompt_builder=ReviewPromptBuilder(max_findings=50),
            llm=MockLLM(
                response=json.dumps(
                    {
                        "summary": "One security issue was identified.",
                        "comments": [
                            {
                                "title": ("Avoid unsafe shell execution"),
                                "line": 5,
                                "category": "security",
                                "priority": "high",
                                "explanation": (
                                    "Using shell=True may allow " "command injection."
                                ),
                                "recommendation": (
                                    "Use shell=False and pass " "arguments as a list."
                                ),
                            }
                        ],
                    }
                )
            ),
            response_parser=ReviewResponseParser(),
        )

        self.report_service = ReportService(
            generators={
                ReportFormat.MARKDOWN: MarkdownReportGenerator(),
                ReportFormat.JSON: JsonReportGenerator(),
            }
        )


@pytest.mark.integration
def test_cli_pipeline_prints_markdown_report(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "vulnerable.py"

    source_path.write_text(
        (
            "import subprocess\n\n"
            "def execute(command):\n"
            "    password = 'admin123'\n"
            "    subprocess.run(command, shell=True)\n"
            "    return password\n"
        ),
        encoding="utf-8",
    )

    with patch(
        "app.cli.main.ApplicationContainer",
        IntegrationApplicationContainer,
    ):
        result = runner.invoke(
            app,
            [
                str(source_path),
            ],
        )

    assert result.exit_code == 0, result.output
    assert "# Code Review Report" in result.output
    assert "One security issue was identified." in result.output
    assert "Avoid unsafe shell execution" in result.output
    assert "B602" in result.output


@pytest.mark.integration
def test_cli_pipeline_writes_json_report(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "vulnerable.py"
    output_path = tmp_path / "reports" / "review.json"

    source_path.write_text(
        (
            "import subprocess\n\n"
            "def execute(command):\n"
            "    value = command\n"
            "    subprocess.run(value, shell=True)\n"
        ),
        encoding="utf-8",
    )

    with patch(
        "app.cli.main.ApplicationContainer",
        IntegrationApplicationContainer,
    ):
        result = runner.invoke(
            app,
            [
                str(source_path),
                "--format",
                "json",
                "--output",
                str(output_path),
            ],
        )

    assert result.exit_code == 0, result.output
    assert "Report saved to" in result.output
    assert output_path.exists()

    report_content = output_path.read_text(encoding="utf-8")

    assert '"source_file"' in report_content
    assert '"static_analysis"' in report_content
    assert '"ai_review"' in report_content
    assert '"security"' in report_content
