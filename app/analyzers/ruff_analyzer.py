import json
import subprocess
import tempfile
from pathlib import Path

from app.analyzers.base_analyzer import BaseAnalyzer
from app.models.enums import Category, Severity
from app.models.finding import Finding
from app.models.source_file import SourceFile


def map_category(rule_id: str) -> Category:
    if rule_id.startswith("F"):
        return Category.BUG

    if rule_id.startswith(("E", "W")):
        return Category.STYLE

    if rule_id.startswith("PERF"):
        return Category.PERFORMANCE

    if rule_id.startswith(("SIM", "UP")):
        return Category.READABILITY

    return Category.STYLE


def map_severity(rule_id: str) -> Severity:
    if rule_id.startswith("F"):
        return Severity.ERROR

    return Severity.WARNING


class RuffAnalyzer(BaseAnalyzer):
    def analyze(self, source_file: SourceFile) -> list[Finding]:
        temp_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".py",
                mode="w",
                encoding=source_file.encoding,
                delete=False,
            ) as temp_file:
                temp_file.write(source_file.content)
                temp_path = Path(temp_file.name)

            try:
                result = subprocess.run(
                    [
                        "ruff",
                        "check",
                        str(temp_path),
                        "--output-format",
                        "json",
                    ],
                    capture_output=True,
                    text=True,
                )
            except FileNotFoundError as exc:
                raise RuntimeError(
                    "Ruff is not installed or not available in PATH."
                ) from exc

            if result.returncode not in (0, 1):
                raise RuntimeError(f"Ruff execution failed: {result.stderr.strip()}")

            try:
                diagnostics = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                raise RuntimeError("Ruff returned malformed JSON output.") from exc

            findings: list[Finding] = []

            for item in diagnostics:
                rule_id = item["code"]

                findings.append(
                    Finding(
                        analyzer="ruff",
                        rule_id=rule_id,
                        severity=map_severity(rule_id),
                        category=map_category(rule_id),
                        line=item["location"]["row"],
                        column=item["location"]["column"],
                        message=item["message"],
                        suggestion=None,
                    )
                )

            return findings

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
