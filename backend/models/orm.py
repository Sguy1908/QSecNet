"""SQLAlchemy persistence entities for QSecNet."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def new_id() -> str:
    """Create a portable UUID primary key."""
    return str(uuid4())


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Base class for all database entities."""


class SimulationStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimestampedEntity:
    """Common audit fields for persisted entities."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class Project(TimestampedEntity, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    topologies: Mapped[list[Topology]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    simulations: Mapped[list[Simulation]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Topology(TimestampedEntity, Base):
    __tablename__ = "topologies"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    project: Mapped[Project] = relationship(back_populates="topologies")
    nodes: Mapped[list[Node]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    links: Mapped[list[QuantumLink]] = relationship(
        back_populates="topology", cascade="all, delete-orphan"
    )


class Node(TimestampedEntity, Base):
    __tablename__ = "nodes"

    topology_id: Mapped[str] = mapped_column(ForeignKey("topologies.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    node_type: Mapped[str] = mapped_column(String(40), default="repeater", nullable=False)
    x_position: Mapped[float | None] = mapped_column(Float)
    y_position: Mapped[float | None] = mapped_column(Float)
    is_operational: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    topology: Mapped[Topology] = relationship(back_populates="nodes")


class QuantumLink(TimestampedEntity, Base):
    __tablename__ = "quantum_links"

    topology_id: Mapped[str] = mapped_column(ForeignKey("topologies.id"), index=True)
    source_node_id: Mapped[str] = mapped_column(ForeignKey("nodes.id"), index=True)
    target_node_id: Mapped[str] = mapped_column(ForeignKey("nodes.id"), index=True)
    fidelity: Mapped[float] = mapped_column(Float, default=0.99, nullable=False)
    loss_probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    decoherence_time_us: Mapped[float | None] = mapped_column(Float)
    distance_km: Mapped[float | None] = mapped_column(Float)
    is_operational: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    topology: Mapped[Topology] = relationship(back_populates="links")


class Simulation(TimestampedEntity, Base):
    __tablename__ = "simulations"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    topology_id: Mapped[str | None] = mapped_column(ForeignKey("topologies.id"), index=True)
    protocol: Mapped[str] = mapped_column(String(40), default="BB84", nullable=False)
    status: Mapped[SimulationStatus] = mapped_column(
        Enum(SimulationStatus), default=SimulationStatus.PENDING, nullable=False
    )
    requested_bits: Mapped[int] = mapped_column(Integer, nullable=False)
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    project: Mapped[Project] = relationship(back_populates="simulations")
    attacks: Mapped[list[Attack]] = relationship(back_populates="simulation", cascade="all, delete-orphan")
    reports: Mapped[list[SecurityReport]] = relationship(
        back_populates="simulation", cascade="all, delete-orphan"
    )


class Attack(TimestampedEntity, Base):
    __tablename__ = "attacks"

    simulation_id: Mapped[str] = mapped_column(ForeignKey("simulations.id"), index=True)
    attack_type: Mapped[str] = mapped_column(String(50), nullable=False)
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    outcome: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    simulation: Mapped[Simulation] = relationship(back_populates="attacks")


class SecurityReport(TimestampedEntity, Base):
    __tablename__ = "security_reports"

    simulation_id: Mapped[str] = mapped_column(ForeignKey("simulations.id"), index=True)
    security_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    simulation: Mapped[Simulation] = relationship(back_populates="reports")
    recommendations: Mapped[list[Recommendation]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )


class Recommendation(TimestampedEntity, Base):
    __tablename__ = "recommendations"

    report_id: Mapped[str] = mapped_column(ForeignKey("security_reports.id"), index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    report: Mapped[SecurityReport] = relationship(back_populates="recommendations")
