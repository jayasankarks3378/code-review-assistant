from pathlib import Path

from app.models.analysis_result import AnalysisResult
from app.models.enums import Category, Language, Severity
from app.models.finding import Finding
from app.models.source_file import SourceFile
from app.prompts.review_prompt_builder import ReviewPromptBuilder


def test_build_includes_source_code_and_findings() -> None:
    source_file = SourceFile(
        path=Path("sample.py"),
        language=Language.PYTHON,
        content="import os\n",
    )

    analysis_result = AnalysisResult(
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
        analyzers_run=["RuffAnalyzer"],
        errors=[],
        execution_time_ms=1.0,
    )

    prompt = ReviewPromptBuilder().build(
        source_file,
        analysis_result,
    )

    assert "import os" in prompt
    assert "F401" in prompt
    assert "`os` imported but unused" in prompt
    assert "Do not invent issues" in prompt
    assert '"comments"' in prompt


def test_build_handles_empty_findings() -> None:
    source_file = SourceFile(
        path=Path("clean.py"),
        language=Language.PYTHON,
        content="print('Hello')\n",
    )

    analysis_result = AnalysisResult(
        findings=[],
        analyzers_run=[
            "RuffAnalyzer",
            "BanditAnalyzer",
        ],
        errors=[],
        execution_time_ms=1.0,
    )

    prompt = ReviewPromptBuilder().build(
        source_file,
        analysis_result,
    )

    assert "No static-analysis findings were detected." in prompt
