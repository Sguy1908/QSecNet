from datetime import UTC, datetime
from types import SimpleNamespace

from backend.models import RiskLevel
from backend.services.report_export import report_csv, report_document, report_pdf


def test_report_exports_are_readable_and_include_metrics() -> None:
    report = SimpleNamespace(
        id="report-1",
        simulation_id="sim-1",
        security_score=88.0,
        risk_level=RiskLevel.LOW, metrics={"qber": 0.01}, created_at=datetime.now(UTC),
    )
    recommendation = SimpleNamespace(
        title="Monitor", description="Continue monitoring", priority=RiskLevel.LOW, category="monitoring"
    )
    document = report_document(report, [recommendation])

    assert "qber" in report_csv(document)
    assert report_pdf(document).startswith(b"%PDF-1.4")
