import json

from app.models.analysis_result import AnalysisResult
from app.models.review_response import ReviewResponse
from app.models.source_file import SourceFile
from app.reports.base_report_generator import BaseReportGenerator


class JsonReportGenerator(BaseReportGenerator):
    """Generate a machine-readable JSON code-review report."""

    def generate(
        self,
        source_file: SourceFile,
        analysis_result: AnalysisResult,
        review_response: ReviewResponse,
    ) -> str:
        """Generate the complete JSON report."""

        report = {
            "source_file": {
                "path": str(source_file.path),
                "language": source_file.language.value,
                "line_count": source_file.line_count,
                "encoding": source_file.encoding,
            },
            "static_analysis": analysis_result.model_dump(mode="json"),
            "ai_review": review_response.model_dump(mode="json"),
        }

        return json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
