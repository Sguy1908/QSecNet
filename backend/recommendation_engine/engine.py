"""Evidence-based recommendations derived from security metrics."""

from backend.analyzer.security import SecurityMetrics


def recommend(metrics: SecurityMetrics, attacks: list[str]) -> list[str]:
    """Return concise, prioritized remediation guidance."""
    recommendations: list[str] = []
    if metrics.qber > 0.11:
        recommendations.append(
            "High QBER exceeds the BB84 security threshold; isolate the affected route and re-key."
        )
    if metrics.mean_fidelity < 0.9:
        recommendations.append(
            "Low link fidelity detected; use entanglement purification or higher-quality repeaters."
        )
    if metrics.connectivity < 0.5 or "node_failure" in attacks:
        recommendations.append("Add redundant relay paths to tolerate node failure and improve connectivity.")
    if "link_failure" in attacks or metrics.reliability < 0.8:
        recommendations.append("Provision a diverse backup link for the weakest network segment.")
    if "intercept_resend" in attacks:
        recommendations.append(
            "Treat intercept-resend evidence as an active eavesdropping event and discard the key material."
        )
    return recommendations or [
        "Security posture is healthy; continue QBER sampling and periodic topology review."
    ]
