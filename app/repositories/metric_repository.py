from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.metric import Metric


class MetricRepository:

    @staticmethod
    def get_employee_metrics(db: Session, employee_id: int):
        return (
            db.query(Metric)
            .filter(Metric.employee_id == employee_id)
            .all()
        )

    @staticmethod
    def get_latest_employee_metrics(db: Session, employee_id: int):
        return (
            db.query(Metric)
            .filter(Metric.employee_id == employee_id)
            .order_by(Metric.metric_date.desc())
            .first()
        )

    @staticmethod
    def get_team_metrics_summary(db: Session, team_id: int):
        return (
            db.query(
                func.avg(Metric.overtime_hours),
                func.avg(Metric.sick_leave_days),
                func.avg(Metric.vacation_gap_days),
                func.avg(Metric.night_activity_pct),
                func.avg(Metric.meeting_load),
            )
            .join(Employee, Employee.id == Metric.employee_id)
            .filter(Employee.team_id == team_id)
            .first()
        )