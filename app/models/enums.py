from enum import Enum


class Language(str, Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"


class Severity(str, Enum):
    """Severity levels for analysis findings."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Category(str, Enum):
    """Categories of issues detected during analysis."""

    BUG = "bug"
    STYLE = "style"
    SECURITY = "security"
    PERFORMANCE = "performance"
    READABILITY = "readability"


class Priority(str, Enum):
    """Priority assigned to AI review comments."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
