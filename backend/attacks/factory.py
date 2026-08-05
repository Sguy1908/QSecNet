"""Registry for attack implementations."""

from backend.attacks.base import AttackModel
from backend.attacks.models import (
    ChannelNoiseAttack,
    InterceptResendAttack,
    LinkFailureAttack,
    NodeFailureAttack,
    PhotonLossAttack,
)

ATTACKS: dict[str, AttackModel] = {
    attack.attack_type: attack
    for attack in (
        InterceptResendAttack(),
        ChannelNoiseAttack(),
        PhotonLossAttack(),
        NodeFailureAttack(),
        LinkFailureAttack(),
    )
}


def get_attack(attack_type: str) -> AttackModel:
    """Retrieve a registered attack implementation by its public name."""
    try:
        return ATTACKS[attack_type]
    except KeyError as error:
        supported = ", ".join(sorted(ATTACKS))
        raise ValueError(
            f"Unsupported attack type '{attack_type}'. Supported: {supported}."
        ) from error
