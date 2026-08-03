"""Optional IBM Quantum Runtime adapter for simulator-to-hardware comparisons."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class IBMRuntimeUnavailableError(RuntimeError):
    """Raised when IBM Runtime cannot be used in the current deployment."""


@dataclass(frozen=True, slots=True)
class HardwareProbeResult:
    """Observed error metrics for a known BB84-compatible prepared state."""

    backend_name: str
    shots: int
    counts: dict[str, int]
    error_rate: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class IBMQuantumService:
    """Small adapter isolating optional IBM SDK and credential concerns."""

    def __init__(self, token: str | None, instance: str | None = None) -> None:
        self.token = token
        self.instance = instance

    @property
    def is_configured(self) -> bool:
        return bool(self.token)

    def run_zero_state_probe(self, backend_name: str, shots: int) -> HardwareProbeResult:
        """Measure prepared |0> states to obtain an empirical hardware bit-error rate."""
        if not self.token:
            raise IBMRuntimeUnavailableError("IBM Quantum credentials are not configured.")
        if not 1 <= shots <= 100_000:
            raise ValueError("shots must be between 1 and 100000")
        try:
            from qiskit import QuantumCircuit
            from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
        except ImportError as error:
            raise IBMRuntimeUnavailableError(
                "Install the IBM extra with `pip install -e '.[ibm]'` to use hardware execution."
            ) from error

        service_args: dict[str, str] = {"channel": "ibm_quantum_platform", "token": self.token}
        if self.instance:
            service_args["instance"] = self.instance
        service = QiskitRuntimeService(**service_args)
        backend = service.backend(backend_name)
        circuit = QuantumCircuit(1, 1)
        circuit.measure(0, 0)
        sampler = SamplerV2(mode=backend)
        result = sampler.run([circuit], shots=shots).result()
        counts = {str(key): int(value) for key, value in result[0].data.c.get_counts().items()}
        correct = counts.get("0", 0)
        return HardwareProbeResult(
            backend_name=backend_name,
            shots=shots,
            counts=counts,
            error_rate=1 - (correct / shots),
        )
