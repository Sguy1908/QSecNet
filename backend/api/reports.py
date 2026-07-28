"""Security report storage and JSON/CSV export endpoints."""

import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.api.security import SecurityAnalysisResponse
from backend.database.session import get_session
from backend.models.topology import SecurityReport

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    analysis: SecurityAnalysisResponse
    topology_id: str | None = None
    simulation_id: str | None = None


class ReportRead(ReportCreate):
    id: str
    created_at: datetime


def serialize(record: SecurityReport) -> ReportRead:
    """Convert JSON persistence fields back to a typed response."""
    return ReportRead(id=record.id, created_at=record.created_at, **record.content)


@router.post("", response_model=ReportRead, status_code=201)
def create_report(payload: ReportCreate, session: Session = Depends(get_session)) -> ReportRead:
    """Store a portable snapshot of the security assessment."""
    record = SecurityReport(
        title=payload.title,
        analysis_id=payload.analysis.id,
        content=payload.model_dump(mode="json"),
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return serialize(record)


@router.get("", response_model=list[ReportRead])
def list_reports(session: Session = Depends(get_session)) -> list[ReportRead]:
    """List reports newest first."""
    records = session.scalars(select(SecurityReport).order_by(SecurityReport.created_at.desc())).all()
    return [serialize(record) for record in records]


@router.get("/{report_id}", response_model=ReportRead)
def get_report(report_id: str, session: Session = Depends(get_session)) -> ReportRead:
    """Retrieve one report."""
    record = session.get(SecurityReport, report_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return serialize(record)


@router.get("/{report_id}/export/{format}")
def export_report(report_id: str, format: str, session: Session = Depends(get_session)) -> Response:
    """Export a report as JSON or a flat, spreadsheet-compatible CSV document."""
    report = get_report(report_id, session)
    if format == "json":
        body = json.dumps(report.model_dump(mode="json"), indent=2)
        return Response(body, media_type="application/json")
    if format == "csv":
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(["metric", "value"])
        for key, value in report.analysis.model_dump(mode="json").items():
            writer.writerow([key, json.dumps(value) if isinstance(value, (list, dict)) else value])
        return Response(stream.getvalue(), media_type="text/csv")
    raise HTTPException(status_code=422, detail="format must be json or csv")
