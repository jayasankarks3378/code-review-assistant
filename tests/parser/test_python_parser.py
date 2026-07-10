import ast

import pytest

from app.models.enums import Language
from app.models.source_file import SourceFile
from app.parser.python_parser import PythonParser


@pytest.fixture
def parser() -> PythonParser:
    """Return a fresh parser for each test."""
    return PythonParser()


def test_parse_returns_ast_for_valid_python(parser: PythonParser):
    source = SourceFile(
        path="example.py",
        language=Language.PYTHON,
        content="""
def add(a, b):
    return a + b
""",
    )

    tree = parser.parse(source)

    assert isinstance(tree, ast.AST)


def test_parse_raises_error_for_invalid_syntax(parser: PythonParser):

    source = SourceFile(
        path="broken.py",
        language=Language.PYTHON,
        content="def hello(",
    )

    with pytest.raises(ValueError, match="Invalid Python syntax"):
        parser.parse(source)


def test_validate_rejects_large_file(parser: PythonParser):
    source = SourceFile(
        path="large.py",
        language=Language.PYTHON,
        content="\n".join(["print(1)"] * 501),
    )

    with pytest.raises(ValueError, match="maximum size"):
        parser.parse(source)


def test_validate_rejects_unsupported_language(parser: PythonParser):

    source = SourceFile(
        path="example.txt",
        language="javascript",  # Intentional invalid value for this test
        content="console.log('Hello');",
    )

    with pytest.raises(ValueError):
        parser.validate(source)


def test_parse_accepts_empty_file(parser: PythonParser):
    source = SourceFile(
        path="empty.py",
        language=Language.PYTHON,
        content="",
    )

    tree = parser.parse(source)

    assert isinstance(tree, ast.Module)
