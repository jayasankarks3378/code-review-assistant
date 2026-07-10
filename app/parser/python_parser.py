import ast

from app.models.enums import Language
from app.models.source_file import SourceFile
from app.parser.base_parser import BaseParser


class PythonParser(BaseParser):
    """
    Parser implementation for Python source files.
    """

    MAX_LINES = 500

    def validate(self, source_file: SourceFile) -> None:
        """
        Validate the source file before parsing.
        """
        if source_file.language != Language.PYTHON:
            raise ValueError(f"Unsupported language: {source_file.language}")

        if source_file.line_count > self.MAX_LINES:
            raise ValueError(f"File exceeds maximum size ({self.MAX_LINES} lines).")

    def parse(self, source_file: SourceFile) -> ast.AST:
        """
        Parse Python source code into an AST.
        """
        self.validate(source_file)

        try:
            return ast.parse(
                source_file.content,
                filename=str(source_file.path),
            )

        except SyntaxError as exc:
            raise ValueError(f"Invalid Python syntax: {exc.msg}") from exc
