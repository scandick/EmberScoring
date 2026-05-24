from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.prediction import Prediction
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.llm_service import LLMService
from app.repositories.metric_repository import MetricRepository
from app.repositories.prediction_repository import PredictionRepository

from llm.schemas import BurnoutScoreResult
from llm.schemas import EmployeeMetrics
from llm.schemas import RecommendationResult


router = APIRouter(prefix="/api/v1")


@router.post(
    "/score/employee/{id}",
    response_model=BurnoutScoreResult,
)
def score_employee(
    id: int,
    db: Session = Depends(get_db),
):

    employee = EmployeeRepository.get_employee(db, id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    metric = MetricRepository.get_latest_employee_metrics(db, id)

    if not metric:
        raise HTTPException(status_code=404, detail="Metrics not found")

    employee_metrics = LLMService.build_employee_metrics(
        employee,
        metric,
    )

    result = LLMService.score(employee_metrics)

    prediction = Prediction(
        employee_id=id,
        created_at=datetime.utcnow(),
        horizon_months=0,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        forecast_text=getattr(result, "summary", ""),
        raw_response=result.model_dump(),
    )

    PredictionRepository.save_prediction(db, prediction)

    return result


@router.get(
    "/score/employee/{id}/history",
)
def get_score_history(
    id: int,
    db: Session = Depends(get_db),
):
    return PredictionRepository.get_prediction_history(db, id)


@router.post(
    "/score/employee/recommendations",
    response_model=RecommendationResult,
)
def get_recommendations(
    metrics: EmployeeMetrics,
) -> RecommendationResult:
    return LLMService.recommendations(metrics)
