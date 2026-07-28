"""Security-analysis API schemas and endpoint."""

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

router = APIRouter(prefix="/security", tags=["security"])


class SecurityAnalysisRequest(BaseModel):
    topology: TopologyCreate
    simulation: SimulationResponse


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
