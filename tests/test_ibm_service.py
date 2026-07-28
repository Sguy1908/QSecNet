from backend.config import Settings
from backend.services.ibm_service import QuantumExecutionService


def test_ibm_adapter_runs_aer_and_is_safe_when_unconfigured() -> None:
    result = QuantumExecutionService(Settings(ibm_quantum_token=None)).compare(32)

    assert sum(result.local_counts.values()) == 32
    assert result.remote_available is False
    assert result.remote_counts is None
