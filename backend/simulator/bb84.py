"""BB84 quantum key-distribution simulation with analytic and Aer execution modes."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import log2
from random import Random
from typing import Literal

ExecutionMode = Literal["analytic", "aer"]


@dataclass(frozen=True, slots=True)
class BB84Result:
    """Security-relevant output of one BB84 protocol run."""

    shared_key: str
    key_length: int
    sifted_bits: int
    qber: float
    success_probability: float
    estimated_key_rate: float
    execution_mode: ExecutionMode
    eavesdropper_detected: bool

    def as_dict(self) -> dict[str, object]:
        """Convert to a JSON-compatible API/persistence representation."""
        return asdict(self)


def _binary_entropy(probability: float) -> float:
    if probability in {0.0, 1.0}:
        return 0.0
    return -probability * log2(probability) - (1 - probability) * log2(1 - probability)


def _aer_measure(bit: int, alice_basis: int, bob_basis: int) -> int:
    """Prepare, measure, and read one BB84 qubit using Qiskit Aer."""
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    circuit = QuantumCircuit(1, 1)
    if bit:
        circuit.x(0)
    if alice_basis:
        circuit.h(0)
    if bob_basis:
        circuit.h(0)
    circuit.measure(0, 0)
    memory = AerSimulator().run(circuit, shots=1, memory=True).result().get_memory(circuit)
    return int(memory[0])


def simulate_bb84(
    requested_bits: int,
    *,
    execution_mode: ExecutionMode = "analytic",
    seed: int | None = None,
    intercept_resend: bool = False,
) -> BB84Result:
    """Run BB84 and return a sifted key and security metrics.

    The analytic mode exactly implements ideal BB84 measurement statistics and
    is preferred for large experiments. Aer mode constructs and executes each
    transmitted qubit circuit, providing a direct Qiskit simulator comparison.
    """
    if not 1 <= requested_bits <= 4096:
        raise ValueError("requested_bits must be between 1 and 4096")
    if execution_mode not in {"analytic", "aer"}:
        raise ValueError("execution_mode must be 'analytic' or 'aer'")

    rng = Random(seed)
    alice_bits = [rng.randrange(2) for _ in range(requested_bits)]
    alice_bases = [rng.randrange(2) for _ in range(requested_bits)]
    bob_bases = [rng.randrange(2) for _ in range(requested_bits)]
    bob_bits: list[int] = []

    for bit, alice_basis, bob_basis in zip(alice_bits, alice_bases, bob_bases, strict=True):
        transmitted_bit, transmitted_basis = bit, alice_basis
        if intercept_resend:
            eve_basis = rng.randrange(2)
            eve_bit = transmitted_bit if eve_basis == transmitted_basis else rng.randrange(2)
            transmitted_bit, transmitted_basis = eve_bit, eve_basis

        if execution_mode == "aer" and not intercept_resend:
            bob_bits.append(_aer_measure(bit, alice_basis, bob_basis))
        elif bob_basis == transmitted_basis:
            bob_bits.append(transmitted_bit)
        else:
            bob_bits.append(rng.randrange(2))

    sifted = [
        (alice_bit, bob_bit)
        for alice_bit, bob_bit, alice_basis, bob_basis in zip(
            alice_bits, bob_bits, alice_bases, bob_bases, strict=True
        )
        if alice_basis == bob_basis
    ]
    errors = sum(alice_bit != bob_bit for alice_bit, bob_bit in sifted)
    sifted_count = len(sifted)
    qber = errors / sifted_count if sifted_count else 0.0
    secret_fraction = max(0.0, 1 - 2 * _binary_entropy(qber))
    return BB84Result(
        shared_key="".join(str(alice_bit) for alice_bit, _ in sifted),
        key_length=sifted_count,
        sifted_bits=sifted_count,
        qber=qber,
        success_probability=sifted_count / requested_bits,
        estimated_key_rate=(sifted_count / requested_bits) * secret_fraction,
        execution_mode=execution_mode,
        eavesdropper_detected=qber > 0.11,
    )
