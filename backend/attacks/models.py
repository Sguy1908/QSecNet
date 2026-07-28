"""Concrete attack models supported by the simulation service."""

from dataclasses import dataclass
from random import Random

from backend.attacks.base import Attack, AttackOutcome
from backend.simulator.bb84 import BB84Transcript


@dataclass(frozen=True)
class InterceptResendAttack(Attack):
    name: str = "intercept_resend"

    def apply(self, transcript: BB84Transcript, rng: Random) -> AttackOutcome:
        eve_bases = [rng.randrange(2) for _ in transcript.alice_bits]
        bob_bits = [
            alice_bit
            if alice_basis == eve_basis
            else rng.randrange(2)
            for alice_bit, alice_basis, eve_basis in zip(
                transcript.alice_bits, transcript.alice_bases, eve_bases
            )
        ]
        # Bob's measurement only preserves Eve's resend result when their bases match.
        bob_bits = [
            eve_bit if eve_basis == bob_basis else rng.randrange(2)
            for eve_bit, eve_basis, bob_basis in zip(bob_bits, eve_bases, transcript.bob_bases)
        ]
        return AttackOutcome(
            BB84Transcript(
                transcript.alice_bits, transcript.alice_bases, bob_bits, transcript.bob_bases
            )
        )


@dataclass(frozen=True)
class ChannelNoiseAttack(Attack):
    probability: float
    name: str = "channel_noise"

    def apply(self, transcript: BB84Transcript, rng: Random) -> AttackOutcome:
        bits = [bit ^ int(rng.random() < self.probability) for bit in transcript.bob_bits]
        return AttackOutcome(
            BB84Transcript(transcript.alice_bits, transcript.alice_bases, bits, transcript.bob_bases)
        )


@dataclass(frozen=True)
class PhotonLossAttack(Attack):
    probability: float
    name: str = "photon_loss"

    def apply(self, transcript: BB84Transcript, rng: Random) -> AttackOutcome:
        delivered = sum(rng.random() >= self.probability for _ in transcript.alice_bits)
        return AttackOutcome(transcript, delivered / len(transcript.alice_bits))


@dataclass(frozen=True)
class NodeFailureAttack(Attack):
    node_id: str
    name: str = "node_failure"

    def apply(self, transcript: BB84Transcript, rng: Random) -> AttackOutcome:
        return AttackOutcome(transcript, 0.0, affected_nodes=(self.node_id,))


@dataclass(frozen=True)
class LinkFailureAttack(Attack):
    source: str
    target: str
    name: str = "link_failure"

    def apply(self, transcript: BB84Transcript, rng: Random) -> AttackOutcome:
        return AttackOutcome(transcript, 0.0, affected_links=((self.source, self.target),))
