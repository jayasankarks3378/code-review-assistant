from app.models.analysis_result import AnalysisResult
from app.models.review_response import ReviewResponse
from app.models.source_file import SourceFile
from app.reports.base_report_generator import BaseReportGenerator


class MarkdownReportGenerator(BaseReportGenerator):
    """Generate a human-readable Markdown code-review report."""

    def generate(
        self,
        source_file: SourceFile,
        analysis_result: AnalysisResult,
        review_response: ReviewResponse,
    ) -> str:
        """Generate the complete Markdown report."""

        sections = [
            self._build_header(source_file),
            self._build_summary(review_response),
            self._build_analysis_section(analysis_result),
            self._build_review_comments(review_response),
            self._build_limitations(analysis_result),
        ]

        return "\n\n".join(sections).strip() + "\n"

    @staticmethod
    def _build_header(source_file: SourceFile) -> str:
        """Build report metadata."""

        return "\n".join(
            [
                "# Code Review Report",
                "",
                f"**File:** `{source_file.path}`  ",
                f"**Language:** {source_file.language.value}  ",
                f"**Lines:** {source_file.line_count}",
            ]
        )

    @staticmethod
    def _build_summary(review_response: ReviewResponse) -> str:
        """Build the AI summary section."""

        return "\n".join(
            [
                "## Review Summary",
                "",
                review_response.summary,
            ]
        )

    @staticmethod
    def _build_analysis_section(
        analysis_result: AnalysisResult,
    ) -> str:
        """Build the static-analysis section."""

        lines = [
            "## Static Analysis",
            "",
            f"- **Status:** "
            f"{'Successful' if analysis_result.success else 'Partial failure'}",
            f"- **Findings:** {len(analysis_result.findings)}",
            f"- **Execution time:** " f"{analysis_result.execution_time_ms:.2f} ms",
            "- **Analyzers completed:** "
            + (
                ", ".join(analysis_result.analyzers_run)
                if analysis_result.analyzers_run
                else "None"
            ),
        ]

        if analysis_result.findings:
            lines.extend(
                [
                    "",
                    "### Detected Findings",
                    "",
                ]
            )

            for finding in analysis_result.findings:
                location = f"line {finding.line}"

                if finding.column is not None:
                    location += f", column {finding.column}"

                lines.append(
                    (
                        f"- **{finding.rule_id}** "
                        f"({finding.category.value}, "
                        f"{finding.severity.value}) at {location}: "
                        f"{finding.message}"
                    )
                )

        return "\n".join(lines)

    @staticmethod
    def _build_review_comments(
        review_response: ReviewResponse,
    ) -> str:
        """Build the AI-generated review comments section."""

        lines = [
            "## AI Review Comments",
            "",
        ]

        if not review_response.comments:
            lines.append("No actionable review comments were generated.")
            return "\n".join(lines)

        for index, comment in enumerate(
            review_response.comments,
            start=1,
        ):
            location = (
                f"Line {comment.line}" if comment.line is not None else "File-level"
            )

            lines.extend(
                [
                    f"### {index}. {comment.title}",
                    "",
                    f"- **Category:** {comment.category.value}",
                    f"- **Priority:** {comment.priority.value}",
                    f"- **Location:** {location}",
                    "",
                    "**Explanation**",
                    "",
                    comment.explanation,
                    "",
                    "**Recommendation**",
                    "",
                    comment.recommendation,
                    "",
                ]
            )

        return "\n".join(lines).rstrip()

    @staticmethod
    def _build_limitations(
        analysis_result: AnalysisResult,
    ) -> str:
        """Build analyzer-error and limitation details."""

        lines = [
            "## Analysis Limitations",
            "",
        ]

        if not analysis_result.errors:
            lines.append("All configured static analyzers completed successfully.")
            return "\n".join(lines)

        lines.append("The following analyzer errors may have reduced review coverage:")
        lines.append("")

        lines.extend(f"- {error}" for error in analysis_result.errors)

        return "\n".join(lines)
