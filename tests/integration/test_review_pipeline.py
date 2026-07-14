from pathlib import Path

import pytest

from app.analyzers.bandit_analyzer import BanditAnalyzer
from app.analyzers.ruff_analyzer import RuffAnalyzer
from app.llm.mock_llm import MockLLM
from app.models.enums import Category, Language, Priority
from app.models.source_file import SourceFile
from app.parser.python_parser import PythonParser
from app.prompts.review_prompt_builder import ReviewPromptBuilder
from app.reports.markdown_report_generator import MarkdownReportGenerator
from app.response.review_response_parser import ReviewResponseParser
from app.services.analysis_service import AnalysisService
from app.services.review_service import ReviewService


@pytest.mark.integration
def test_review_pipeline_generates_valid_report() -> None:
    source_file = SourceFile(
        path=Path("vulnerable_example.py"),
        language=Language.PYTHON,
        content=(
            "import os\n"
            "import subprocess\n\n"
            "def execute(command):\n"
            '    password = "admin123"\n'
            "    subprocess.run(command, shell=True)\n"
            "    return password\n"
        ),
    )

    PythonParser(max_lines=500).parse(source_file)

    analysis_service = AnalysisService(
        analyzers=[
            RuffAnalyzer(),
            BanditAnalyzer(),
        ]
    )

    analysis_result = analysis_service.analyze(source_file)

    mock_response = """
    {
      "summary": "Two security issues and one style issue were identified.",
      "comments": [
        {
          "title": "Remove unused import",
          "line": 1,
          "category": "style",
          "priority": "low",
          "explanation": "The os module is imported but never used.",
          "recommendation": "Remove the unused import."
        },
        {
          "title": "Avoid hardcoded credentials",
          "line": 5,
          "category": "security",
          "priority": "medium",
          "explanation": "Credentials stored in source code may be exposed.",
          "recommendation": "Load the credential from secure configuration."
        },
        {
          "title": "Avoid shell command injection",
          "line": 6,
          "category": "security",
          "priority": "high",
          "explanation": "Using shell=True with uncontrolled input may allow command injection.",
          "recommendation": "Use shell=False and pass arguments as a list."
        }
      ]
    }
    """

    review_service = ReviewService(
        prompt_builder=ReviewPromptBuilder(max_findings=50),
        llm=MockLLM(response=mock_response),
        response_parser=ReviewResponseParser(),
    )

    review_response = review_service.review(
        source_file=source_file,
        analysis_result=analysis_result,
    )

    report = MarkdownReportGenerator().generate(
        source_file=source_file,
        analysis_result=analysis_result,
        review_response=review_response,
    )

    assert analysis_result.success is True
    assert analysis_result.findings
    assert len(review_response.comments) == 3

    categories = {comment.category for comment in review_response.comments}

    priorities = {comment.priority for comment in review_response.comments}

    assert Category.SECURITY in categories
    assert Category.STYLE in categories
    assert Priority.HIGH in priorities
    assert Priority.LOW in priorities

    assert "# Code Review Report" in report
    assert "Avoid shell command injection" in report
    assert "Remove unused import" in report

    analyzer_names = {finding.analyzer for finding in analysis_result.findings}

    assert "ruff" in analyzer_names
    assert "bandit" in analyzer_names
    assert analysis_result.findings
