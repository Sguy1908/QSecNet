"""Downloadable security-report exports."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_session
from backend.models import Recommendation, SecurityReport
from backend.services.report_export import report_csv, report_document, report_pdf

router = APIRouter(tags=["Exports"])


def _document_or_404(session: Session, report_id: str) -> dict[str, object]:
    report = session.get(SecurityReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Security report '{report_id}' was not found.")
    recommendations = list(
        session.scalars(select(Recommendation).where(Recommendation.report_id == report_id))
    )
    return report_document(report, recommendations)


@router.get("/security-reports/{report_id}/export/json")
def export_json(report_id: str, session: Session = Depends(get_session)) -> JSONResponse:
    """Download an interoperable JSON security report."""
    return JSONResponse(_document_or_404(session, report_id))


@router.get("/security-reports/{report_id}/export/csv")
def export_csv(report_id: str, session: Session = Depends(get_session)) -> Response:
    """Download flattened report metrics as CSV."""
    content = report_csv(_document_or_404(session, report_id))
    return Response(
        content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="qsecnet-report-{report_id}.csv"'},
    )


@router.get("/security-reports/{report_id}/export/pdf")
def export_pdf(report_id: str, session: Session = Depends(get_session)) -> Response:
    """Download a portable PDF security report."""
    content = report_pdf(_document_or_404(session, report_id))
    return Response(
        content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="qsecnet-report-{report_id}.pdf"'},
    )
