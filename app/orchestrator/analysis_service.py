from time import perf_counter

from app.analyzers.base_analyzer import BaseAnalyzer
from app.models.analysis_result import AnalysisResult
from app.models.finding import Finding
from app.models.source_file import SourceFile


class AnalysisService:
    """Coordinate multiple static analyzers."""

    def __init__(self, analyzers: list[BaseAnalyzer]) -> None:
        self._analyzers = analyzers

    def analyze(self, source_file: SourceFile) -> AnalysisResult:
        """Run all configured analyzers against one source file."""

        start_time = perf_counter()

        findings: list[Finding] = []
        analyzers_run: list[str] = []
        errors: list[str] = []

        for analyzer in self._analyzers:
            analyzer_name = analyzer.__class__.__name__

            try:
                analyzer_findings = analyzer.analyze(source_file)
            except RuntimeError as exc:
                errors.append(f"{analyzer_name}: {exc}")
                continue

            findings.extend(analyzer_findings)
            analyzers_run.append(analyzer_name)

        execution_time_ms = (perf_counter() - start_time) * 1000

        return AnalysisResult(
            findings=findings,
            analyzers_run=analyzers_run,
            errors=errors,
            execution_time_ms=execution_time_ms,
        )
