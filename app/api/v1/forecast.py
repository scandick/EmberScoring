from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.prediction import Prediction
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.llm_service import LLMService
from app.repositories.prediction_repository import PredictionRepository

from llm.schemas import BurnoutForecastResult


router = APIRouter(prefix="/api/v1")

ALLOWED_HORIZONS = [7, 14, 30, 60]


@router.post(
    "/forecast/employee/{id}",
    response_model=BurnoutForecastResult,
)
def forecast_employee(
    id: int,
    horizon_days: int = Query(30),
    db: Session = Depends(get_db),
):

    if horizon_days not in ALLOWED_HORIZONS:
        raise HTTPException(
            status_code=400,
            detail=f"Allowed horizons: {ALLOWED_HORIZONS}",
        )

    employee = EmployeeRepository.get_employee(db, id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee_metrics = LLMService.build_employee_metrics(employee)

    result = LLMService.forecast(
        employee_metrics,
        horizon_days,
    )

    prediction = Prediction(
        employee_id=id,
        created_at=datetime.utcnow(),
        horizon_months=horizon_days,
        risk_score=(
            result.forecast_points[-1].predicted_score
            if result.forecast_points else None
        ),
        risk_level=(
            result.forecast_points[-1].risk_level
            if result.forecast_points else None
        ),
        forecast_text=result.forecast_summary,
        raw_response=result.model_dump(),
    )

    PredictionRepository.save_prediction(db, prediction)

    return result
