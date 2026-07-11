import ast

from app.models.enums import Language
from app.models.source_file import SourceFile
from app.parser.base_parser import BaseParser


class PythonParser(BaseParser):
    """Parser implementation for Python source files."""

    def __init__(self, max_lines: int = 500) -> None:
        """
        Initialize the parser.

        Args:
            max_lines: Maximum number of source-code lines accepted.

        Raises:
            ValueError: If max_lines is less than 1.
        """
        if max_lines < 1:
            raise ValueError("max_lines must be at least 1.")

        self._max_lines = max_lines

    def validate(self, source_file: SourceFile) -> None:
        """
        Validate the source file before parsing.

        Args:
            source_file: Source file to validate.

        Raises:
            ValueError: If the language is unsupported or the file
                exceeds the configured line limit.
        """
        if source_file.language != Language.PYTHON:
            raise ValueError(f"Unsupported language: {source_file.language.value}")

        if source_file.line_count > self._max_lines:
            raise ValueError("File exceeds maximum size " f"({self._max_lines} lines).")

    def parse(self, source_file: SourceFile) -> ast.AST:
        """
        Parse Python source code into an AST.

        Args:
            source_file: Python source file to parse.

        Returns:
            Parsed Python abstract syntax tree.

        Raises:
            ValueError: If validation fails or the source contains
                invalid Python syntax.
        """
        self.validate(source_file)

        try:
            return ast.parse(
                source_file.content,
                filename=str(source_file.path),
            )
        except SyntaxError as exc:
            raise ValueError(f"Invalid Python syntax: {exc.msg}") from exc
