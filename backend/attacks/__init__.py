"""Modular quantum-network threat models."""

from backend.attacks.base import AttackResult
from backend.attacks.factory import ATTACKS, get_attack

__all__ = ["ATTACKS", "AttackResult", "get_attack"]
