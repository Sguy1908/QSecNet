"""Security report persistence and export endpoints."""

import csv
import io
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.security import SecurityAnalysisResponse
from backend.api.simulations import SimulationResponse
from backend.api.topologies import TopologyCreate
from backend.database.session import get_session
from backend.models.records import ReportRecord
from backend.recommendation_engine.engine import RecommendationItem

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportCreateRequest(BaseModel):
    topology: TopologyCreate
    simulation: SimulationResponse
    analysis: SecurityAnalysisResponse
    recommendations: list[RecommendationItem]


class ReportResponse(BaseModel):
    id: str
    created_at: datetime
    payload: dict[str, Any]


@router.post("", response_model=ReportResponse)
def create_report(payload: ReportCreateRequest, session: Session = Depends(get_session)) -> ReportResponse:
    """Create and persist a structured security report."""
    report_payload = {
        "topology": payload.topology.model_dump(mode="json"),
        "simulation": payload.simulation.model_dump(mode="json"),
        "analysis": payload.analysis.model_dump(mode="json"),
        "recommendations": [item.model_dump(mode="json") for item in payload.recommendations],
    }
    report = ReportRecord(
        topology_id=payload.simulation.metadata.get("topology_id") if payload.simulation.metadata else None,
        simulation_id=payload.simulation.id,
        analysis_id=payload.analysis.id,
        payload=report_payload,
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    return ReportResponse(id=report.id, created_at=report.created_at, payload=report_payload)


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, session: Session = Depends(get_session)) -> ReportResponse:
    """Fetch one report object."""
    report = session.get(ReportRecord, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportResponse(id=report.id, created_at=report.created_at, payload=report.payload)


@router.get("/{report_id}/export")
def export_report(
    report_id: str,
    format: str = Query(default="json", pattern="^(json|csv)$"),
    session: Session = Depends(get_session),
) -> Response:
    """Export report as JSON or CSV."""
    report = session.get(ReportRecord, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    if format == "json":
        return JSONResponse(content=report.payload)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value"])
    analysis = report.payload.get("analysis", {})
    for key, value in analysis.items():
        writer.writerow([key, value])
    writer.writerow([])
    writer.writerow(["recommendation_rank", "action", "priority", "reason"])
    for item in report.payload.get("recommendations", []):
        writer.writerow([item.get("rank"), item.get("action"), item.get("priority"), item.get("reason")])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="report-{report.id}.csv"'},
    )
