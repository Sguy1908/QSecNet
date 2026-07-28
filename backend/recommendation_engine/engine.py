"""Evidence-based recommendations derived from security metrics."""

from pydantic import BaseModel

from backend.analyzer.security import SecurityMetrics


class RecommendationItem(BaseModel):
    rank: int
    action: str
    reason: str
    priority: str


def recommend(metrics: SecurityMetrics, attacks: list[str]) -> list[str]:
    """Return concise, prioritized remediation guidance."""
    return [item.action for item in recommend_ranked(metrics, attacks)]


def recommend_ranked(metrics: SecurityMetrics, attacks: list[str]) -> list[RecommendationItem]:
    items: list[RecommendationItem] = []

    if metrics.qber > 0.11:
        items.append(
            RecommendationItem(
                rank=0,
                action="Isolate the affected route and discard current key material.",
                reason="QBER exceeds the BB84 security threshold.",
                priority="critical",
            )
        )
    if metrics.mean_fidelity < 0.9:
        items.append(
            RecommendationItem(
                rank=0,
                action="Apply purification and upgrade low-fidelity repeaters.",
                reason="Low link fidelity reduces secure key viability.",
                priority="high",
            )
        )
    if metrics.connectivity < 0.5 or "node_failure" in attacks:
        items.append(
            RecommendationItem(
                rank=0,
                action="Increase path redundancy around critical nodes.",
                reason="Connectivity is fragile under node failure.",
                priority="high",
            )
        )
    if "link_failure" in attacks or metrics.reliability < 0.8:
        items.append(
            RecommendationItem(
                rank=0,
                action="Provision a diverse backup link for the weakest segment.",
                reason="Delivery reliability is below target.",
                priority="medium",
            )
        )
    if "intercept_resend" in attacks:
        items.append(
            RecommendationItem(
                rank=0,
                action="Enable aggressive eavesdropping detection and rotate keys.",
                reason="Intercept-resend behavior indicates active adversary presence.",
                priority="critical",
            )
        )

    if not items:
        items = [
            RecommendationItem(
                rank=1,
                action="Maintain periodic QBER sampling and topology review.",
                reason="Current posture is healthy.",
                priority="low",
            )
        ]

    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    for rank, item in enumerate(sorted(items, key=lambda item: order[item.priority]), start=1):
        item.rank = rank
    return items
