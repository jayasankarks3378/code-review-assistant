from app.bootstrap.container import ApplicationContainer
from app.services.analysis_service import AnalysisService
from app.services.review_service import ReviewService


def test_container_creates_application() -> None:
    container = ApplicationContainer()

    assert isinstance(
        container.analysis_service,
        AnalysisService,
    )

    assert isinstance(
        container.review_service,
        ReviewService,
    )
