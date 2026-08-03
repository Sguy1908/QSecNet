"""Security report creation and retrieval endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

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
