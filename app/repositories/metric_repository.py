from datetime import date

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.metric import Metric


class MetricRepository:
    WORK_LIFE_BALANCE_WEIGHT = {
        "Poor": 10,
        "Fair": 6,
        "Good": 3,
        "Excellent": 0,
    }

    JOB_SATISFACTION_WEIGHT = {
        "Low": 8,
        "Medium": 4,
        "High": 1,
        "Very High": 0,
    }

    PERFORMANCE_WEIGHT = {
        "Low": 4,
        "Average": 2,
        "High": 1,
    }

    RECOGNITION_WEIGHT = {
        "Low": 5,
        "Medium": 2,
        "High": 0,
    }

    TEAM_MEETING_BASE = {
        "Engineering": 10.0,
        "Marketing": 13.0,
        "Operations": 12.0,
        "People Operations": 11.0,
        "Customer Success": 15.0,
    }

    @staticmethod
    def _safe_lookup(mapping: dict[str, int | float], value: str, default: int | float = 0) -> int | float:
        return mapping.get(value, default)

    @staticmethod
    def _build_metric_snapshot(employee: Employee) -> Metric:
        overtime_hours = 4.0 if employee.overtime_flag == "No" else 14.0
        overtime_hours += MetricRepository._safe_lookup(
            MetricRepository.WORK_LIFE_BALANCE_WEIGHT,
            employee.work_life_balance,
            4,
        ) * 0.8
        overtime_hours += MetricRepository._safe_lookup(
            MetricRepository.JOB_SATISFACTION_WEIGHT,
            employee.job_satisfaction,
            3,
        ) * 0.5

        sick_leave_days = int(
            1
            + MetricRepository._safe_lookup(
                MetricRepository.WORK_LIFE_BALANCE_WEIGHT,
                employee.work_life_balance,
                2,
            ) / 3
            + MetricRepository._safe_lookup(
                MetricRepository.RECOGNITION_WEIGHT,
                employee.employee_recognition,
                1,
            ) / 2
        )

        vacation_gap_days = int(
            30
            + employee.years_at_company * 4
            + (0 if employee.number_of_promotions > 0 else 20)
            + MetricRepository._safe_lookup(
                MetricRepository.RECOGNITION_WEIGHT,
                employee.employee_recognition,
                2,
            ) * 10
        )

        night_activity_pct = float(
            min(
                100,
                8
                + (20 if employee.overtime_flag == "Yes" else 0)
                + MetricRepository._safe_lookup(
                    MetricRepository.WORK_LIFE_BALANCE_WEIGHT,
                    employee.work_life_balance,
                    4,
                ) * 2
                + MetricRepository._safe_lookup(
                    MetricRepository.PERFORMANCE_WEIGHT,
                    employee.performance_rating,
                    2,
                ) * 1.5,
            )
        )

        meeting_load = float(
            MetricRepository.TEAM_MEETING_BASE.get(employee.team, 10.0)
            + (3 if employee.leadership_opportunities == "Yes" else 0)
            + (2 if employee.innovation_opportunities == "Yes" else 0)
        )

        return Metric(
            employee_id=employee.id,
            metric_date=date.today(),
            overtime_hours=round(overtime_hours, 1),
            sick_leave_days=max(sick_leave_days, 0),
            vacation_gap_days=max(vacation_gap_days, 0),
            night_activity_pct=round(night_activity_pct, 1),
            meeting_load=round(meeting_load, 1),
        )

    @staticmethod
    def get_employee_metrics(db: Session, employee_id: int):
        employee = (
            db.query(Employee)
            .filter(Employee.id == employee_id)
            .first()
        )
        if not employee:
            return []

        return [MetricRepository._build_metric_snapshot(employee)]

    @staticmethod
    def get_latest_employee_metrics(db: Session, employee_id: int):
        employee = (
            db.query(Employee)
            .filter(Employee.id == employee_id)
            .first()
        )
        if not employee:
            return None

        return MetricRepository._build_metric_snapshot(employee)

    @staticmethod
    def get_team_metrics_summary(db: Session, team: str):
        employees = (
            db.query(Employee)
            .filter(Employee.team == team)
            .all()
        )
        if not employees:
            return None

        metrics = [MetricRepository._build_metric_snapshot(employee) for employee in employees]

        return {
            "team": team,
            "avg_overtime_hours": round(sum(metric.overtime_hours for metric in metrics) / len(metrics), 1),
            "avg_sick_leave_days": round(sum(metric.sick_leave_days for metric in metrics) / len(metrics), 1),
            "avg_vacation_gap_days": round(sum(metric.vacation_gap_days for metric in metrics) / len(metrics), 1),
            "avg_night_activity_pct": round(sum(metric.night_activity_pct for metric in metrics) / len(metrics), 1),
            "avg_meeting_load": round(sum(metric.meeting_load for metric in metrics) / len(metrics), 1),
        }
