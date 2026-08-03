"""Recommendation generation and retrieval endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_session
from backend.models import Recommendation, RiskLevel, SecurityReport
from backend.recommendation_engine.engine import generate_recommendations

router = APIRouter(tags=["Recommendations"])


class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_id: str
    title: str
    description: str
    priority: RiskLevel
    category: str


@router.post(
    "/security-reports/{report_id}/recommendations",
    response_model=list[RecommendationRead],
    status_code=status.HTTP_201_CREATED,
)
def generate_report_recommendations(
    report_id: str, session: Session = Depends(get_session)
) -> list[Recommendation]:
    """Generate and persist suggestions from a security report's metrics."""
    report = session.get(SecurityReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Security report '{report_id}' was not found.")
    existing = list(
        session.scalars(select(Recommendation).where(Recommendation.report_id == report_id))
    )
    if existing:
        return existing
    recommendations = [
        Recommendation(
            report_id=report_id,
            title=suggestion.title,
            description=suggestion.description,
            priority=suggestion.priority,
            category=suggestion.category,
        )
        for suggestion in generate_recommendations(report.metrics)
    ]
    session.add_all(recommendations)
    session.commit()
    for recommendation in recommendations:
        session.refresh(recommendation)
    return recommendations


@router.get(
    "/security-reports/{report_id}/recommendations", response_model=list[RecommendationRead]
)
def list_report_recommendations(
    report_id: str, session: Session = Depends(get_session)
) -> list[Recommendation]:
    """List persistent mitigations for a security report."""
    if session.get(SecurityReport, report_id) is None:
        raise HTTPException(
            status_code=404, detail=f"Security report '{report_id}' was not found."
        )
    return list(
        session.scalars(select(Recommendation).where(Recommendation.report_id == report_id))
    )
