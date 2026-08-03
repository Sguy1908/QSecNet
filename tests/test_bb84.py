from backend.simulator.bb84 import simulate_bb84


def test_ideal_bb84_has_no_qber_and_is_reproducible() -> None:
    result = simulate_bb84(128, seed=7)

    assert result.qber == 0
    assert result.shared_key == simulate_bb84(128, seed=7).shared_key
    assert result.estimated_key_rate > 0


def test_intercept_resend_introduces_detectable_qber() -> None:
    result = simulate_bb84(1024, seed=17, intercept_resend=True)

    assert result.qber > 0.11
    assert result.eavesdropper_detected
