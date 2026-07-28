"""Persistence models for saved quantum network topologies."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, String, func
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
