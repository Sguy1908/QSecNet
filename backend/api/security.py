"""Security-analysis API schemas and endpoint."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.analyzer.security import analyze_security
from backend.api.simulations import SimulationResponse
from backend.api.topologies import TopologyCreate
from backend.database.session import get_session
from backend.models.topology import AnalysisRecord
from backend.recommendation_engine.engine import recommend

router = APIRouter(prefix="/security", tags=["security"])


class SecurityAnalysisRequest(BaseModel):
    topology: TopologyCreate
    simulation: SimulationResponse


class SecurityAnalysisResponse(BaseModel):
    id: str | None = None
    qber: float
    mean_fidelity: float
    security_score: float
    risk_level: str
    weakest_link: tuple[str, str] | None
    weakest_node: str | None
    estimated_key_rate: float
    reliability: float
    connectivity: float
    recommendations: list[str]


@router.post("/analyze", response_model=SecurityAnalysisResponse)
def analyze(
    payload: SecurityAnalysisRequest, session: Session = Depends(get_session)
) -> SecurityAnalysisResponse:
    """Assess a network using an observed BB84 simulation result."""
    metrics = analyze_security(payload.topology, payload.simulation)
    response = SecurityAnalysisResponse(
        **metrics.__dict__, recommendations=recommend(metrics, payload.simulation.attacks)
    )
    record = AnalysisRecord(simulation_id=payload.simulation.id, result=response.model_dump(mode="json"))
    session.add(record)
    session.commit()
    session.refresh(record)
    return response.model_copy(update={"id": record.id})
