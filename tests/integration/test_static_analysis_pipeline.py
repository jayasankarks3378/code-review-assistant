from pathlib import Path

import pytest

from app.analyzers.bandit_analyzer import BanditAnalyzer
from app.analyzers.ruff_analyzer import RuffAnalyzer
from app.models.enums import Category, Language
from app.models.source_file import SourceFile
from app.services.analysis_service import AnalysisService


@pytest.mark.integration
def test_static_analysis_pipeline_detects_real_issues() -> None:
    source_file = SourceFile(
        path=Path("vulnerable_sample.py"),
        language=Language.PYTHON,
        content=(
            "import os\n"
            "import subprocess\n\n"
            "def execute(command):\n"
            "    subprocess.run(command, shell=True)\n"
        ),
    )

    service = AnalysisService(
        analyzers=[
            RuffAnalyzer(),
            BanditAnalyzer(),
        ]
    )

    result = service.analyze(source_file)

    assert result.success is True
    assert result.findings
    assert len(result.analyzers_run) == 2

    analyzer_names = {finding.analyzer for finding in result.findings}

    assert "ruff" in analyzer_names
    assert "bandit" in analyzer_names

    categories = {finding.category for finding in result.findings}

    assert Category.SECURITY in categories
