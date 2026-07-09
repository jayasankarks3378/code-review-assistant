from abc import ABC, abstractmethod

from app.models.finding import Finding
from app.models.source_file import SourceFile


class BaseAnalyzer(ABC):
    """
    Base interface for all static analyzers.
    """

    @abstractmethod
    def analyze(self, source_file: SourceFile) -> list[Finding]:
        """
        Analyze a source file.

        Returns:
            A normalized list of findings.
        """
        raise NotImplementedError