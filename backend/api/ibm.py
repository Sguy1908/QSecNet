"""IBM Quantum comparison API."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.config import get_settings
from backend.services.ibm_service import QuantumExecutionService

router = APIRouter(prefix="/ibm", tags=["ibm-quantum"])


class IBMComparisonRequest(BaseModel):
    shots: int = Field(default=1024, ge=16, le=8192)


class IBMComparisonResponse(BaseModel):
    local_counts: dict[str, int]
    remote_available: bool
    remote_counts: dict[str, int] | None
    backend_name: str | None
    message: str


@router.get("/status")
def status() -> dict[str, bool]:
    """Expose whether remote execution is configured without revealing secrets."""
    return {"configured": bool(get_settings().ibm_quantum_token)}


@router.post("/compare", response_model=IBMComparisonResponse)
def compare(payload: IBMComparisonRequest) -> IBMComparisonResponse:
    """Compare a local Aer Bell-pair execution with optional IBM hardware."""
    result = QuantumExecutionService(get_settings()).compare(payload.shots)
    return IBMComparisonResponse(**result.__dict__)
