from backend.api.attacks import AttackPreviewRequest, preview
from backend.api.simulations import AttackRequest
from backend.api.topologies import TopologyCreate


def test_link_failure_removes_link_from_preview() -> None:
    topology = TopologyCreate.model_validate(
        {
            "name": "test",
            "nodes": [{"id": "alice", "label": "Alice"}, {"id": "bob", "label": "Bob"}],
            "links": [{"source": "alice", "target": "bob"}],
        }
    )
    result = preview(
        AttackPreviewRequest(
            topology=topology,
            attacks=[AttackRequest(kind="link_failure", source="alice", target="bob")],
        )
    )

    assert result.remaining_links == []
    assert result.unavailable_links == [("alice", "bob")]
