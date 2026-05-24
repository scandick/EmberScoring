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
    ):
        return (
            db.query(Employee)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_team_employees(
        db: Session,
        team: str,
        skip: int = 0,
        limit: int = 100,
    ):
        return (
            db.query(Employee)
            .filter(Employee.team == team)
            .offset(skip)
            .limit(limit)
            .all()
        )
