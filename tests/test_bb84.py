from backend.api.simulations import AttackRequest, SimulationRequest, derive_result
from backend.simulator.bb84 import simulate_bb84


def test_ideal_bb84_has_zero_qber() -> None:
    result = simulate_bb84(512, seed=7)

    assert result.qber == 0.0
    assert result.key_length == result.sifted_bits


def test_intercept_resend_introduces_errors() -> None:
    payload = SimulationRequest(
        rounds=10000,
        seed=12,
        attacks=[AttackRequest(kind="intercept_resend")],
    )

    result = derive_result(simulate_bb84(payload.rounds, payload.seed), payload)

    assert 0.20 < result.qber < 0.30


def test_photon_loss_reduces_key_length() -> None:
    payload = SimulationRequest(
        rounds=512,
        seed=2,
        attacks=[AttackRequest(kind="photon_loss", probability=0.5)],
    )
    result = derive_result(simulate_bb84(payload.rounds, payload.seed), payload)

    assert result.delivery_probability < 0.6
    assert result.key_length < result.sifted_bits
    assert len(result.raw_key_bits) == payload.rounds
    assert result.sifted_key
    assert result.estimated_secure_key_rate >= 0
