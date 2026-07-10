import pytest

from app.models.enums import Category, Priority
from app.response.review_response_parser import ReviewResponseParser


def test_parse_returns_validated_review_response() -> None:
    raw_response = """
    {
      "summary": "One issue was identified.",
      "comments": [
        {
          "title": "Remove unused import",
          "line": 1,
          "category": "style",
          "priority": "low",
          "explanation": "The import is not used.",
          "recommendation": "Remove the unused import."
        }
      ]
    }
    """

    response = ReviewResponseParser().parse(raw_response)

    assert response.summary == "One issue was identified."
    assert len(response.comments) == 1
    assert response.comments[0].category == Category.STYLE
    assert response.comments[0].priority == Priority.LOW


def test_parse_accepts_json_markdown_fence() -> None:
    raw_response = """
```json
{
  "summary": "No significant issues were found.",
  "comments": []
}
```
"""

    response = ReviewResponseParser().parse(raw_response)

    assert response.summary == "No significant issues were found."
    assert response.comments == []


def test_parse_accepts_plain_markdown_fence() -> None:
    raw_response = """
{
  "summary": "Review complete.",
  "comments": []
}
"""

    response = ReviewResponseParser().parse(raw_response)

    assert response.summary == "Review complete."
    assert response.comments == []


def test_parse_rejects_empty_response() -> None:
    with pytest.raises(
        ValueError,
        match="LLM response must not be empty",
    ):
        ReviewResponseParser().parse(" ")


def test_parse_rejects_invalid_json() -> None:
    with pytest.raises(
        ValueError,
        match="expected JSON contract",
    ):
        ReviewResponseParser().parse("not valid json")


def test_parse_rejects_missing_required_fields() -> None:
    raw_response = """
{
  "comments": []
}
"""

    with pytest.raises(
        ValueError,
        match="expected JSON contract",
    ):
        ReviewResponseParser().parse(raw_response)


def test_parse_rejects_invalid_comment_category() -> None:
    raw_response = """
{
  "summary": "Review complete.",
  "comments": [
    {
      "title": "Unknown issue type",
      "line": 1,
      "category": "maintainability",
      "priority": "medium",
      "explanation": "This category is unsupported.",
      "recommendation": "Use a supported category."
    }
  ]
}
"""

    with pytest.raises(
        ValueError,
        match="expected JSON contract",
    ):
        ReviewResponseParser().parse(raw_response)


def test_parse_rejects_non_positive_line_number() -> None:
    raw_response = """
{
  "summary": "Review complete.",
  "comments": [
    {
      "title": "Invalid line",
      "line": 0,
      "category": "bug",
      "priority": "high",
      "explanation": "Line numbers must be positive.",
      "recommendation": "Provide a valid line number."
    }
  ]
}
"""

    with pytest.raises(
        ValueError,
        match="expected JSON contract",
    ):
        ReviewResponseParser().parse(raw_response)


def test_parse_accepts_null_line_for_file_level_comment() -> None:
    raw_response = """
{
  "summary": "One file-level issue was identified.",
  "comments": [
    {
      "title": "Add module documentation",
      "line": null,
      "category": "readability",
      "priority": "low",
      "explanation": "The module purpose is not documented.",
      "recommendation": "Add a concise module-level docstring."
    }
  ]
}
"""

    response = ReviewResponseParser().parse(raw_response)

    assert response.comments[0].line is None


def test_parse_rejects_unexpected_top_level_fields() -> None:
    raw_response = """
{
  "summary": "Review complete.",
  "comments": [],
  "model_name": "example-model"
}
"""

    with pytest.raises(
        ValueError,
        match="expected JSON contract",
    ):
        ReviewResponseParser().parse(raw_response)


def test_parse_rejects_unexpected_comment_fields() -> None:
    raw_response = """
{
  "summary": "Review complete.",
  "comments": [
    {
      "title": "Unsafe shell execution",
      "line": 5,
      "category": "security",
      "priority": "high",
      "explanation": "Command injection may be possible.",
      "recommendation": "Avoid shell=True.",
      "confidence": 0.95
    }
  ]
}
"""

    with pytest.raises(
        ValueError,
        match="expected JSON contract",
    ):
        ReviewResponseParser().parse(raw_response)
