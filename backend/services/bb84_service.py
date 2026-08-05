"""BB84 simulation service with optional Qiskit Aer backend."""

from random import Random

from backend.simulator.bb84 import BB84Result, BB84Transcript, simulate_bb84


def run_bb84(rounds: int, seed: int | None = None) -> tuple[BB84Result, str]:
    """Run BB84 using Qiskit Aer when available, otherwise fallback to internal model."""
    if rounds > 4096:
        return simulate_bb84(rounds, seed), "internal"
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import AerSimulator
    except Exception:
        return simulate_bb84(rounds, seed), "internal"

    rng = Random(seed)
    backend = AerSimulator(seed_simulator=seed)
    alice_bits = [rng.randrange(2) for _ in range(rounds)]
    alice_bases = [rng.randrange(2) for _ in range(rounds)]
    bob_bases = [rng.randrange(2) for _ in range(rounds)]
    bob_bits: list[int] = []

    for idx, (bit, alice_basis, bob_basis) in enumerate(zip(alice_bits, alice_bases, bob_bases)):
        circuit = QuantumCircuit(1, 1)
        if bit:
            circuit.x(0)
        if alice_basis:
            circuit.h(0)
        if bob_basis:
            circuit.h(0)
        circuit.measure(0, 0)
        compiled = transpile(circuit, backend)
        result = backend.run(compiled, shots=1, seed_simulator=(seed or 0) + idx).result()
        counts = result.get_counts()
        bob_bits.append(1 if counts.get("1", 0) else 0)

    matched = [index for index in range(rounds) if alice_bases[index] == bob_bases[index]]
    errors = sum(alice_bits[index] != bob_bits[index] for index in matched)
    key = "".join(str(alice_bits[index]) for index in matched)
    sifted = len(matched)
    bb84_result = BB84Result(
        shared_key=key,
        key_length=sifted,
        qber=errors / sifted if sifted else 0.0,
        success_probability=sifted / rounds,
        sifted_bits=sifted,
        transcript=BB84Transcript(alice_bits, alice_bases, bob_bits, bob_bases),
    )
    return bb84_result, "aer"
