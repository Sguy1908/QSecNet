from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.api.projects import create_node, create_project, create_quantum_link, create_topology
from backend.api.schemas import NodeCreate, ProjectCreate, QuantumLinkCreate, TopologyCreate
from backend.models import Base


def test_project_topology_and_link_lifecycle() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project = create_project(ProjectCreate(name="Research"), session)
        topology = create_topology(project.id, TopologyCreate(name="Testbed"), session)
        alice = create_node(topology.id, NodeCreate(name="Alice"), session)
        bob = create_node(topology.id, NodeCreate(name="Bob"), session)
        link = create_quantum_link(
            topology.id,
            QuantumLinkCreate(source_node_id=alice.id, target_node_id=bob.id, fidelity=0.97),
            session,
        )

        assert link.fidelity == 0.97
        assert link.topology_id == topology.id
