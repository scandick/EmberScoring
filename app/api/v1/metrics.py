from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.metric_repository import MetricRepository
from app.schemas.metric import MetricResponse
from app.schemas.metric import TeamMetricSummary


router = APIRouter(prefix="/api/v1")


@router.get(
    "/metrics/employee/{id}",
    response_model=list[MetricResponse],
)
def get_employee_metrics(
    id: int,
    db: Session = Depends(get_db),
):
    return MetricRepository.get_employee_metrics(db, id)


@router.get(
    "/metrics/team/{id}/summary",
    response_model=TeamMetricSummary,
)
def get_team_metrics_summary(
    id: int,
    db: Session = Depends(get_db),
):

    result = MetricRepository.get_team_metrics_summary(db, id)

    return TeamMetricSummary(
        team_id=id,
        avg_overtime_hours=result[0] or 0,
        avg_sick_leave_days=result[1] or 0,
        avg_vacation_gap_days=result[2] or 0,
        avg_night_activity_pct=result[3] or 0,
        avg_meeting_load=result[4] or 0,
    )