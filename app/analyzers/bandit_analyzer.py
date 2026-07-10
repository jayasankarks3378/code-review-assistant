import json
import subprocess
import tempfile
from pathlib import Path

from app.analyzers.base_analyzer import BaseAnalyzer
from app.models.enums import Category, Severity
from app.models.finding import Finding
from app.models.source_file import SourceFile


class BanditAnalyzer(BaseAnalyzer):
    """Analyze Python source code for potential security issues."""

    @staticmethod
    def _to_finding(item: dict) -> Finding:
        """Convert one Bandit result into the internal Finding model."""

        return Finding(
            analyzer="bandit",
            rule_id=item["test_id"],
            severity=BanditAnalyzer._map_severity(item["issue_severity"]),
            category=Category.SECURITY,
            line=item["line_number"],
            column=item.get("col_offset", 0) + 1,
            message=item["issue_text"],
            suggestion=None,
        )

    @staticmethod
    def _map_severity(value: str) -> Severity:
        """Map Bandit severity values to internal severity levels."""

        severity_mapping = {
            "LOW": Severity.INFO,
            "MEDIUM": Severity.WARNING,
            "HIGH": Severity.ERROR,
        }

        return severity_mapping.get(
            value.upper(),
            Severity.WARNING,
        )

    def analyze(self, source_file: SourceFile) -> list[Finding]:
        """Run Bandit and return normalized security findings."""

        temp_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                encoding=source_file.encoding,
                delete=False,
            ) as temp_file:
                temp_file.write(source_file.content)
                temp_path = Path(temp_file.name)

            result = subprocess.run(
                [
                    "bandit",
                    str(temp_path),
                    "-f",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode not in (0, 1):
                raise RuntimeError(f"Bandit execution failed: {result.stderr.strip()}")

            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                raise RuntimeError("Bandit returned invalid JSON output.") from exc

            return [self._to_finding(item) for item in output.get("results", [])]

        except FileNotFoundError as exc:
            raise RuntimeError(
                "Bandit is not installed or is not available in PATH."
            ) from exc

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
