"""Project and topology lifecycle endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.api.schemas import (
    NodeCreate,
    NodeRead,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    QuantumLinkCreate,
    QuantumLinkRead,
    TopologyCreate,
    TopologyRead,
)
from backend.database import get_session
from backend.models import Node, Project, QuantumLink, Topology

router = APIRouter(tags=["Projects and topologies"])


def _not_found(resource: str, resource_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{resource} '{resource_id}' was not found.")


def _project_or_404(session: Session, project_id: str) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise _not_found("Project", project_id)
    return project


def _topology_or_404(session: Session, topology_id: str) -> Topology:
    topology = session.get(Topology, topology_id)
    if topology is None:
        raise _not_found("Topology", topology_id)
    return topology


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, session: Session = Depends(get_session)) -> Project:
    """Create a named security-analysis project."""
    project = Project(**payload.model_dump())
    session.add(project)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="A project with this name already exists."
        ) from error
    session.refresh(project)
    return project


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(session: Session = Depends(get_session)) -> list[Project]:
    """List projects ordered by creation time."""
    return list(session.scalars(select(Project).order_by(Project.created_at.desc())))


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, session: Session = Depends(get_session)) -> Project:
    return _project_or_404(session, project_id)


@router.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: str, payload: ProjectUpdate, session: Session = Depends(get_session)
) -> Project:
    project = _project_or_404(session, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="A project with this name already exists."
        ) from error
    session.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, session: Session = Depends(get_session)) -> None:
    session.delete(_project_or_404(session, project_id))
    session.commit()


@router.post("/projects/{project_id}/topologies", response_model=TopologyRead, status_code=201)
def create_topology(
    project_id: str, payload: TopologyCreate, session: Session = Depends(get_session)
) -> Topology:
    _project_or_404(session, project_id)
    topology = Topology(project_id=project_id, **payload.model_dump())
    session.add(topology)
    session.commit()
    session.refresh(topology)
    return topology


@router.get("/projects/{project_id}/topologies", response_model=list[TopologyRead])
def list_topologies(project_id: str, session: Session = Depends(get_session)) -> list[Topology]:
    _project_or_404(session, project_id)
    return list(session.scalars(select(Topology).where(Topology.project_id == project_id)))


@router.post("/topologies/{topology_id}/nodes", response_model=NodeRead, status_code=201)
def create_node(
    topology_id: str, payload: NodeCreate, session: Session = Depends(get_session)
) -> Node:
    _topology_or_404(session, topology_id)
    node = Node(
        topology_id=topology_id,
        metadata_=payload.metadata,
        **payload.model_dump(exclude={"metadata"}),
    )
    session.add(node)
    session.commit()
    session.refresh(node)
    return node


@router.get("/topologies/{topology_id}/nodes", response_model=list[NodeRead])
def list_nodes(topology_id: str, session: Session = Depends(get_session)) -> list[Node]:
    _topology_or_404(session, topology_id)
    return list(session.scalars(select(Node).where(Node.topology_id == topology_id)))


@router.post("/topologies/{topology_id}/links", response_model=QuantumLinkRead, status_code=201)
def create_quantum_link(
    topology_id: str, payload: QuantumLinkCreate, session: Session = Depends(get_session)
) -> QuantumLink:
    _topology_or_404(session, topology_id)
    nodes = list(
        session.scalars(
            select(Node.id).where(
                Node.topology_id == topology_id,
                Node.id.in_([payload.source_node_id, payload.target_node_id]),
            )
        )
    )
    if len(nodes) != 2:
        raise HTTPException(status_code=422, detail="Link endpoints must belong to the topology.")
    link = QuantumLink(topology_id=topology_id, **payload.model_dump())
    session.add(link)
    session.commit()
    session.refresh(link)
    return link
