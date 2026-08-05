import pytest

from backend.attacks import get_attack


BASELINE = {"qber": 0.0, "success_probability": 1.0, "estimated_key_rate": 0.5}


def test_intercept_resend_creates_detectable_qber() -> None:
    outcome = get_attack("intercept_resend").execute(BASELINE, {})

    assert outcome.qber == 0.25
    assert outcome.detected
    assert outcome.estimated_key_rate == 0.0


def test_photon_loss_reduces_delivery_without_increasing_qber() -> None:
    outcome = get_attack("photon_loss").execute(BASELINE, {"loss_probability": 0.4})

    assert outcome.qber == 0.0
    assert outcome.success_probability == 0.6
    assert outcome.estimated_key_rate == 0.3


def test_failure_attack_requires_target() -> None:
    with pytest.raises(ValueError, match="node_id"):
        get_attack("node_failure").execute(BASELINE, {})
