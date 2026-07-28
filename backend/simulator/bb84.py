"""Protocol-level BB84 simulation with reproducible stochastic execution."""

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class BB84Transcript:
    """Raw protocol observations retained for attack and security analysis."""

    alice_bits: list[int]
    alice_bases: list[int]
    bob_bits: list[int]
    bob_bases: list[int]


@dataclass(frozen=True)
class BB84Result:
    """Derived output from a BB84 transmission."""

    shared_key: str
    key_length: int
    qber: float
    success_probability: float
    sifted_bits: int
    transcript: BB84Transcript


def simulate_bb84(rounds: int, seed: int | None = None) -> BB84Result:
    """Simulate ideal BB84 preparation, measurement, and basis reconciliation.

    Bases use 0 for rectilinear and 1 for diagonal. In an ideal channel, matched
    bases deterministically yield Alice's encoded bit.
    """
    rng = Random(seed)
    alice_bits = [rng.randrange(2) for _ in range(rounds)]
    alice_bases = [rng.randrange(2) for _ in range(rounds)]
    bob_bases = [rng.randrange(2) for _ in range(rounds)]
    bob_bits = [
        bit if a_basis == b_basis else rng.randrange(2)
        for bit, a_basis, b_basis in zip(alice_bits, alice_bases, bob_bases)
    ]
    matched = [index for index in range(rounds) if alice_bases[index] == bob_bases[index]]
    errors = sum(alice_bits[index] != bob_bits[index] for index in matched)
    key = "".join(str(alice_bits[index]) for index in matched)
    sifted = len(matched)
    return BB84Result(
        shared_key=key,
        key_length=sifted,
        qber=errors / sifted if sifted else 0.0,
        success_probability=sifted / rounds,
        sifted_bits=sifted,
        transcript=BB84Transcript(alice_bits, alice_bases, bob_bits, bob_bases),
    )
