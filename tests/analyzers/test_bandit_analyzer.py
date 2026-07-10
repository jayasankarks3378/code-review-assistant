import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.analyzers.bandit_analyzer import BanditAnalyzer
from app.models.enums import Category, Language, Severity
from app.models.source_file import SourceFile


@pytest.fixture
def source_file() -> SourceFile:
    """Return Python source code containing an unsafe subprocess call."""

    return SourceFile(
        path=Path("vulnerable.py"),
        language=Language.PYTHON,
        content=("import subprocess\n\n" "subprocess.run('ls', shell=True)\n"),
    )


def test_analyze_converts_bandit_result_to_finding(
    source_file: SourceFile,
) -> None:
    bandit_output = {
        "results": [
            {
                "test_id": "B602",
                "issue_severity": "HIGH",
                "issue_confidence": "HIGH",
                "issue_text": ("subprocess call with shell=True identified"),
                "line_number": 3,
                "col_offset": 0,
            }
        ]
    }

    completed_process = Mock(
        stdout=json.dumps(bandit_output),
        stderr="",
        returncode=1,
    )

    with patch(
        "app.analyzers.bandit_analyzer.subprocess.run",
        return_value=completed_process,
    ):
        findings = BanditAnalyzer().analyze(source_file)

    assert len(findings) == 1

    finding = findings[0]

    assert finding.analyzer == "bandit"
    assert finding.rule_id == "B602"
    assert finding.severity == Severity.ERROR
    assert finding.category == Category.SECURITY
    assert finding.line == 3
    assert finding.column == 1
    assert finding.message == ("subprocess call with shell=True identified")


def test_analyze_returns_empty_list_when_no_issues_are_found(
    source_file: SourceFile,
) -> None:
    completed_process = Mock(
        stdout=json.dumps({"results": []}),
        stderr="",
        returncode=0,
    )

    with patch(
        "app.analyzers.bandit_analyzer.subprocess.run",
        return_value=completed_process,
    ):
        findings = BanditAnalyzer().analyze(source_file)

    assert findings == []


@pytest.mark.parametrize(
    ("bandit_severity", "expected_severity"),
    [
        ("LOW", Severity.INFO),
        ("MEDIUM", Severity.WARNING),
        ("HIGH", Severity.ERROR),
    ],
)
def test_map_severity_returns_expected_internal_severity(
    bandit_severity: str,
    expected_severity: Severity,
) -> None:
    result = BanditAnalyzer._map_severity(bandit_severity)

    assert result == expected_severity


def test_analyze_raises_clear_error_when_bandit_is_unavailable(
    source_file: SourceFile,
) -> None:
    with patch(
        "app.analyzers.bandit_analyzer.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        with pytest.raises(
            RuntimeError,
            match="Bandit is not installed",
        ):
            BanditAnalyzer().analyze(source_file)


def test_analyze_raises_error_for_invalid_json(
    source_file: SourceFile,
) -> None:
    completed_process = Mock(
        stdout="This is not JSON",
        stderr="",
        returncode=0,
    )

    with patch(
        "app.analyzers.bandit_analyzer.subprocess.run",
        return_value=completed_process,
    ):
        with pytest.raises(
            RuntimeError,
            match="invalid JSON",
        ):
            BanditAnalyzer().analyze(source_file)


def test_analyze_raises_error_when_bandit_execution_fails(
    source_file: SourceFile,
) -> None:
    completed_process = Mock(
        stdout="",
        stderr="Invalid Bandit configuration",
        returncode=2,
    )

    with patch(
        "app.analyzers.bandit_analyzer.subprocess.run",
        return_value=completed_process,
    ):
        with pytest.raises(
            RuntimeError,
            match="Bandit execution failed",
        ):
            BanditAnalyzer().analyze(source_file)
