from fastapi import APIRouter
from backend.app.services.experiment_service import experiment_service

router = APIRouter(prefix="/benchmark", tags=["Research Benchmark Lab"])

@router.get("/run-experiment")
def run_comparative_experiment():
    """
    Executes the live research benchmark comparing Approach A (Direct LLM),
    Approach B (NLP + LLM), and Approach C (NLP + Deterministic State Machine).
    """
    return experiment_service.run_comparative_experiment()
