from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from app.bootstrap.container import ApplicationContainer
from app.exceptions import CodeReviewAssistantError
from app.models.enums import Language, ReportFormat
from app.models.source_file import SourceFile

app = typer.Typer(
    help="AI-powered Python code review assistant.",
    no_args_is_help=True,
)

console = Console()


@app.command()
def review(
    file_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to the Python source file to review.",
    ),
    report_format: ReportFormat = typer.Option(
        ReportFormat.MARKDOWN,
        "--format",
        "-f",
        help="Output report format.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional file path where the report should be saved.",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Allow replacement of an existing output file.",
    ),
) -> None:
    """Analyze a Python file and generate an AI-assisted review report."""

    if file_path.suffix.lower() != ".py":
        console.print("[red]Error:[/red] Only Python files are currently supported.")
        raise typer.Exit(code=1)

    container = ApplicationContainer()

    try:
        source_file = _load_source_file(file_path)

        container.parser.parse(source_file)

        analysis_result = container.analysis_service.analyze(source_file)

        review_response = container.review_service.review(
            source_file=source_file,
            analysis_result=analysis_result,
        )

        report_content = container.report_service.generate(
            report_format=report_format,
            source_file=source_file,
            analysis_result=analysis_result,
            review_response=review_response,
        )

        if output is not None:
            written_path = container.report_service.write(
                report_content=report_content,
                output_path=output,
                overwrite=overwrite,
            )

            console.print(
                Panel(
                    f"Report saved to:\n{written_path}",
                    title="Code Review Complete",
                )
            )
        else:
            console.print(report_content)

    except UnicodeDecodeError:
        console.print(
            "[red]Error:[/red] The source file could not be decoded as UTF-8."
        )
        raise typer.Exit(code=1) from None

    except FileExistsError as exc:
        console.print(
            f"[red]Output error:[/red] {exc}\n"
            "Use --overwrite to replace the existing file."
        )
        raise typer.Exit(code=1) from exc

    except CodeReviewAssistantError as exc:
        console.print(f"[red]Application error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    except ValueError as exc:
        console.print(f"[red]Validation error:[/red] {exc}")
        raise typer.Exit(code=1) from exc


def _load_source_file(file_path: Path) -> SourceFile:
    """Read a Python file and create the internal source model."""

    content = file_path.read_text(encoding="utf-8")

    return SourceFile(
        path=file_path,
        language=Language.PYTHON,
        content=content,
        encoding="utf-8",
    )


if __name__ == "__main__":
    app()
