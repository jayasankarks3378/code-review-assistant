from abc import ABC, abstractmethod

from app.models.analysis_result import AnalysisResult
from app.models.review_response import ReviewResponse
from app.models.source_file import SourceFile


class BaseReportGenerator(ABC):
    """Define the contract for review report generators."""

    @abstractmethod
    def generate(
        self,
        source_file: SourceFile,
        analysis_result: AnalysisResult,
        review_response: ReviewResponse,
    ) -> str:
        """
        Generate a formatted review report.

        Args:
            source_file: Source file that was reviewed.
            analysis_result: Static-analysis results.
            review_response: Validated AI review response.

        Returns:
            Formatted report content.
        """
        raise NotImplementedError
