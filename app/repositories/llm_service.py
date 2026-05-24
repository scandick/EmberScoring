from llm.scorer import (
    forecast_burnout,
    generate_recommendations,
    score_current_burnout,
)

from llm.schemas import BurnoutForecastResult
from llm.schemas import BurnoutScoreResult
from llm.schemas import EmployeeMetrics
from llm.schemas import RecommendationResult

from app.models.employee import Employee
from app.models.metric import Metric


class LLMService:

    @staticmethod
    def build_employee_metrics(
        employee: Employee,
        metric: Metric,
    ) -> EmployeeMetrics:

        return EmployeeMetrics(
            employee_id=str(employee.id),
            team_id=str(employee.team_id),
            overtime=metric.overtime_hours,
            sick_leave=metric.sick_leave_days,
            vacation_gap=metric.vacation_gap_days,
            night_activity=metric.night_activity_pct,
            meeting_load=metric.meeting_load,
        )

    @staticmethod
    def score(metrics: EmployeeMetrics) -> BurnoutScoreResult:
        return score_current_burnout(metrics)

    @staticmethod
    def forecast(
        metrics: EmployeeMetrics,
        horizon_days: int,
    ) -> BurnoutForecastResult:
        return forecast_burnout(metrics, horizon_days)

    @staticmethod
    def recommendations(metrics: EmployeeMetrics) -> RecommendationResult:
        return generate_recommendations(metrics)
