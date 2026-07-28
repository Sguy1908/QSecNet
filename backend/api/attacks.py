"""Composable attack preview API for topology-aware clients."""

from random import Random

from fastapi import APIRouter
from pydantic import BaseModel

from backend.api.simulations import AttackRequest
from backend.api.topologies import TopologyCreate
from backend.attacks.factory import build_attack
from backend.simulator.bb84 import simulate_bb84

router = APIRouter(prefix="/attacks", tags=["attacks"])


class AttackPreviewRequest(BaseModel):
    topology: TopologyCreate
    attacks: list[AttackRequest]
    rounds: int = 256
    seed: int | None = None


class AttackPreviewResponse(BaseModel):
    attacks: list[str]
    delivery_probability: float
    unavailable_nodes: list[str]
    unavailable_links: list[tuple[str, str]]
    remaining_nodes: list[str]
    remaining_links: list[tuple[str, str]]


@router.post("/preview", response_model=AttackPreviewResponse)
def preview(payload: AttackPreviewRequest) -> AttackPreviewResponse:
    """Apply attacks compositionally and return the resulting available network state."""
    transcript = simulate_bb84(payload.rounds, payload.seed).transcript
    rng = Random(payload.seed)
    delivery = 1.0
    failed_nodes: set[str] = set()
    failed_links: set[tuple[str, str]] = set()
    for request in payload.attacks:
        outcome = build_attack(request).apply(transcript, rng)
        transcript = outcome.transcript
        delivery *= outcome.delivered_fraction
        failed_nodes.update(outcome.affected_nodes)
        failed_links.update(tuple(sorted(link)) for link in outcome.affected_links)
    remaining_nodes = [node.id for node in payload.topology.nodes if node.id not in failed_nodes]
    remaining_links = [
        (link.source, link.target)
        for link in payload.topology.links
        if link.source not in failed_nodes
        and link.target not in failed_nodes
        and tuple(sorted((link.source, link.target))) not in failed_links
    ]
    return AttackPreviewResponse(
        attacks=[item.kind.value for item in payload.attacks],
        delivery_probability=delivery,
        unavailable_nodes=sorted(failed_nodes),
        unavailable_links=sorted(failed_links),
        remaining_nodes=remaining_nodes,
        remaining_links=remaining_links,
    )
