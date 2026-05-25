from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.employee_score import EmployeeScore


class EmployeeScoreRepository:

    @staticmethod
    def save_latest_score(
        db: Session,
        *,
        employee_id: int,
        created_at,
        risk_score: float,
        risk_level: str,
        summary: str,
        key_factors: list[str],
        raw_response: dict,
    ) -> EmployeeScore:
        existing = (
            db.query(EmployeeScore)
            .filter(EmployeeScore.employee_id == employee_id)
            .first()
        )

        if existing is None:
            existing = EmployeeScore(employee_id=employee_id)
            db.add(existing)

        existing.created_at = created_at
        existing.risk_score = risk_score
        existing.risk_level = risk_level
        existing.summary = summary
        existing.key_factors = key_factors
        existing.raw_response = raw_response

        db.commit()
        db.refresh(existing)
        return existing

    @staticmethod
    def get_latest_score(db: Session, employee_id: int) -> EmployeeScore | None:
        return (
            db.query(EmployeeScore)
            .filter(EmployeeScore.employee_id == employee_id)
            .first()
        )

    @staticmethod
    def list_latest_scores(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        team: str | None = None,
        job_role: str | None = None,
    ) -> list[EmployeeScore]:
        query = db.query(EmployeeScore).join(Employee, Employee.id == EmployeeScore.employee_id)

        if team:
            query = query.filter(Employee.team == team)

        if job_role:
            query = query.filter(Employee.job_role == job_role)

        return (
            query.order_by(EmployeeScore.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_score_stats(
        db: Session,
        *,
        team: str | None = None,
        job_role: str | None = None,
    ) -> dict[str, int]:
        query = db.query(EmployeeScore).join(Employee, Employee.id == EmployeeScore.employee_id)

        if team:
            query = query.filter(Employee.team == team)

        if job_role:
            query = query.filter(Employee.job_role == job_role)

        scored_employees = query.count()
        at_risk_employees = (
            query.filter(EmployeeScore.risk_level.in_(["high", "critical"]))
            .count()
        )

        return {
            "scored_employees": scored_employees,
            "at_risk_employees": at_risk_employees,
        }

    @staticmethod
    def get_team_counts(db: Session) -> list[dict[str, int | str]]:
        rows = (
            db.query(
                Employee.team.label("team"),
                func.count(Employee.id).label("employee_count"),
            )
            .group_by(Employee.team)
            .order_by(Employee.team.asc())
            .all()
        )

        return [
            {
                "team": row.team,
                "employee_count": row.employee_count,
            }
            for row in rows
        ]
