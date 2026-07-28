"""Network and protocol security metric calculations."""

from dataclasses import dataclass

import networkx as nx

from backend.api.simulations import SimulationResponse
from backend.api.topologies import TopologyCreate


@dataclass(frozen=True)
class SecurityMetrics:
    qber: float
    mean_fidelity: float
    security_score: float
    risk_level: str
    weakest_link: tuple[str, str] | None
    weakest_node: str | None
    estimated_key_rate: float
    reliability: float
    connectivity: float


def analyze_security(topology: TopologyCreate, simulation: SimulationResponse) -> SecurityMetrics:
    """Combine BB84 observations and graph reliability into comparable metrics."""
    graph = nx.Graph()
    graph.add_nodes_from(node.id for node in topology.nodes)
    for link in topology.links:
        graph.add_edge(link.source, link.target, fidelity=link.fidelity, loss=link.loss_probability)
    weakest = min(topology.links, key=lambda link: link.fidelity * (1 - link.loss_probability))
    node_reliability = {
        node: sum(
            graph.edges[edge]["fidelity"] * (1 - graph.edges[edge]["loss"])
            for edge in graph.edges(node)
        )
        / max(graph.degree(node), 1)
        for node in graph.nodes
    }
    mean_fidelity = sum(link.fidelity for link in topology.links) / len(topology.links)
    reliability = sum(node_reliability.values()) / len(node_reliability) * simulation.delivery_probability
    connectivity = nx.node_connectivity(graph) / max(len(graph) - 1, 1)
    # BB84 security threshold is conventionally near 11%; cap each degraded factor.
    qber_factor = max(0.0, 1 - simulation.qber / 0.11)
    score = 100 * (0.45 * qber_factor + 0.30 * mean_fidelity + 0.15 * reliability + 0.10 * connectivity)
    risk = "low" if score >= 80 else "medium" if score >= 55 else "high" if score >= 30 else "critical"
    return SecurityMetrics(
        qber=simulation.qber,
        mean_fidelity=mean_fidelity,
        security_score=round(score, 2),
        risk_level=risk,
        weakest_link=(weakest.source, weakest.target),
        weakest_node=min(node_reliability, key=node_reliability.get),
        estimated_key_rate=round(simulation.key_length * reliability, 2),
        reliability=round(reliability, 4),
        connectivity=round(connectivity, 4),
    )
