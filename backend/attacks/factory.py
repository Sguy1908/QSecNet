"""Validation-aware factory for concrete attack implementations."""

from backend.attacks.base import Attack
from backend.attacks.models import (
    ChannelNoiseAttack,
    InterceptResendAttack,
    LinkFailureAttack,
    NodeFailureAttack,
    PhotonLossAttack,
)


def build_attack(request: object) -> Attack:
    """Create an attack from its API representation."""
    kind = getattr(request, "kind")
    if kind == "intercept_resend":
        return InterceptResendAttack()
    if kind == "channel_noise":
        return ChannelNoiseAttack(getattr(request, "probability") or 0.0)
    if kind == "photon_loss":
        return PhotonLossAttack(getattr(request, "probability") or 0.0)
    if kind == "node_failure":
        return NodeFailureAttack(getattr(request, "node_id") or "")
    return LinkFailureAttack(getattr(request, "source") or "", getattr(request, "target") or "")
