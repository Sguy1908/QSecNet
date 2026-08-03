from types import SimpleNamespace

import pytest

from backend.simulator.network import QuantumNetwork


def _node(identifier: str, operational: bool = True) -> SimpleNamespace:
    return SimpleNamespace(id=identifier, name=identifier, is_operational=operational)


def _link(
    identifier: str, source: str, target: str, fidelity: float, loss: float = 0.0
) -> SimpleNamespace:
    return SimpleNamespace(
        id=identifier,
        source_node_id=source,
        target_node_id=target,
        fidelity=fidelity,
        loss_probability=loss,
        decoherence_time_us=None,
        is_operational=True,
    )


def test_network_selects_the_most_secure_route() -> None:
    network = QuantumNetwork(
        [_node("alice"), _node("repeater"), _node("bob")],
        [
            _link("direct", "alice", "bob", 0.7),
            _link("a-r", "alice", "repeater", 0.99),
            _link("r-b", "repeater", "bob", 0.99),
        ],
    )

    assert network.secure_route("alice", "bob") == ["alice", "repeater", "bob"]
    assert network.analyze().weakest_link_id == "direct"


def test_network_rejects_routes_through_failed_nodes() -> None:
    network = QuantumNetwork(
        [_node("alice"), _node("bob", operational=False)],
        [_link("a-b", "alice", "bob", 0.99)],
    )

    with pytest.raises(ValueError, match="No operational quantum route"):
        network.secure_route("alice", "bob")
