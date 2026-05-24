from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.metric_repository import MetricRepository
from app.schemas.metric import TeamMetricSummary


router = APIRouter(prefix="/api/v1")


@router.get(
    "/metrics/team/{team}/summary",
    response_model=TeamMetricSummary,
)
def get_team_metrics_summary(
    team: str,
    db: Session = Depends(get_db),
):

    result = MetricRepository.get_team_metrics_summary(db, team)
    if not result:
        raise HTTPException(status_code=404, detail="Team not found")

    return TeamMetricSummary(**result)
