"""BB84 simulation and attack analysis endpoints."""

from enum import StrEnum
from random import Random

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from backend.attacks.factory import build_attack
from backend.simulator.bb84 import BB84Result, simulate_bb84

router = APIRouter(prefix="/simulations", tags=["simulations"])


class AttackKind(StrEnum):
    INTERCEPT_RESEND = "intercept_resend"
    CHANNEL_NOISE = "channel_noise"
    PHOTON_LOSS = "photon_loss"
    NODE_FAILURE = "node_failure"
    LINK_FAILURE = "link_failure"


class AttackRequest(BaseModel):
    kind: AttackKind
    probability: float | None = Field(default=None, ge=0.0, le=1.0)
    node_id: str | None = None
    source: str | None = None
    target: str | None = None

    @model_validator(mode="after")
    def require_attack_parameters(self) -> "AttackRequest":
        if self.kind in {AttackKind.CHANNEL_NOISE, AttackKind.PHOTON_LOSS} and self.probability is None:
            raise ValueError("probability is required for this attack")
        if self.kind is AttackKind.NODE_FAILURE and not self.node_id:
            raise ValueError("node_id is required for node failure")
        if self.kind is AttackKind.LINK_FAILURE and not (self.source and self.target):
            raise ValueError("source and target are required for link failure")
        return self


class SimulationRequest(BaseModel):
    rounds: int = Field(default=1024, ge=16, le=1_000_000)
    seed: int | None = None
    attacks: list[AttackRequest] = Field(default_factory=list)


class SimulationResponse(BaseModel):
    shared_key: str
    key_length: int
    qber: float
    success_probability: float
    sifted_bits: int
    delivery_probability: float
    attacks: list[str]
    affected_nodes: list[str]
    affected_links: list[tuple[str, str]]


def derive_result(result: BB84Result, request: SimulationRequest) -> SimulationResponse:
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
    return SimulationResponse(
        shared_key=key,
        key_length=int(sifted * delivery),
        qber=errors / sifted if sifted else 0.0,
        success_probability=(sifted / len(transcript.alice_bits)) * delivery,
        sifted_bits=sifted,
        delivery_probability=delivery,
        attacks=[attack.kind.value for attack in request.attacks],
        affected_nodes=nodes,
        affected_links=links,
    )


@router.post("/bb84", response_model=SimulationResponse)
def run_bb84(payload: SimulationRequest) -> SimulationResponse:
    """Execute an ideal BB84 run and apply configured adversarial conditions."""
    try:
        return derive_result(simulate_bb84(payload.rounds, payload.seed), payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
