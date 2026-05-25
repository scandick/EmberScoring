from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.employee_score_repository import EmployeeScoreRepository
from app.repositories.llm_service import LLMService

from llm.schemas import BurnoutScoreResult
from llm.schemas import RecommendationResult
from app.schemas.employee_score import EmployeeScoreStatsResponse
from app.schemas.employee_score import EmployeeScoreSummaryResponse


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

    employee_metrics = LLMService.build_employee_metrics(employee)

    result = LLMService.score(employee_metrics)

    EmployeeScoreRepository.save_latest_score(
        db,
        employee_id=id,
        created_at=datetime.utcnow(),
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        summary=getattr(result, "summary", ""),
        key_factors=result.key_factors,
        raw_response=result.model_dump(),
    )

    return result


@router.get(
    "/score/employee/{id}/latest",
    response_model=EmployeeScoreSummaryResponse,
)
def get_latest_employee_score(
    id: int,
    db: Session = Depends(get_db),
) -> EmployeeScoreSummaryResponse:
    score = EmployeeScoreRepository.get_latest_score(db, id)

    if not score:
        raise HTTPException(status_code=404, detail="Score not found")

    return EmployeeScoreSummaryResponse(
        employee_id=score.employee_id,
        created_at=score.created_at,
        risk_score=score.risk_score,
        risk_level=score.risk_level,
        summary=score.summary,
        key_factors=score.key_factors or [],
    )


@router.get(
    "/score/latest",
    response_model=list[EmployeeScoreSummaryResponse],
)
def list_latest_scores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    team: str | None = Query(None),
    job_role: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[EmployeeScoreSummaryResponse]:
    scores = EmployeeScoreRepository.list_latest_scores(
        db,
        skip=skip,
        limit=limit,
        team=team,
        job_role=job_role,
    )

    return [
        EmployeeScoreSummaryResponse(
            employee_id=score.employee_id,
            created_at=score.created_at,
            risk_score=score.risk_score,
            risk_level=score.risk_level,
            summary=score.summary,
            key_factors=score.key_factors or [],
        )
        for score in scores
    ]


@router.get(
    "/score/stats",
    response_model=EmployeeScoreStatsResponse,
)
def get_score_stats(
    team: str | None = Query(None),
    job_role: str | None = Query(None),
    db: Session = Depends(get_db),
) -> EmployeeScoreStatsResponse:
    return EmployeeScoreStatsResponse(
        **EmployeeScoreRepository.get_score_stats(
            db,
            team=team,
            job_role=job_role,
        )
    )


@router.post(
    "/score/employee/{id}/recommendations",
    response_model=RecommendationResult,
)
def get_recommendations(
    id: int,
    db: Session = Depends(get_db),
) -> RecommendationResult:
    employee = EmployeeRepository.get_employee(db, id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee_metrics = LLMService.build_employee_metrics(employee)

    return LLMService.recommendations(employee_metrics)
