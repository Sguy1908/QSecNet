import pytest

from backend.services.ibm_service import IBMQuantumService, IBMRuntimeUnavailableError


def test_ibm_service_requires_credentials_before_execution() -> None:
    service = IBMQuantumService(token=None)

    assert not service.is_configured
    with pytest.raises(IBMRuntimeUnavailableError, match="credentials"):
        service.run_zero_state_probe("ibm_brisbane", 128)


def test_ibm_service_validates_shots_before_sdk_import() -> None:
    service = IBMQuantumService(token="token")

    with pytest.raises(ValueError, match="shots"):
        service.run_zero_state_probe("ibm_brisbane", 0)
