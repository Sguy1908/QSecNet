"""IBM Quantum adapter endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.ibm_service import IBMCompareResponse, compare_bb84

router = APIRouter(prefix="/ibm", tags=["ibm"])


class IBMCompareRequest(BaseModel):
    rounds: int = Field(default=512, ge=16, le=10000)
    seed: int | None = None


@router.post("/compare", response_model=IBMCompareResponse)
def compare(payload: IBMCompareRequest) -> IBMCompareResponse:
    """Compare local BB84 output to IBM backend availability/metadata."""
    return compare_bb84(payload.rounds, payload.seed)
