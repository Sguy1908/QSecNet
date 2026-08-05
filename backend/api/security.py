"""Security report creation and retrieval endpoints."""

<<<<<<< HEAD
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session
=======
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.analyzer.security import analyze_security
from backend.api.simulations import SimulationResponse
from backend.api.topologies import TopologyCreate
from backend.database.session import get_session
from backend.models.records import AnalysisRecord, RecommendationRecord
from backend.recommendation_engine.engine import RecommendationItem, recommend_ranked
>>>>>>> origin/main

from backend.analyzer.security import assess_security
from backend.database import get_session
from backend.models import (
    Attack,
    Node,
    QuantumLink,
    RiskLevel,
    SecurityReport,
    Simulation,
    SimulationStatus,
)

router = APIRouter(tags=["Security reports"])


class SecurityReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

<<<<<<< HEAD
    id: str
    simulation_id: str
    security_score: float
    risk_level: RiskLevel
    metrics: dict[str, Any]


@router.post(
    "/simulations/{simulation_id}/security-reports",
    response_model=SecurityReportRead,
    status_code=status.HTTP_201_CREATED,
)
def create_security_report(
    simulation_id: str, session: Session = Depends(get_session)
) -> SecurityReport:
    """Calculate and persist a security report from current simulation context."""
    simulation = session.get(Simulation, simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail=f"Simulation '{simulation_id}' was not found.")
    if simulation.status != SimulationStatus.COMPLETED or simulation.result is None:
        raise HTTPException(
            status_code=409, detail="Security reports require a completed simulation."
        )
    nodes: list[Node] = []
    links: list[QuantumLink] = []
    if simulation.topology_id is not None:
        nodes = list(
            session.scalars(select(Node).where(Node.topology_id == simulation.topology_id))
        )
        links = list(
            session.scalars(
                select(QuantumLink).where(QuantumLink.topology_id == simulation.topology_id)
            )
        )
    outcomes = list(
        session.scalars(select(Attack.outcome).where(Attack.simulation_id == simulation_id))
    )
    assessment = assess_security(
        simulation.result, nodes, links, [outcome or {} for outcome in outcomes]
    )
    report = SecurityReport(
        simulation_id=simulation.id,
        security_score=assessment.security_score,
        risk_level=assessment.risk_level,
        metrics=assessment.as_dict(),
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


@router.get("/security-reports/{report_id}", response_model=SecurityReportRead)
def get_security_report(report_id: str, session: Session = Depends(get_session)) -> SecurityReport:
    """Retrieve one immutable, persisted security assessment."""
    report = session.get(SecurityReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Security report '{report_id}' was not found.")
    return report
=======

class SecurityAnalysisResponse(BaseModel):
    id: str | None = None
    qber: float
    fidelity: float
    reliability: float
    connectivity: float
    weakest_node: str | None
    weakest_link: tuple[str, str] | None
    risk_score: float
    security_score: float
    risk_level: str
    key_rate_estimate: float
    recommendations: list[RecommendationItem]
    created_at: datetime | None = None


@router.post("/analyze", response_model=SecurityAnalysisResponse)
def analyze(
    payload: SecurityAnalysisRequest,
    session: Session = Depends(get_session),
) -> SecurityAnalysisResponse:
    """Assess a network using an observed BB84 simulation result."""
    metrics = analyze_security(payload.topology, payload.simulation)
    recommendations = recommend_ranked(metrics, payload.simulation.attacks)
    response = SecurityAnalysisResponse(
        qber=metrics.qber,
        fidelity=metrics.mean_fidelity,
        reliability=metrics.reliability,
        connectivity=metrics.connectivity,
        weakest_node=metrics.weakest_node,
        weakest_link=metrics.weakest_link,
        risk_score=round(100 - metrics.security_score, 2),
        security_score=metrics.security_score,
        risk_level=metrics.risk_level,
        key_rate_estimate=metrics.estimated_key_rate,
        recommendations=recommendations,
    )

    analysis = AnalysisRecord(
        topology_id=payload.simulation.metadata.get("topology_id") if payload.simulation.metadata else None,
        simulation_id=payload.simulation.id,
        metrics=response.model_dump(mode="json", exclude={"id", "created_at"}),
    )
    session.add(analysis)
    session.commit()
    session.refresh(analysis)

    session.add(
        RecommendationRecord(
            analysis_id=analysis.id,
            items=[item.model_dump(mode="json") for item in recommendations],
        )
    )
    session.commit()

    response.id = analysis.id
    response.created_at = analysis.created_at
    return response
>>>>>>> origin/main
