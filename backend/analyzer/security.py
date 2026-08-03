"""Security posture calculation for quantum communication networks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import fmean
from typing import Any

from backend.models import Node, QuantumLink, RiskLevel
from backend.simulator.network import QuantumNetwork


@dataclass(frozen=True, slots=True)
class SecurityAssessment:
    """Derived security metrics suitable for a persisted report."""

    qber: float
    average_fidelity: float
    security_score: float
    risk_level: RiskLevel
    weakest_link_id: str | None
    weakest_node_id: str | None
    estimated_key_rate: float
    reliability: float
    connectivity: float

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["risk_level"] = self.risk_level.value
        return data


def _risk_level(score: float) -> RiskLevel:
    if score >= 80:
        return RiskLevel.LOW
    if score >= 60:
        return RiskLevel.MEDIUM
    if score >= 35:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def _weakest_node(nodes: list[Node], links: list[QuantumLink]) -> str | None:
    if not nodes:
        return None
    incident_quality: dict[str, list[float]] = {node.id: [] for node in nodes}
    for link in links:
        quality = link.fidelity * (1 - link.loss_probability) if link.is_operational else 0.0
        incident_quality[link.source_node_id].append(quality)
        incident_quality[link.target_node_id].append(quality)

    def health(node: Node) -> float:
        if not node.is_operational:
            return 0.0
        qualities = incident_quality[node.id]
        return fmean(qualities) if qualities else 0.0

    return min(nodes, key=health).id


def assess_security(
    simulation_result: dict[str, Any],
    nodes: list[Node],
    links: list[QuantumLink],
    attack_outcomes: list[dict[str, Any]] | None = None,
) -> SecurityAssessment:
    """Assess security using the most adverse measured attack outcome.

    The score is a bounded product of protocol integrity (QBER), channel
    fidelity, network reliability, and graph connectivity. This makes every
    component explicit and avoids an opaque model for research comparisons.
    """
    outcomes = attack_outcomes or []
    qber = max(
        [float(simulation_result.get("qber", 0.0))] + [float(x.get("qber") or 0) for x in outcomes]
    )
    key_rate = min(
        [float(simulation_result.get("estimated_key_rate", 0.0))]
        + [float(x.get("estimated_key_rate") or 0) for x in outcomes]
    )
    network = QuantumNetwork(nodes, links)
    network_metrics = network.analyze()
    active_links = [link for link in links if link.is_operational]
    average_fidelity = fmean(link.fidelity for link in active_links) if active_links else 0.0
    qber_integrity = max(0.0, 1 - (qber / 0.11))
    score = round(
        100
        * qber_integrity
        * average_fidelity
        * network_metrics.reliability
        * network_metrics.connectivity,
        2,
    )
    return SecurityAssessment(
        qber=qber,
        average_fidelity=average_fidelity,
        security_score=score,
        risk_level=_risk_level(score),
        weakest_link_id=network_metrics.weakest_link_id,
        weakest_node_id=_weakest_node(nodes, links),
        estimated_key_rate=key_rate,
        reliability=network_metrics.reliability,
        connectivity=network_metrics.connectivity,
    )
