"""Persistence models for saved quantum network topologies."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base


class Topology(Base):
    """A user-defined quantum communication network."""

    __tablename__ = "topologies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    nodes: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    links: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SimulationRecord(Base):
    """A reproducible BB84 execution and its public result data."""

    __tablename__ = "simulation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    topology_id: Mapped[str | None] = mapped_column(ForeignKey("topologies.id"), nullable=True)
    request: Mapped[dict[str, object]] = mapped_column(JSON)
    result: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AnalysisRecord(Base):
    """Persisted security analysis related to an optional simulation."""

    __tablename__ = "security_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    simulation_id: Mapped[str | None] = mapped_column(ForeignKey("simulation_results.id"), nullable=True)
    result: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SecurityReport(Base):
    """An immutable, exportable security assessment."""

    __tablename__ = "security_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(160))
    analysis_id: Mapped[str | None] = mapped_column(ForeignKey("security_analyses.id"), nullable=True)
    content: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
