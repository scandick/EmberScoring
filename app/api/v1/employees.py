from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeResponse


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
    db: Session = Depends(get_db),
):
    return EmployeeRepository.get_all_employees(db)


@router.get(
    "/teams/{team}/employees",
    response_model=list[EmployeeResponse],
)
def get_team_employees(
    team: str,
    db: Session = Depends(get_db),
):
    return EmployeeRepository.get_team_employees(db, team)
