"""Explainable mitigation recommendations derived from security metrics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from backend.models import RiskLevel


@dataclass(frozen=True, slots=True)
class RecommendationSuggestion:
    """A deterministic mitigation proposal ready for persistence."""

    title: str
    description: str
    priority: RiskLevel
    category: str

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["priority"] = self.priority.value
        return data


def generate_recommendations(metrics: dict[str, Any]) -> list[RecommendationSuggestion]:
    """Generate non-duplicative mitigations from transparent threshold rules."""
    recommendations: list[RecommendationSuggestion] = []
    qber = float(metrics.get("qber", 0.0))
    fidelity = float(metrics.get("average_fidelity", 1.0))
    reliability = float(metrics.get("reliability", 1.0))
    connectivity = float(metrics.get("connectivity", 1.0))
    key_rate = float(metrics.get("estimated_key_rate", 0.0))

    if qber > 0.11:
        recommendations.append(
            RecommendationSuggestion(
                title="Investigate high QBER before distributing keys",
                description=(
                    f"Observed QBER is {qber:.1%}, above BB84's 11% security bound. "
                    "Inspect channels for interception or excess noise and rerun key exchange."
                ),
                priority=RiskLevel.CRITICAL,
                category="protocol_integrity",
            )
        )
    if fidelity < 0.9:
        recommendations.append(
            RecommendationSuggestion(
                title="Improve low-fidelity quantum channels",
                description=(
                    f"Average link fidelity is {fidelity:.1%}. Apply entanglement purification "
                    "or choose a higher-fidelity route before transmitting key material."
                ),
                priority=RiskLevel.HIGH,
                category="channel_quality",
            )
        )
    if connectivity < 1.0 or reliability < 0.8:
        recommendations.append(
            RecommendationSuggestion(
                title="Add resilient routing capacity",
                description=(
                    "The active topology has incomplete connectivity "
                    "or weak end-to-end reliability. "
                    "Add redundant repeater paths and monitor failed links."
                ),
                priority=RiskLevel.HIGH,
                category="resilience",
            )
        )
    if key_rate <= 0:
        recommendations.append(
            RecommendationSuggestion(
                title="Suspend insecure key generation",
                description=(
                    "The estimated secure key rate is zero. Remediate "
                    "the failing channel or attack "
                    "condition before resuming QKD sessions."
                ),
                priority=RiskLevel.CRITICAL,
                category="key_management",
            )
        )
    if not recommendations:
        recommendations.append(
            RecommendationSuggestion(
                title="Maintain continuous security monitoring",
                description=(
                    "Current metrics are within configured thresholds. Continue sampling QBER and "
                    "channel fidelity to detect drift early."
                ),
                priority=RiskLevel.LOW,
                category="monitoring",
            )
        )
    return recommendations
