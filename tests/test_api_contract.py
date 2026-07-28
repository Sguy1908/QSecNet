from uuid import uuid4

from fastapi.testclient import TestClient

from backend.database.session import SessionLocal, initialize_database
from backend.main import app
from backend.models.records import (
    AnalysisRecord,
    AttackRecord,
    RecommendationRecord,
    ReportRecord,
    SimulationRecord,
)
from backend.models.topology import Topology


client = TestClient(app)


def _cleanup() -> None:
    initialize_database()
    with SessionLocal() as session:
        session.query(ReportRecord).delete()
        session.query(RecommendationRecord).delete()
        session.query(AnalysisRecord).delete()
        session.query(AttackRecord).delete()
        session.query(SimulationRecord).delete()
        session.query(Topology).delete()
        session.commit()


def test_health_endpoint_under_api_prefix() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "degraded"}
    assert payload["environment"] == "development"
    assert "database" in payload["readiness"]


def test_topology_crud_and_validation() -> None:
    _cleanup()
    name = f"topology-{uuid4()}"
    topology = {
        "name": name,
        "description": "Integration test topology",
        "nodes": [{"id": "a", "label": "Alice"}, {"id": "b", "label": "Bob"}],
        "links": [
            {
                "source": "a",
                "target": "b",
                "fidelity": 0.97,
                "loss_probability": 0.03,
                "decoherence_time": 90,
                "noise_level": 0.05,
            }
        ],
    }

    validate_response = client.post("/api/v1/topologies/validate", json=topology)
    assert validate_response.status_code == 200
    assert validate_response.json()["valid"] is True

    create_response = client.post("/api/v1/topologies", json=topology)
    assert create_response.status_code == 201
    topology_id = create_response.json()["id"]

    update_payload = {**topology, "name": f"{name}-updated"}
    update_response = client.put(f"/api/v1/topologies/{topology_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == update_payload["name"]

    delete_response = client.delete(f"/api/v1/topologies/{topology_id}")
    assert delete_response.status_code == 204


def test_simulation_security_report_and_ibm_contract() -> None:
    _cleanup()
    topology_name = f"network-{uuid4()}"
    topology_response = client.post(
        "/api/v1/topologies",
        json={
            "name": topology_name,
            "nodes": [{"id": "a", "label": "Alice"}, {"id": "b", "label": "Bob"}],
            "links": [{"source": "a", "target": "b", "fidelity": 0.98}],
        },
    )
    assert topology_response.status_code == 201
    topology_payload = topology_response.json()

    simulation_response = client.post(
        "/api/v1/simulations/bb84",
        json={
            "rounds": 2048,
            "seed": 42,
            "topology_id": topology_payload["id"],
            "attacks": [{"kind": "intercept_resend"}],
        },
    )
    assert simulation_response.status_code == 201
    simulation = simulation_response.json()
    assert simulation["provider"] in {"internal", "aer"}
    assert simulation["sifted_key"] == simulation["shared_key"]
    assert "estimated_secure_key_rate" in simulation

    attack_response = client.get(f"/api/v1/simulations/{simulation['id']}/attacks")
    assert attack_response.status_code == 200
    assert "intercept_resend" in attack_response.json()["attacks"]

    analysis_response = client.post(
        "/api/v1/security/analyze",
        json={"topology": topology_payload, "simulation": simulation},
    )
    assert analysis_response.status_code == 200
    analysis = analysis_response.json()
    assert analysis["risk_level"] in {"low", "medium", "high", "critical"}
    assert analysis["recommendations"]

    report_response = client.post(
        "/api/v1/reports",
        json={
            "topology": topology_payload,
            "simulation": simulation,
            "analysis": analysis,
            "recommendations": analysis["recommendations"],
        },
    )
    assert report_response.status_code == 200
    report_id = report_response.json()["id"]

    csv_export = client.get(f"/api/v1/reports/{report_id}/export", params={"format": "csv"})
    assert csv_export.status_code == 200
    assert csv_export.headers["content-type"].startswith("text/csv")

    ibm_response = client.post("/api/v1/ibm/compare", json={"rounds": 64, "seed": 7})
    assert ibm_response.status_code == 200
    assert ibm_response.json()["status"]["enabled"] is False
