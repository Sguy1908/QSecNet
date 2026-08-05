from backend.models import RiskLevel
from backend.recommendation_engine.engine import generate_recommendations


def test_critical_metrics_produce_actionable_recommendations() -> None:
    recommendations = generate_recommendations(
        {
            "qber": 0.2,
            "average_fidelity": 0.8,
            "reliability": 0.7,
            "connectivity": 0.5,
            "estimated_key_rate": 0.0,
        }
    )

    assert {recommendation.category for recommendation in recommendations} == {
        "protocol_integrity",
        "channel_quality",
        "resilience",
        "key_management",
    }
    assert recommendations[0].priority == RiskLevel.CRITICAL


def test_healthy_metrics_produce_monitoring_advice() -> None:
    recommendations = generate_recommendations(
        {
            "qber": 0.01,
            "average_fidelity": 0.99,
            "reliability": 0.99,
            "connectivity": 1.0,
            "estimated_key_rate": 0.4,
        }
    )

    assert len(recommendations) == 1
    assert recommendations[0].category == "monitoring"
