from uuid import uuid4

from backend.api.topologies import TopologyCreate, create_topology, get_topology
from backend.database.session import SessionLocal, initialize_database
from backend.models.topology import Topology


def test_create_and_retrieve_topology() -> None:
    name = f"test-{uuid4()}"
    payload = {
        "name": name,
        "nodes": [{"id": "alice", "label": "Alice"}, {"id": "bob", "label": "Bob"}],
        "links": [{"source": "alice", "target": "bob", "fidelity": 0.96}],
    }

    initialize_database()
    with SessionLocal() as session:
        created = create_topology(TopologyCreate.model_validate(payload), session)
        fetched = get_topology(created.id, session)
        session.delete(session.get(Topology, created.id))
        session.commit()

    assert fetched.id == created.id
    assert fetched.links[0].fidelity == 0.96
