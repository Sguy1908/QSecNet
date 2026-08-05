from types import SimpleNamespace

from backend.analyzer.security import assess_security
from backend.models import RiskLevel


def test_security_assessment_uses_attack_worst_case() -> None:
    nodes = [
        SimpleNamespace(id="a", name="Alice", is_operational=True),
        SimpleNamespace(id="b", name="Bob", is_operational=True),
    ]
    links = [
        SimpleNamespace(
            id="link", source_node_id="a", target_node_id="b", fidelity=0.99,
            loss_probability=0.01, decoherence_time_us=None, is_operational=True,
        )
    ]
    assessment = assess_security(
        {"qber": 0.0, "estimated_key_rate": 0.5}, nodes, links,
        [{"qber": 0.25, "estimated_key_rate": 0.0}],
    )

    assert assessment.qber == 0.25
    assert assessment.estimated_key_rate == 0.0
    assert assessment.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
