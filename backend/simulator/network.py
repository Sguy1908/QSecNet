"""NetworkX-backed quantum network topology and routing analysis."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import prod

import networkx as nx

from backend.models import Node, QuantumLink


@dataclass(frozen=True, slots=True)
class NetworkAnalysis:
    """Topology-level channel health and graph connectivity metrics."""

    node_count: int
    link_count: int
    connectivity: float
    reliability: float
    connected_components: int
    weakest_link_id: str | None
    weakest_link_fidelity: float | None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class QuantumNetwork:
    """In-memory graph adapter for persisted quantum nodes and channels."""

    def __init__(self, nodes: list[Node], links: list[QuantumLink]) -> None:
        self.graph = nx.Graph()
        for node in nodes:
            self.graph.add_node(node.id, operational=node.is_operational, name=node.name)
        for link in links:
            if not 0 <= link.fidelity <= 1 or not 0 <= link.loss_probability <= 1:
                raise ValueError(f"Link '{link.id}' has invalid channel probabilities.")
            self.graph.add_edge(
                link.source_node_id,
                link.target_node_id,
                link_id=link.id,
                operational=link.is_operational,
                fidelity=link.fidelity,
                loss_probability=link.loss_probability,
                decoherence_time_us=link.decoherence_time_us,
                security_cost=1 - (link.fidelity * (1 - link.loss_probability)),
            )

    def _available_graph(self) -> nx.Graph:
        available = nx.Graph()
        available.add_nodes_from(
            (node_id, data)
            for node_id, data in self.graph.nodes(data=True)
            if data["operational"]
        )
        available.add_edges_from(
            (source, target, data)
            for source, target, data in self.graph.edges(data=True)
            if data["operational"] and source in available and target in available
        )
        return available

    def secure_route(self, source_node_id: str, target_node_id: str) -> list[str]:
        """Return the operational route that minimizes cumulative channel risk."""
        available = self._available_graph()
        try:
            return nx.shortest_path(available, source_node_id, target_node_id, weight="security_cost")
        except (nx.NetworkXNoPath, nx.NodeNotFound) as error:
            raise ValueError(
                "No operational quantum route exists between the requested nodes."
            ) from error

    def analyze(self) -> NetworkAnalysis:
        """Calculate connectivity, channel reliability, and the weakest link."""
        available = self._available_graph()
        node_count = self.graph.number_of_nodes()
        active_edges = list(available.edges(data=True))
        weakest = min(active_edges, key=lambda item: item[2]["fidelity"], default=None)
        connected_components = (
            nx.number_connected_components(available) if available.nodes else 0
        )
        connectivity = 0.0
        if available.number_of_nodes() > 1:
            connectivity = 1.0 if nx.is_connected(available) else 0.0
        reliability = prod(
            data["fidelity"] * (1 - data["loss_probability"]) for _, _, data in active_edges
        )
        return NetworkAnalysis(
            node_count=node_count,
            link_count=self.graph.number_of_edges(),
            connectivity=connectivity,
            reliability=reliability if active_edges else 0.0,
            connected_components=connected_components,
            weakest_link_id=weakest[2]["link_id"] if weakest else None,
            weakest_link_fidelity=weakest[2]["fidelity"] if weakest else None,
        )
