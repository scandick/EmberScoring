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
    JOB_ROLE_TO_TEAM = {
        "Technology": "Engineering",
        "Media": "Marketing",
        "Finance": "Operations",
        "Education": "People Operations",
        "Healthcare": "Customer Success",
    }

    @staticmethod
    def _string_flag_from_bool_like(value, yes_value: str = "Yes", no_value: str = "No") -> str:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"yes", "y", "true", "1"}:
                return yes_value
            if normalized in {"no", "n", "false", "0"}:
                return no_value
        return yes_value if value else no_value

    @staticmethod
    def _resolve_team(employee: Employee) -> str:
        explicit_team = getattr(employee, "team", None)
        if explicit_team:
            return explicit_team

        job_role = getattr(employee, "job_role", getattr(employee, "role", "Unknown"))
        return LLMService.JOB_ROLE_TO_TEAM.get(job_role, "General")

    @staticmethod
    def build_employee_metrics(
        employee: Employee,
        metric: Metric,
    ) -> EmployeeMetrics:

        return EmployeeMetrics(
            employee_id=str(employee.id),
            team=LLMService._resolve_team(employee),
            job_role=getattr(employee, "job_role", getattr(employee, "role", "Unknown")),
            years_at_company=max(getattr(employee, "years_at_company", getattr(employee, "tenure_months", 0)), 0),
            work_life_balance=getattr(employee, "work_life_balance", "Unknown"),
            job_satisfaction=getattr(employee, "job_satisfaction", "Unknown"),
            performance_rating=getattr(employee, "performance_rating", "Unknown"),
            number_of_promotions=max(getattr(employee, "number_of_promotions", 0), 0),
            overtime_flag=LLMService._string_flag_from_bool_like(
                getattr(employee, "overtime_flag", metric.overtime_hours > 0)
            ),
            employee_recognition=getattr(employee, "employee_recognition", "Unknown"),
            leadership_opportunities=LLMService._string_flag_from_bool_like(
                getattr(employee, "leadership_opportunities", False)
            ),
            innovation_opportunities=LLMService._string_flag_from_bool_like(
                getattr(employee, "innovation_opportunities", False)
            ),
            attrition=getattr(employee, "attrition", "Unknown"),
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
