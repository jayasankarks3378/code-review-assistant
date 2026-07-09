from abc import ABC, abstractmethod
from ast import AST

from app.models.source_file import SourceFile


class BaseParser(ABC):
    """
    Abstract base class for language-specific parsers.
    """

    @abstractmethod
    def validate(self, source_file: SourceFile) -> None:
        """
        Validate that the source file can be parsed.

        Raises:
            ValueError: If the source file is invalid.
        """
        raise NotImplementedError

    @abstractmethod
    def parse(self, source_file: SourceFile) -> AST:
        """
        Parse the source file into an Abstract Syntax Tree.

        Returns:
            AST: Parsed syntax tree.
        """
        raise NotImplementedError