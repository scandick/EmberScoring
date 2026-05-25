from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:

    @staticmethod
    def get_employee(db: Session, employee_id: int):
        return (
            db.query(Employee)
            .filter(Employee.id == employee_id)
            .first()
        )

    @staticmethod
    def get_all_employees(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        team: str | None = None,
        job_role: str | None = None,
    ):
        query = db.query(Employee)

        if team:
            query = query.filter(Employee.team == team)

        if job_role:
            query = query.filter(Employee.job_role == job_role)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_team_employees(
        db: Session,
        team: str,
        skip: int = 0,
        limit: int = 100,
        job_role: str | None = None,
    ):
        query = db.query(Employee).filter(Employee.team == team)

        if job_role:
            query = query.filter(Employee.job_role == job_role)

        return query.offset(skip).limit(limit).all()
