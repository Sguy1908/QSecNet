"""Persistence records for simulations, analysis, recommendations, and reports."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base


class SimulationRecord(Base):
    __tablename__ = "simulations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    topology_id: Mapped[str | None] = mapped_column(ForeignKey("topologies.id"), nullable=True)
    provider: Mapped[str] = mapped_column(String(32), default="internal")
    rounds: Mapped[int] = mapped_column()
    seed: Mapped[int | None] = mapped_column(nullable=True)
    request_payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    result_payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AttackRecord(Base):
    __tablename__ = "attacks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    simulation_id: Mapped[str] = mapped_column(ForeignKey("simulations.id"), index=True)
    summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    topology_id: Mapped[str | None] = mapped_column(ForeignKey("topologies.id"), nullable=True)
    simulation_id: Mapped[str | None] = mapped_column(ForeignKey("simulations.id"), nullable=True)
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RecommendationRecord(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id"), index=True)
    items: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReportRecord(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    topology_id: Mapped[str | None] = mapped_column(ForeignKey("topologies.id"), nullable=True)
    simulation_id: Mapped[str | None] = mapped_column(ForeignKey("simulations.id"), nullable=True)
    analysis_id: Mapped[str | None] = mapped_column(ForeignKey("analyses.id"), nullable=True)
    recommendation_id: Mapped[str | None] = mapped_column(ForeignKey("recommendations.id"), nullable=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
