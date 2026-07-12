from app.analyzers.bandit_analyzer import BanditAnalyzer
from app.analyzers.ruff_analyzer import RuffAnalyzer
from app.config import get_settings
from app.llm.ollama_llm import OllamaLLM
from app.services.analysis_service import AnalysisService
from app.services.review_service import ReviewService
from app.parser.python_parser import PythonParser
from app.prompts.review_prompt_builder import ReviewPromptBuilder
from app.response.review_response_parser import ReviewResponseParser
from app.models.enums import ReportFormat
from app.reports.json_report_generator import JsonReportGenerator
from app.reports.markdown_report_generator import MarkdownReportGenerator
from app.services.report_service import ReportService


class ApplicationContainer:
    """Create and wire together application dependencies."""

    def __init__(self) -> None:
        settings = get_settings()

        self.parser = PythonParser(
            max_lines=settings.max_source_lines,
        )

        self.analysis_service = AnalysisService(
            analyzers=[
                RuffAnalyzer(),
                BanditAnalyzer(),
            ]
        )

        self.prompt_builder = ReviewPromptBuilder(
            max_findings=settings.max_prompt_findings,
        )

        self.llm = OllamaLLM(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout=settings.ollama_timeout_seconds,
        )

        self.response_parser = ReviewResponseParser()

        self.review_service = ReviewService(
            prompt_builder=self.prompt_builder,
            llm=self.llm,
            response_parser=self.response_parser,
        )

        self.report_service = ReportService(
            generators={
                ReportFormat.MARKDOWN: MarkdownReportGenerator(),
                ReportFormat.JSON: JsonReportGenerator(),
            }
        )
