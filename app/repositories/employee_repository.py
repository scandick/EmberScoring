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
    def get_all_employees(db: Session):
        return db.query(Employee).all()

    @staticmethod
    def get_team_employees(db: Session, team_id: int):
        return (
            db.query(Employee)
            .filter(Employee.team_id == team_id)
            .all()
        )