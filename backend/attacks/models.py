"""Built-in threat models for QSecNet."""

from __future__ import annotations

from typing import Any

from backend.attacks.base import AttackResult


def _metrics(simulation: dict[str, Any]) -> tuple[float, float, float]:
    qber = float(simulation.get("qber", 0.0))
    success = float(simulation.get("success_probability", 0.0))
    key_rate = float(simulation.get("estimated_key_rate", 0.0))
    return qber, success, key_rate


class InterceptResendAttack:
    attack_type = "intercept_resend"

    def execute(self, simulation: dict[str, Any], configuration: dict[str, Any]) -> AttackResult:
        qber, success, key_rate = _metrics(simulation)
        interception_rate = float(configuration.get("interception_rate", 1.0))
        if not 0 <= interception_rate <= 1:
            raise ValueError("interception_rate must be between 0 and 1")
        attacked_qber = qber + (0.25 * interception_rate * (1 - 2 * qber))
        attacked_qber = min(1.0, max(0.0, attacked_qber))
        return AttackResult(
            attack_type=self.attack_type,
            qber=attacked_qber,
            success_probability=min(success, 1 - attacked_qber),
            estimated_key_rate=key_rate * max(0.0, 1 - 4 * interception_rate),
            detected=attacked_qber > 0.11,
            impact={"interception_rate": interception_rate},
        )


class ChannelNoiseAttack:
    attack_type = "channel_noise"

    def execute(self, simulation: dict[str, Any], configuration: dict[str, Any]) -> AttackResult:
        qber, success, key_rate = _metrics(simulation)
        noise_probability = float(configuration.get("noise_probability", 0.05))
        if not 0 <= noise_probability <= 1:
            raise ValueError("noise_probability must be between 0 and 1")
        attacked_qber = qber * (1 - noise_probability) + (1 - qber) * noise_probability
        return AttackResult(
            attack_type=self.attack_type,
            qber=attacked_qber,
            success_probability=min(success, 1 - attacked_qber),
            estimated_key_rate=key_rate * max(0.0, 1 - 2 * noise_probability),
            detected=attacked_qber > 0.11,
            impact={"noise_probability": noise_probability},
        )


class PhotonLossAttack:
    attack_type = "photon_loss"

    def execute(self, simulation: dict[str, Any], configuration: dict[str, Any]) -> AttackResult:
        qber, success, key_rate = _metrics(simulation)
        loss_probability = float(configuration.get("loss_probability", 0.1))
        if not 0 <= loss_probability <= 1:
            raise ValueError("loss_probability must be between 0 and 1")
        factor = 1 - loss_probability
        return AttackResult(
            attack_type=self.attack_type,
            qber=qber,
            success_probability=success * factor,
            estimated_key_rate=key_rate * factor,
            detected=loss_probability > 0.2,
            impact={"loss_probability": loss_probability},
        )


class NodeFailureAttack:
    attack_type = "node_failure"

    def execute(self, simulation: dict[str, Any], configuration: dict[str, Any]) -> AttackResult:
        qber, _, key_rate = _metrics(simulation)
        node_id = configuration.get("node_id")
        if not isinstance(node_id, str) or not node_id:
            raise ValueError("node_id is required for a node_failure attack")
        return AttackResult(
            attack_type=self.attack_type,
            qber=qber,
            success_probability=0.0,
            estimated_key_rate=0.0,
            detected=True,
            impact={
                "failed_node_id": node_id,
                "service_disruption": True,
                "baseline_key_rate": key_rate,
            },
        )


class LinkFailureAttack:
    attack_type = "link_failure"

    def execute(self, simulation: dict[str, Any], configuration: dict[str, Any]) -> AttackResult:
        qber, _, key_rate = _metrics(simulation)
        link_id = configuration.get("link_id")
        if not isinstance(link_id, str) or not link_id:
            raise ValueError("link_id is required for a link_failure attack")
        return AttackResult(
            attack_type=self.attack_type,
            qber=qber,
            success_probability=0.0,
            estimated_key_rate=0.0,
            detected=True,
            impact={
                "failed_link_id": link_id,
                "service_disruption": True,
                "baseline_key_rate": key_rate,
            },
        )
