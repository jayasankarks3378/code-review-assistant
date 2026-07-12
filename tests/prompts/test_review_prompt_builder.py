from pathlib import Path

import pytest

from app.models.analysis_result import AnalysisResult
from app.models.enums import Category, Language, Severity
from app.models.finding import Finding
from app.models.source_file import SourceFile
from app.prompts.review_prompt_builder import ReviewPromptBuilder


def create_source_file() -> SourceFile:
    """Create a reusable Python source file for prompt tests."""

    return SourceFile(
        path=Path("sample.py"),
        language=Language.PYTHON,
        content=(
            "import os\n"
            "import subprocess\n\n"
            "def execute(command):\n"
            "    subprocess.run(command, shell=True)\n"
        ),
    )


def create_analysis_result() -> AnalysisResult:
    """Create reusable static-analysis findings."""

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
            ),
            Finding(
                analyzer="bandit",
                rule_id="B602",
                severity=Severity.ERROR,
                category=Category.SECURITY,
                line=5,
                column=5,
                message=(
                    "subprocess call with shell=True identified, " "security issue."
                ),
                suggestion=None,
            ),
        ],
        analyzers_run=[
            "RuffAnalyzer",
            "BanditAnalyzer",
        ],
        errors=[],
        execution_time_ms=5.0,
    )


def test_build_includes_source_code_and_findings() -> None:
    prompt = ReviewPromptBuilder().build(
        source_file=create_source_file(),
        analysis_result=create_analysis_result(),
    )

    assert "import os" in prompt
    assert "subprocess.run(command, shell=True)" in prompt

    assert "F401" in prompt
    assert "B602" in prompt

    assert "`os` imported but unused" in prompt
    assert "subprocess call with shell=True" in prompt


def test_build_includes_false_positive_reduction_rules() -> None:
    prompt = ReviewPromptBuilder().build(
        source_file=create_source_file(),
        analysis_result=create_analysis_result(),
    )

    assert (
        "Treat static-analysis findings as evidence, "
        "not guaranteed defects." in prompt
    )
    assert "Do not invent issues unsupported by the supplied code." in prompt
    assert "State uncertainty when context is insufficient." in prompt


def test_build_includes_priority_guidance() -> None:
    prompt = ReviewPromptBuilder().build(
        source_file=create_source_file(),
        analysis_result=create_analysis_result(),
    )

    assert "Do not assign high priority to style or unused-import findings" in prompt
    assert "Use low priority for ordinary style and readability issues." in prompt
    assert (
        "Use medium or high priority only when the code provides "
        "concrete evidence" in prompt
    )


def test_build_includes_duplicate_suppression_rules() -> None:
    prompt = ReviewPromptBuilder().build(
        source_file=create_source_file(),
        analysis_result=create_analysis_result(),
    )

    assert "Merge findings that refer to the same root cause." in prompt
    assert "more specific actionable issue" in prompt
    assert "Avoid duplicate or equivalent comments." in prompt


def test_build_includes_subprocess_security_guidance() -> None:
    prompt = ReviewPromptBuilder().build(
        source_file=create_source_file(),
        analysis_result=create_analysis_result(),
    )

    assert "text=True or check=True prevents command injection" in prompt
    assert "Prefer shell=False." in prompt
    assert "passing command arguments as a list" in prompt
    assert "process error handling" in prompt


def test_build_rejects_unrelated_recommendations() -> None:
    prompt = ReviewPromptBuilder().build(
        source_file=create_source_file(),
        analysis_result=create_analysis_result(),
    )

    assert "Do not recommend unrelated libraries or tools." in prompt
    assert "Every recommendation must directly mitigate the identified issue." in prompt


def test_build_handles_empty_findings_conservatively() -> None:
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
        source_file=create_source_file(),
        analysis_result=analysis_result,
    )

    assert "No static-analysis findings were detected." in prompt
    assert "Perform a conservative review" in prompt
    assert "report only issues clearly supported by the source code" in prompt


def test_build_includes_analyzer_errors() -> None:
    analysis_result = AnalysisResult(
        findings=[],
        analyzers_run=["RuffAnalyzer"],
        errors=[
            "BanditAnalyzer: Bandit is not installed.",
        ],
        execution_time_ms=1.0,
    )

    prompt = ReviewPromptBuilder().build(
        source_file=create_source_file(),
        analysis_result=analysis_result,
    )

    assert "Analyzer execution errors:" in prompt
    assert "BanditAnalyzer: Bandit is not installed." in prompt


def test_build_limits_number_of_findings() -> None:
    findings = [
        Finding(
            analyzer="ruff",
            rule_id=f"F40{index}",
            severity=Severity.WARNING,
            category=Category.STYLE,
            line=index + 1,
            column=1,
            message=f"Finding number {index}",
            suggestion=None,
        )
        for index in range(5)
    ]

    analysis_result = AnalysisResult(
        findings=findings,
        analyzers_run=["RuffAnalyzer"],
        errors=[],
        execution_time_ms=1.0,
    )

    prompt = ReviewPromptBuilder(max_findings=2).build(
        source_file=create_source_file(),
        analysis_result=analysis_result,
    )

    assert "Finding number 0" in prompt
    assert "Finding number 1" in prompt
    assert "Finding number 2" not in prompt
    assert "3 additional static-analysis finding(s) were omitted" in prompt


@pytest.mark.parametrize(
    "max_findings",
    [
        0,
        -1,
    ],
)
def test_constructor_rejects_invalid_max_findings(
    max_findings: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_findings must be at least 1",
    ):
        ReviewPromptBuilder(max_findings=max_findings)
