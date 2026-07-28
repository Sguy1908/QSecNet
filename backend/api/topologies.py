"""Topology builder endpoints and validation schemas."""

from datetime import datetime
from enum import StrEnum

import networkx as nx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database.session import get_session
from backend.models.topology import Topology

router = APIRouter(prefix="/topologies", tags=["topologies"])


class NodeRole(StrEnum):
    ENDPOINT = "endpoint"
    REPEATER = "repeater"
    TRUSTED_RELAY = "trusted_relay"


class NetworkNode(BaseModel):
    id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    label: str = Field(min_length=1, max_length=100)
    role: NodeRole = NodeRole.ENDPOINT
    x: float | None = None
    y: float | None = None


class QuantumLink(BaseModel):
    source: str
    target: str
    fidelity: float = Field(default=0.98, ge=0.0, le=1.0)
    loss_probability: float = Field(default=0.02, ge=0.0, le=1.0)
    decoherence_time_us: float = Field(default=100.0, gt=0.0)


class TopologyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    nodes: list[NetworkNode] = Field(min_length=2)
    links: list[QuantumLink] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_graph(self) -> "TopologyCreate":
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("node ids must be unique")
        graph = nx.Graph()
        graph.add_nodes_from(node_ids)
        for link in self.links:
            if link.source == link.target:
                raise ValueError("self-links are not permitted")
            if link.source not in graph or link.target not in graph:
                raise ValueError("each link must reference existing nodes")
            if graph.has_edge(link.source, link.target):
                raise ValueError("duplicate links are not permitted")
            graph.add_edge(link.source, link.target)
        if not nx.is_connected(graph):
            raise ValueError("topology must be connected")
        return self


class TopologyRead(TopologyCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


def serialize_topology(topology: Topology) -> TopologyRead:
    """Map JSON-backed database data to typed output objects."""
    return TopologyRead(
        id=topology.id,
        name=topology.name,
        description=topology.description,
        nodes=[NetworkNode.model_validate(node) for node in topology.nodes],
        links=[QuantumLink.model_validate(link) for link in topology.links],
        created_at=topology.created_at,
        updated_at=topology.updated_at,
    )


@router.post("", response_model=TopologyRead, status_code=status.HTTP_201_CREATED)
def create_topology(
    payload: TopologyCreate, session: Session = Depends(get_session)
) -> TopologyRead:
    """Persist a validated network topology."""
    topology = Topology(
        name=payload.name,
        description=payload.description,
        nodes=[node.model_dump() for node in payload.nodes],
        links=[link.model_dump() for link in payload.links],
    )
    session.add(topology)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="A topology with this name exists"
        ) from exc
    session.refresh(topology)
    return serialize_topology(topology)


@router.get("", response_model=list[TopologyRead])
def list_topologies(session: Session = Depends(get_session)) -> list[TopologyRead]:
    """List saved topologies in creation order."""
    items = session.scalars(select(Topology).order_by(Topology.created_at.desc())).all()
    return [serialize_topology(item) for item in items]


@router.get("/{topology_id}", response_model=TopologyRead)
def get_topology(
    topology_id: str, session: Session = Depends(get_session)
) -> TopologyRead:
    """Retrieve one saved topology."""
    topology = session.get(Topology, topology_id)
    if topology is None:
        raise HTTPException(status_code=404, detail="Topology not found")
    return serialize_topology(topology)
