"""Pydantic request and response schemas for the public API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class APIModel(BaseModel):
    """Base schema with ORM attribute support."""

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=5000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=5000)


class ProjectRead(APIModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class TopologyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=5000)


class TopologyRead(APIModel):
    id: str
    project_id: str
    name: str
    description: str | None
    version: int
    created_at: datetime
    updated_at: datetime


class NodeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    node_type: str = Field(default="repeater", min_length=1, max_length=40)
    x_position: float | None = None
    y_position: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class NodeRead(APIModel):
    id: str
    topology_id: str
    name: str
    node_type: str
    x_position: float | None
    y_position: float | None
    is_operational: bool
    metadata_: dict[str, Any] = Field(serialization_alias="metadata")
    created_at: datetime
    updated_at: datetime


class QuantumLinkCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    fidelity: float = Field(default=0.99, ge=0, le=1)
    loss_probability: float = Field(default=0.0, ge=0, le=1)
    decoherence_time_us: float | None = Field(default=None, gt=0)
    distance_km: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_distinct_endpoints(self) -> "QuantumLinkCreate":
        if self.source_node_id == self.target_node_id:
            raise ValueError("A quantum link must connect two distinct nodes.")
        return self


class QuantumLinkRead(APIModel):
    id: str
    topology_id: str
    source_node_id: str
    target_node_id: str
    fidelity: float
    loss_probability: float
    decoherence_time_us: float | None
    distance_km: float | None
    is_operational: bool
    created_at: datetime
    updated_at: datetime
