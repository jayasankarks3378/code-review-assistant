from app.bootstrap.container import ApplicationContainer
from app.services.analysis_service import AnalysisService
from app.services.review_service import ReviewService
from app.services.report_service import ReportService


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

    assert isinstance(
        container.report_service,
        ReportService,
    )
