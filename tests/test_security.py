from backend.analyzer.security import analyze_security
from backend.api.simulations import AttackRequest, SimulationRequest, derive_result
from backend.api.topologies import TopologyCreate
from backend.recommendation_engine.engine import recommend
from backend.simulator.bb84 import simulate_bb84


def test_security_analysis_flags_intercept_resend() -> None:
    topology = TopologyCreate.model_validate(
        {
            "name": "network",
            "nodes": [{"id": "a", "label": "Alice"}, {"id": "b", "label": "Bob"}],
            "links": [{"source": "a", "target": "b", "fidelity": 0.98}],
        }
    )
    request = SimulationRequest(
        rounds=5000, seed=5, attacks=[AttackRequest(kind="intercept_resend")]
    )
    simulation = derive_result(simulate_bb84(request.rounds, request.seed), request)
    metrics = analyze_security(topology, simulation)

    assert metrics.risk_level in {"high", "critical"}
    assert any("eavesdropping" in item for item in recommend(metrics, simulation.attacks))
