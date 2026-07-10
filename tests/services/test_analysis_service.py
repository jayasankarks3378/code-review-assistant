from pathlib import Path

from app.analyzers.base_analyzer import BaseAnalyzer
from app.models.enums import Category, Language, Severity
from app.models.finding import Finding
from app.models.source_file import SourceFile
from app.orchestrator.analysis_service import AnalysisService


class SuccessfulAnalyzer(BaseAnalyzer):
    def analyze(
        self,
        source_file: SourceFile,
    ) -> list[Finding]:
        return [
            Finding(
                analyzer="fake",
                rule_id="TEST001",
                severity=Severity.WARNING,
                category=Category.STYLE,
                line=1,
                column=1,
                message="Example finding",
                suggestion=None,
            )
        ]


class FailingAnalyzer(BaseAnalyzer):
    def analyze(
        self,
        source_file: SourceFile,
    ) -> list[Finding]:
        raise RuntimeError("Analyzer failed")


def create_source_file() -> SourceFile:
    return SourceFile(
        path=Path("sample.py"),
        language=Language.PYTHON,
        content="print('Hello')\n",
    )


def test_analyze_combines_findings_from_multiple_analyzers() -> None:
    service = AnalysisService(
        analyzers=[
            SuccessfulAnalyzer(),
            SuccessfulAnalyzer(),
        ]
    )

    result = service.analyze(create_source_file())

    assert result.success is True
    assert len(result.findings) == 2
    assert len(result.analyzers_run) == 2
    assert result.errors == []
    assert result.execution_time_ms >= 0


def test_analyze_returns_partial_results_when_analyzer_fails() -> None:
    service = AnalysisService(
        analyzers=[
            SuccessfulAnalyzer(),
            FailingAnalyzer(),
        ]
    )

    result = service.analyze(create_source_file())

    assert result.success is False
    assert len(result.findings) == 1
    assert result.analyzers_run == ["SuccessfulAnalyzer"]
    assert len(result.errors) == 1
    assert "FailingAnalyzer" in result.errors[0]
    assert "Analyzer failed" in result.errors[0]


def test_analyze_returns_empty_result_when_no_analyzers_are_configured() -> None:
    service = AnalysisService(analyzers=[])

    result = service.analyze(create_source_file())

    assert result.success is True
    assert result.findings == []
    assert result.analyzers_run == []
    assert result.errors == []
