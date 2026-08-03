"""Extensible interfaces and shared types for quantum-network attacks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class AttackResult:
    """Measured consequences of applying one threat model."""

    attack_type: str
    qber: float | None
    success_probability: float | None
    estimated_key_rate: float | None
    detected: bool
    impact: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class AttackModel(Protocol):
    """Protocol every pluggable attack model must implement."""

    attack_type: str

    def execute(self, simulation: dict[str, Any], configuration: dict[str, Any]) -> AttackResult:
        """Apply the attack to a completed simulation's metrics."""
