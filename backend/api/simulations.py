"""Simulation execution and result retrieval endpoints."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.database import get_session
from backend.models import Project, Simulation, SimulationStatus, Topology
from backend.simulator.bb84 import simulate_bb84

router = APIRouter(tags=["Simulations"])


class SimulationCreate(BaseModel):
    topology_id: str | None = None
    requested_bits: int = Field(default=256, ge=1, le=4096)
    execution_mode: Literal["analytic", "aer"] = "analytic"
    seed: int | None = None


class SimulationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    topology_id: str | None
    protocol: str
    status: SimulationStatus
    requested_bits: int
    configuration: dict[str, object]
    result: dict[str, object] | None
    error_message: str | None


@router.post(
    "/projects/{project_id}/simulations",
    response_model=SimulationRead,
    status_code=status.HTTP_201_CREATED,
)
def run_simulation(
    project_id: str, payload: SimulationCreate, session: Session = Depends(get_session)
) -> Simulation:
    """Execute BB84 and persist its reproducible inputs and outputs."""
    if session.get(Project, project_id) is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' was not found.")
    if payload.topology_id is not None:
        topology = session.get(Topology, payload.topology_id)
        if topology is None or topology.project_id != project_id:
            raise HTTPException(status_code=422, detail="Topology must belong to the project.")

    simulation = Simulation(
        project_id=project_id,
        topology_id=payload.topology_id,
        requested_bits=payload.requested_bits,
        status=SimulationStatus.RUNNING,
        configuration=payload.model_dump(exclude={"seed"}) | {"seed": payload.seed},
    )
    session.add(simulation)
    try:
        result = simulate_bb84(
            payload.requested_bits, execution_mode=payload.execution_mode, seed=payload.seed
        )
    except ValueError as error:
        simulation.status = SimulationStatus.FAILED
        simulation.error_message = str(error)
        session.commit()
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        simulation.status = SimulationStatus.FAILED
        simulation.error_message = "BB84 simulation execution failed."
        session.commit()
        raise HTTPException(status_code=500, detail="BB84 simulation execution failed.") from error

    simulation.status = SimulationStatus.COMPLETED
    simulation.result = result.as_dict()
    session.commit()
    session.refresh(simulation)
    return simulation


@router.get("/simulations/{simulation_id}", response_model=SimulationRead)
def get_simulation(simulation_id: str, session: Session = Depends(get_session)) -> Simulation:
    """Retrieve a persisted simulation and its BB84 metrics."""
    simulation = session.get(Simulation, simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail=f"Simulation '{simulation_id}' was not found.")
    return simulation
