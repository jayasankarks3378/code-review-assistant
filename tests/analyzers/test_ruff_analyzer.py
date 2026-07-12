import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.analyzers.ruff_analyzer import RuffAnalyzer, map_category, map_severity
from app.models.enums import Category, Language, Severity
from app.models.source_file import SourceFile


def test_analyze_converts_ruff_diagnostic_to_finding() -> None:
    source_file = SourceFile(
        path=Path("sample.py"),
        language=Language.PYTHON,
        content="import os\n",
    )

    ruff_output = [
        {
            "code": "F401",
            "message": "`os` imported but unused",
            "location": {
                "row": 1,
                "column": 8,
            },
        }
    ]

    completed_process = Mock(
        stdout=json.dumps(ruff_output),
        stderr="",
        returncode=1,
    )

    with patch(
        "app.analyzers.ruff_analyzer.subprocess.run",
        return_value=completed_process,
    ):
        findings = RuffAnalyzer().analyze(source_file)

    assert len(findings) == 1

    finding = findings[0]

    assert finding.analyzer == "ruff"
    assert finding.rule_id == "F401"
    assert finding.severity == Severity.WARNING
    assert finding.category == Category.STYLE
    assert finding.line == 1
    assert finding.column == 8
    assert finding.message == "`os` imported but unused"


def test_analyze_returns_empty_list_when_ruff_finds_no_issues() -> None:
    source_file = SourceFile(
        path=Path("clean.py"),
        language=Language.PYTHON,
        content="print('Hello')\n",
    )

    completed_process = Mock(
        stdout="[]",
        stderr="",
        returncode=0,
    )

    with patch(
        "app.analyzers.ruff_analyzer.subprocess.run",
        return_value=completed_process,
    ):
        findings = RuffAnalyzer().analyze(source_file)

    assert findings == []


def test_analyze_raises_clear_error_when_ruff_is_not_installed() -> None:
    source_file = SourceFile(
        path=Path("sample.py"),
        language=Language.PYTHON,
        content="print('Hello')\n",
    )

    with patch(
        "app.analyzers.ruff_analyzer.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        with pytest.raises(
            RuntimeError,
            match="Ruff is not installed",
        ):
            RuffAnalyzer().analyze(source_file)


def test_analyze_raises_error_when_ruff_execution_fails() -> None:
    source_file = SourceFile(
        path=Path("sample.py"),
        language=Language.PYTHON,
        content="print('Hello')\n",
    )

    completed_process = Mock(
        stdout="",
        stderr="Invalid Ruff configuration",
        returncode=2,
    )

    with patch(
        "app.analyzers.ruff_analyzer.subprocess.run",
        return_value=completed_process,
    ):
        with pytest.raises(
            RuntimeError,
            match="Ruff execution failed",
        ):
            RuffAnalyzer().analyze(source_file)


def test_f401_maps_to_style_warning() -> None:
    assert map_category("F401") == Category.STYLE
    assert map_severity("F401") == Severity.WARNING


def test_other_f_rules_map_to_bug_error() -> None:
    assert map_category("F821") == Category.BUG
    assert map_severity("F821") == Severity.ERROR
