import pytest
from pydantic import ValidationError

from backend.api.topologies import TopologyCreate


def test_topology_requires_connected_graph() -> None:
    with pytest.raises(ValidationError, match="connected"):
        TopologyCreate.model_validate(
            {
                "name": "disconnected",
                "nodes": [
                    {"id": "alice", "label": "Alice"},
                    {"id": "bob", "label": "Bob"},
                    {"id": "charlie", "label": "Charlie"},
                ],
                "links": [{"source": "alice", "target": "bob"}],
            }
        )


def test_topology_accepts_quantum_link_properties() -> None:
    topology = TopologyCreate.model_validate(
        {
            "name": "alice-bob",
            "nodes": [{"id": "alice", "label": "Alice"}, {"id": "bob", "label": "Bob"}],
            "links": [{"source": "alice", "target": "bob", "fidelity": 0.97}],
        }
    )

    assert topology.links[0].fidelity == 0.97
