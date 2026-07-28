"""Ranked recommendation endpoint for independent API consumers."""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.analyzer.security import SecurityMetrics
from backend.api.security import SecurityAnalysisResponse
from backend.recommendation_engine.engine import recommend

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendationItem(BaseModel):
    priority: int
    recommendation: str
    reason: str


class RecommendationRequest(BaseModel):
    analysis: SecurityAnalysisResponse
    attacks: list[str] = []


def _metrics(analysis: SecurityAnalysisResponse) -> SecurityMetrics:
    return SecurityMetrics(
        qber=analysis.qber,
        mean_fidelity=analysis.mean_fidelity,
        security_score=analysis.security_score,
        risk_level=analysis.risk_level,
        weakest_link=analysis.weakest_link,
        weakest_node=analysis.weakest_node,
        estimated_key_rate=analysis.estimated_key_rate,
        reliability=analysis.reliability,
        connectivity=analysis.connectivity,
    )


@router.post("", response_model=list[RecommendationItem])
def generate(payload: RecommendationRequest) -> list[RecommendationItem]:
    """Return recommendations in stable priority order with contextual reasons."""
    messages = recommend(_metrics(payload.analysis), payload.attacks)
    reason = (
        f"Risk level is {payload.analysis.risk_level}; "
        f"security score is {payload.analysis.security_score}."
    )
    return [
        RecommendationItem(priority=index, recommendation=message, reason=reason)
        for index, message in enumerate(messages, start=1)
    ]
