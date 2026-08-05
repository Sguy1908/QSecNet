"""Network topology analysis and secure-routing endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_session
from backend.models import Node, QuantumLink, Topology
from backend.simulator.network import QuantumNetwork

router = APIRouter(tags=["Network analysis"])


class NetworkAnalysisRead(BaseModel):
    node_count: int
    link_count: int
    connectivity: float
    reliability: float
    connected_components: int
    weakest_link_id: str | None
    weakest_link_fidelity: float | None


class RouteRequest(BaseModel):
    source_node_id: str
    target_node_id: str


class RouteRead(BaseModel):
    node_ids: list[str] = Field(min_length=2)


def _network_or_404(session: Session, topology_id: str) -> QuantumNetwork:
    if session.get(Topology, topology_id) is None:
        raise HTTPException(status_code=404, detail=f"Topology '{topology_id}' was not found.")
    nodes = list(session.scalars(select(Node).where(Node.topology_id == topology_id)))
    links = list(session.scalars(select(QuantumLink).where(QuantumLink.topology_id == topology_id)))
    return QuantumNetwork(nodes, links)


@router.get("/topologies/{topology_id}/network-analysis", response_model=NetworkAnalysisRead)
def analyze_network(topology_id: str, session: Session = Depends(get_session)) -> dict[str, object]:
    """Calculate channel health and graph connectivity for a topology."""
    return _network_or_404(session, topology_id).analyze().as_dict()


@router.post("/topologies/{topology_id}/routes", response_model=RouteRead)
def find_secure_route(
    topology_id: str, payload: RouteRequest, session: Session = Depends(get_session)
) -> RouteRead:
    """Find the lowest-risk currently operational route between two network nodes."""
    try:
        route = _network_or_404(session, topology_id).secure_route(
            payload.source_node_id, payload.target_node_id
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return RouteRead(node_ids=route)
