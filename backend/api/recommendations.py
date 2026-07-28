"""Recommendation generation endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.analyzer.security import SecurityMetrics
from backend.recommendation_engine.engine import RecommendationItem, recommend_ranked

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class MetricsPayload(BaseModel):
    qber: float
    mean_fidelity: float
    security_score: float
    risk_level: str
    weakest_link: tuple[str, str] | None
    weakest_node: str | None
    estimated_key_rate: float
    reliability: float
    connectivity: float


class RecommendationRequest(BaseModel):
    metrics: MetricsPayload
    attacks: list[str] = []


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]


@router.post("/generate", response_model=RecommendationResponse)
def generate(payload: RecommendationRequest) -> RecommendationResponse:
    """Generate ranked actionable recommendations for security metrics."""
    metrics = SecurityMetrics(**payload.metrics.model_dump())
    return RecommendationResponse(recommendations=recommend_ranked(metrics, payload.attacks))
