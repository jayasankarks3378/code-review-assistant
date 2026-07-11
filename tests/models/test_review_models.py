import pytest
from pydantic import ValidationError

from app.models.enums import Category, Priority
from app.models.review_comment import ReviewComment
from app.models.review_response import ReviewResponse


def test_review_response_accepts_valid_data() -> None:
    response = ReviewResponse(
        summary="The code contains one important security concern.",
        comments=[
            ReviewComment(
                title="Avoid shell execution",
                line=5,
                category=Category.SECURITY,
                priority=Priority.HIGH,
                explanation=(
                    "Using shell=True with uncontrolled input may "
                    "allow command injection."
                ),
                recommendation=(
                    "Pass command arguments as a list and avoid shell=True."
                ),
            )
        ],
    )

    assert len(response.comments) == 1
    assert response.comments[0].category == Category.SECURITY
    assert response.comments[0].priority == Priority.HIGH


def test_review_comment_accepts_null_line_for_file_level_issue() -> None:
    comment = ReviewComment(
        title="Improve module documentation",
        line=None,
        category=Category.READABILITY,
        priority=Priority.LOW,
        explanation="The module purpose is not documented.",
        recommendation="Add a concise module-level docstring.",
    )

    assert comment.line is None


def test_review_comment_rejects_non_positive_line_number() -> None:
    with pytest.raises(ValidationError):
        ReviewComment(
            title="Invalid line",
            line=0,
            category=Category.BUG,
            priority=Priority.HIGH,
            explanation="The line value must be positive.",
            recommendation="Provide a valid source-code line.",
        )


def test_review_comment_rejects_unknown_category() -> None:
    with pytest.raises(ValidationError):
        ReviewComment.model_validate(
            {
                "title": "Unknown category",
                "line": 1,
                "category": "maintainability",
                "priority": "medium",
                "explanation": "Invalid category.",
                "recommendation": "Use a supported category.",
            }
        )


def test_review_comment_rejects_unexpected_fields() -> None:
    with pytest.raises(ValidationError):
        ReviewComment.model_validate(
            {
                "title": "Unsafe shell execution",
                "line": 5,
                "category": "security",
                "priority": "high",
                "explanation": "Command injection may be possible.",
                "recommendation": "Avoid shell=True.",
                "confidence": 0.95,
            }
        )


def test_review_response_accepts_empty_comment_list() -> None:
    response = ReviewResponse(
        summary="No significant issues were identified.",
        comments=[],
    )

    assert response.comments == []


def test_review_response_validates_json_string() -> None:
    raw_response = """
    {
      "summary": "One issue was identified.",
      "comments": [
        {
          "title": "Unused import",
          "line": 1,
          "category": "style",
          "priority": "low",
          "explanation": "The import is not used.",
          "recommendation": "Remove the unused import."
        }
      ]
    }
    """

    response = ReviewResponse.model_validate_json(raw_response)

    assert response.summary == "One issue was identified."
    assert response.comments[0].line == 1
