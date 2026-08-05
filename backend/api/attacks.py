"""Attack execution endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.attacks import ATTACKS, get_attack
from backend.database import get_session
from backend.models import Attack, Simulation, SimulationStatus

router = APIRouter(tags=["Attack analysis"])


class AttackCreate(BaseModel):
    attack_type: str = Field(description=f"One of: {', '.join(sorted(ATTACKS))}")
    configuration: dict[str, Any] = Field(default_factory=dict)


class AttackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    simulation_id: str
    attack_type: str
    configuration: dict[str, Any]
    outcome: dict[str, Any] | None


@router.post(
    "/simulations/{simulation_id}/attacks",
    response_model=AttackRead,
    status_code=status.HTTP_201_CREATED,
)
def execute_attack(
    simulation_id: str, payload: AttackCreate, session: Session = Depends(get_session)
) -> Attack:
    """Run a registered threat model against stored simulation metrics."""
    simulation = session.get(Simulation, simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail=f"Simulation '{simulation_id}' was not found.")
    if simulation.status != SimulationStatus.COMPLETED or simulation.result is None:
        raise HTTPException(status_code=409, detail="Attacks require a completed simulation.")
    try:
        outcome = get_attack(payload.attack_type).execute(simulation.result, payload.configuration)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    attack = Attack(
        simulation_id=simulation.id,
        attack_type=payload.attack_type,
        configuration=payload.configuration,
        outcome=outcome.as_dict(),
    )
    session.add(attack)
    session.commit()
    session.refresh(attack)
    return attack


@router.get("/simulations/{simulation_id}/attacks", response_model=list[AttackRead])
def list_attacks(simulation_id: str, session: Session = Depends(get_session)) -> list[Attack]:
    """List persisted attack outcomes for a simulation."""
    if session.get(Simulation, simulation_id) is None:
        raise HTTPException(status_code=404, detail=f"Simulation '{simulation_id}' was not found.")
    return list(session.scalars(select(Attack).where(Attack.simulation_id == simulation_id)))
