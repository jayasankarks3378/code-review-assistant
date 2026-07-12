from pathlib import Path


def generate_large_python_file() -> str:
    """Generate a Python source file of roughly 500 lines."""

    lines = []

    for index in range(250):
        lines.append(f"def function_{index}():")
        lines.append(f"    return {index}")

    return "\n".join(lines)


import time
from pathlib import Path

import pytest

from app.analyzers.bandit_analyzer import BanditAnalyzer
from app.analyzers.ruff_analyzer import RuffAnalyzer
from app.models.enums import Language
from app.models.source_file import SourceFile
from app.parser.python_parser import PythonParser
from app.services.analysis_service import AnalysisService


@pytest.mark.performance
def test_large_file_analysis_performance() -> None:
    source_file = SourceFile(
        path=Path("large_file.py"),
        language=Language.PYTHON,
        content=generate_large_python_file(),
    )

    parser = PythonParser(max_lines=600)

    analysis_service = AnalysisService(
        analyzers=[
            RuffAnalyzer(),
            BanditAnalyzer(),
        ]
    )

    start = time.perf_counter()

    parser.parse(source_file)

    analysis_result = analysis_service.analyze(source_file)

    elapsed = time.perf_counter() - start

    assert analysis_result.success is True

    print(f"\nAnalysis time: {elapsed:.3f} seconds")

    assert elapsed < 5

    assert source_file.line_count >= 500

    assert analysis_result.analyzers_run == [
        "RuffAnalyzer",
        "BanditAnalyzer",
    ]