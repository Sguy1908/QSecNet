"""Optional Qiskit Aer and IBM Quantum Runtime execution adapter."""

from dataclasses import dataclass

from backend.config import Settings


@dataclass(frozen=True)
class ExecutionComparison:
    """Comparable local and remote execution outcome."""

    local_counts: dict[str, int]
    remote_available: bool
    remote_counts: dict[str, int] | None
    backend_name: str | None
    message: str


class QuantumExecutionService:
    """Run a small calibration circuit locally and optionally on IBM hardware."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def compare(self, shots: int) -> ExecutionComparison:
        """Execute a Bell-pair circuit on Aer and IBM Runtime when enabled.

        Remote access is deliberately opt-in: no credential is persisted or
        transmitted unless `QSECNET_IBM_QUANTUM_TOKEN` is supplied.
        """
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator

        circuit = QuantumCircuit(2, 2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure([0, 1], [0, 1])
        local_counts = dict(AerSimulator().run(circuit, shots=shots).result().get_counts())
        if not self.settings.ibm_quantum_token:
            return ExecutionComparison(
                local_counts=local_counts,
                remote_available=False,
                remote_counts=None,
                backend_name=None,
                message="IBM Quantum Runtime is disabled; set QSECNET_IBM_QUANTUM_TOKEN to enable it.",
            )
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService

            service = QiskitRuntimeService(
                token=self.settings.ibm_quantum_token,
                instance=self.settings.ibm_quantum_instance,
            )
            backend = service.least_busy(operational=True, simulator=False)
            job = backend.run(circuit, shots=shots)
            remote_counts = dict(job.result().get_counts())
            return ExecutionComparison(
                local_counts=local_counts,
                remote_available=True,
                remote_counts=remote_counts,
                backend_name=backend.name,
                message="Local Aer and IBM hardware results are available.",
            )
        except Exception as exc:
            return ExecutionComparison(
                local_counts=local_counts,
                remote_available=False,
                remote_counts=None,
                backend_name=None,
                message=f"IBM Quantum Runtime unavailable: {exc}",
            )
