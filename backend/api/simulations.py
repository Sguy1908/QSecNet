"""Simulation execution and result retrieval endpoints."""

<<<<<<< HEAD
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.database import get_session
from backend.models import Project, Simulation, SimulationStatus, Topology
from backend.simulator.bb84 import simulate_bb84
=======
from datetime import datetime
from enum import StrEnum
from random import Random

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from backend.attacks.factory import build_attack
from backend.database.session import get_session
from backend.models.records import AttackRecord, SimulationRecord
from backend.services.bb84_service import run_bb84
from backend.simulator.bb84 import BB84Result
>>>>>>> origin/main

router = APIRouter(tags=["Simulations"])


class SimulationCreate(BaseModel):
    topology_id: str | None = None
    requested_bits: int = Field(default=256, ge=1, le=4096)
    execution_mode: Literal["analytic", "aer"] = "analytic"
    seed: int | None = None
<<<<<<< HEAD


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
=======
    topology_id: str | None = None
    attacks: list[AttackRequest] = Field(default_factory=list)


class SimulationResponse(BaseModel):
    id: str | None = None
    status: str = "success"
    provider: str = "internal"
    shared_key: str
    raw_key_bits: list[int]
    sifted_key: str
    key_length: int
    qber: float
    estimated_secure_key_rate: float
    success_probability: float
    sifted_bits: int
    delivery_probability: float
    attacks: list[str]
    affected_nodes: list[str]
    affected_links: list[tuple[str, str]]
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime | None = None


class SimulationListItem(BaseModel):
    id: str
    topology_id: str | None
    provider: str
    rounds: int
    seed: int | None
    created_at: datetime


def derive_result(
    result: BB84Result,
    request: SimulationRequest,
    provider: str = "internal",
) -> SimulationResponse:
    """Apply selected attacks and compute observable BB84 quantities."""
    transcript = result.transcript
    delivery = 1.0
    nodes: list[str] = []
    links: list[tuple[str, str]] = []
    rng = Random(request.seed)
    for attack_request in request.attacks:
        outcome = build_attack(attack_request).apply(transcript, rng)
        transcript = outcome.transcript
        delivery *= outcome.delivered_fraction
        nodes.extend(outcome.affected_nodes)
        links.extend(outcome.affected_links)
    matched = [i for i, basis in enumerate(transcript.alice_bases) if basis == transcript.bob_bases[i]]
    errors = sum(transcript.alice_bits[i] != transcript.bob_bits[i] for i in matched)
    sifted = len(matched)
    key = "".join(str(transcript.alice_bits[i]) for i in matched)
    secure_key_rate = max(
        0.0,
        (1 - 2 * (errors / sifted if sifted else 0.0))
        * (sifted / request.rounds)
        * delivery,
    )
    return SimulationResponse(
        status="success",
        provider=provider,
        shared_key=key,
        raw_key_bits=transcript.alice_bits,
        sifted_key=key,
        key_length=int(sifted * delivery),
        qber=errors / sifted if sifted else 0.0,
        estimated_secure_key_rate=round(secure_key_rate, 6),
        success_probability=(sifted / len(transcript.alice_bits)) * delivery,
        sifted_bits=sifted,
        delivery_probability=delivery,
        attacks=[attack.kind.value for attack in request.attacks],
        affected_nodes=sorted(set(nodes)),
        affected_links=sorted(set(links)),
        metadata={
            "rounds": request.rounds,
            "seed": request.seed,
            "attack_count": len(request.attacks),
            "topology_id": request.topology_id,
        },
    )


def _serialize_record(record: SimulationRecord) -> SimulationResponse:
    payload = SimulationResponse.model_validate(record.result_payload)
    payload.id = record.id
    payload.created_at = record.created_at
    return payload


@router.post("/bb84", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def run_bb84_simulation(
    payload: SimulationRequest, session: Session = Depends(get_session)
) -> SimulationResponse:
    """Execute an ideal BB84 run and apply configured adversarial conditions."""
    try:
        bb84_result, provider = run_bb84(payload.rounds, payload.seed)
        response = derive_result(bb84_result, payload, provider=provider)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record = SimulationRecord(
        topology_id=payload.topology_id,
        provider=provider,
        rounds=payload.rounds,
        seed=payload.seed,
        request_payload=payload.model_dump(mode="json"),
        result_payload=response.model_dump(mode="json"),
    )
    session.add(record)
    session.commit()
    session.refresh(record)

    if payload.attacks:
        session.add(
            AttackRecord(
                simulation_id=record.id,
                summary={
                    "attacks": response.attacks,
                    "affected_nodes": response.affected_nodes,
                    "affected_links": response.affected_links,
                    "delivery_probability": response.delivery_probability,
                },
            )
        )
        session.commit()

    response.id = record.id
    response.created_at = record.created_at
    return response


@router.get("", response_model=list[SimulationListItem])
def list_simulations(session: Session = Depends(get_session)) -> list[SimulationListItem]:
    """List persisted BB84 simulations."""
    records = session.query(SimulationRecord).order_by(SimulationRecord.created_at.desc()).all()
    return [
        SimulationListItem(
            id=record.id,
            topology_id=record.topology_id,
            provider=record.provider,
            rounds=record.rounds,
            seed=record.seed,
            created_at=record.created_at,
        )
        for record in records
    ]


@router.get("/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: str, session: Session = Depends(get_session)) -> SimulationResponse:
    """Retrieve one persisted BB84 simulation."""
    record = session.get(SimulationRecord, simulation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return _serialize_record(record)


@router.get("/{simulation_id}/attacks")
def get_attack_summary(simulation_id: str, session: Session = Depends(get_session)) -> dict[str, object]:
    """Fetch persisted attack effects for a simulation."""
    attack = (
        session.query(AttackRecord)
        .filter(AttackRecord.simulation_id == simulation_id)
        .order_by(AttackRecord.created_at.desc())
        .first()
    )
    if attack is None:
        return {"simulation_id": simulation_id, "attacks": [], "summary": None}
    return {
        "simulation_id": simulation_id,
        "attacks": attack.summary.get("attacks", []),
        "summary": attack.summary,
    }
>>>>>>> origin/main
