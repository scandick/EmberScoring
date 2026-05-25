from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.employee_score_repository import EmployeeScoreRepository
from app.schemas.employee import EmployeeResponse
from app.schemas.team import TeamResponse


router = APIRouter(prefix="/api/v1")


@router.get(
    "/employees/{id}",
    response_model=EmployeeResponse,
)
def get_employee(
    id: int,
    db: Session = Depends(get_db),
):

    employee = EmployeeRepository.get_employee(db, id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.get(
    "/employees",
    response_model=list[EmployeeResponse],
)
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    team: str | None = Query(None),
    job_role: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return EmployeeRepository.get_all_employees(
        db,
        skip=skip,
        limit=limit,
        team=team,
        job_role=job_role,
    )


@router.get(
    "/teams",
    response_model=list[TeamResponse],
)
def get_teams(db: Session = Depends(get_db)):
    return EmployeeScoreRepository.get_team_counts(db)


@router.get(
    "/teams/{team}/employees",
    response_model=list[EmployeeResponse],
)
def get_team_employees(
    team: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    job_role: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return EmployeeRepository.get_team_employees(
        db,
        team,
        skip=skip,
        limit=limit,
        job_role=job_role,
    )
