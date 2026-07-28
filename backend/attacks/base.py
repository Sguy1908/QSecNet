"""Extensible attack protocol for quantum-channel perturbations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import Random

from backend.simulator.bb84 import BB84Transcript


@dataclass(frozen=True)
class AttackOutcome:
    transcript: BB84Transcript
    delivered_fraction: float = 1.0
    affected_nodes: tuple[str, ...] = ()
    affected_links: tuple[tuple[str, str], ...] = ()


class Attack(ABC):
    """A configurable operation applied after quantum transmission."""

    name: str

    @abstractmethod
    def apply(self, transcript: BB84Transcript, rng: Random) -> AttackOutcome:
        """Return a potentially altered protocol transcript."""
