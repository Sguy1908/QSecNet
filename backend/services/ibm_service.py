"""IBM Quantum Runtime adapter with safe disabled behavior."""

import os

from pydantic import BaseModel

from backend.services.bb84_service import run_bb84


class IBMStatus(BaseModel):
    enabled: bool
    available: bool
    backend: str | None = None
    message: str


class IBMCompareResponse(BaseModel):
    status: IBMStatus
    local: dict[str, float | int | str]
    ibm: dict[str, float | int | str] | None = None


def ibm_enabled() -> bool:
    return os.getenv("QSECNET_ENABLE_IBM", "false").lower() in {"1", "true", "yes"}


def _ibm_credentials_present() -> bool:
    return bool(os.getenv("QSECNET_IBM_TOKEN"))


def compare_bb84(rounds: int, seed: int | None) -> IBMCompareResponse:
    local_result, provider = run_bb84(rounds, seed)
    local_payload = {
        "provider": provider,
        "qber": local_result.qber,
        "key_length": local_result.key_length,
        "success_probability": local_result.success_probability,
    }
    if not ibm_enabled():
        return IBMCompareResponse(
            status=IBMStatus(enabled=False, available=False, message="IBM integration disabled"),
            local=local_payload,
            ibm=None,
        )
    if not _ibm_credentials_present():
        return IBMCompareResponse(
            status=IBMStatus(
                enabled=True,
                available=False,
                message="IBM credentials missing: set QSECNET_IBM_TOKEN",
            ),
            local=local_payload,
            ibm=None,
        )

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except Exception:
        return IBMCompareResponse(
            status=IBMStatus(
                enabled=True,
                available=False,
                message="qiskit-ibm-runtime not installed",
            ),
            local=local_payload,
            ibm=None,
        )

    try:
        service = QiskitRuntimeService(channel="ibm_quantum", token=os.environ["QSECNET_IBM_TOKEN"])
        backend = service.least_busy(simulator=True)
    except Exception as exc:
        return IBMCompareResponse(
            status=IBMStatus(enabled=True, available=False, message=f"IBM unavailable: {exc}"),
            local=local_payload,
            ibm=None,
        )

    return IBMCompareResponse(
        status=IBMStatus(
            enabled=True,
            available=True,
            backend=getattr(backend, "name", None),
            message="IBM backend available",
        ),
        local=local_payload,
        ibm={
            "provider": "ibm_runtime",
            "backend": getattr(backend, "name", "unknown"),
        },
    )
