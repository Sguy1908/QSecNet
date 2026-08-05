<<<<<<< HEAD
"""IBM Quantum Runtime comparison endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.database import get_session
from backend.models import Simulation, SimulationStatus
from backend.services.ibm_service import IBMQuantumService, IBMRuntimeUnavailableError

router = APIRouter(tags=["IBM Quantum"])


class IBMComparisonRequest(BaseModel):
    backend_name: str = Field(min_length=1, max_length=100)
    shots: int = Field(default=1024, ge=1, le=100_000)


class IBMComparisonRead(BaseModel):
    simulator_qber: float
    hardware_error_rate: float
    qber_difference: float
    hardware: dict[str, Any]


def _ibm_service() -> IBMQuantumService:
    settings = get_settings()
    return IBMQuantumService(
        token=getattr(settings, "ibm_quantum_token", None),
        instance=getattr(settings, "ibm_quantum_instance", None),
    )


@router.post(
    "/simulations/{simulation_id}/ibm-comparison", response_model=IBMComparisonRead
)
def compare_with_ibm_hardware(
    simulation_id: str,
    payload: IBMComparisonRequest,
    session: Session = Depends(get_session),
) -> IBMComparisonRead:
    """Compare simulator QBER with an empirically measured IBM hardware error rate."""
    simulation = session.get(Simulation, simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail=f"Simulation '{simulation_id}' was not found.")
    if simulation.status != SimulationStatus.COMPLETED or simulation.result is None:
        raise HTTPException(status_code=409, detail="IBM comparison requires a completed simulation.")
    try:
        hardware = _ibm_service().run_zero_state_probe(payload.backend_name, payload.shots)
    except (IBMRuntimeUnavailableError, ValueError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    simulator_qber = float(simulation.result.get("qber", 0.0))
    return IBMComparisonRead(
        simulator_qber=simulator_qber,
        hardware_error_rate=hardware.error_rate,
        qber_difference=hardware.error_rate - simulator_qber,
        hardware=hardware.as_dict(),
    )
=======
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
>>>>>>> origin/main
