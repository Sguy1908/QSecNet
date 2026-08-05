from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.api.projects import create_project
from backend.api.schemas import ProjectCreate
from backend.api.simulations import SimulationCreate, run_simulation
from backend.models import Base, SimulationStatus


def test_simulation_endpoint_persists_bb84_result() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project = create_project(ProjectCreate(name="BB84 experiment"), session)
        simulation = run_simulation(
            project.id, SimulationCreate(requested_bits=64, seed=5), session
        )

        assert simulation.status == SimulationStatus.COMPLETED
        assert simulation.result is not None
        assert simulation.result["qber"] == 0.0
