from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from backend.models import Base, Project, Topology


def test_schema_creates_all_core_tables() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    assert set(inspect(engine).get_table_names()) == {
        "attacks",
        "nodes",
        "projects",
        "quantum_links",
        "recommendations",
        "security_reports",
        "simulations",
        "topologies",
    }


def test_project_owns_versioned_topologies() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project = Project(name="Demo")
        topology = Topology(name="Metro network")
        project.topologies.append(topology)
        session.add(project)
        session.flush()

        assert topology.project is project
        assert topology.version == 1
