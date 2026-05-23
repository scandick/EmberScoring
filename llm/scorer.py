from client import get_default_llm_client
from prompts import (
    build_current_burnout_messages,
    build_forecast_messages,
    build_recommendation_messages,
)
from schemas import (
    BurnoutForecastResult,
    BurnoutScoreResult,
    EmployeeMetrics,
    RecommendationResult,
)


def score_current_burnout(metrics: EmployeeMetrics) -> BurnoutScoreResult:
    messages = build_current_burnout_messages(metrics)
    return get_default_llm_client().call_structured(messages, BurnoutScoreResult)


def forecast_burnout(
    metrics: EmployeeMetrics,
    horizon_days: int,
) -> BurnoutForecastResult:
    messages = build_forecast_messages(metrics, horizon_days)
    return get_default_llm_client().call_structured(messages, BurnoutForecastResult)


def generate_recommendations(metrics: EmployeeMetrics) -> RecommendationResult:
    messages = build_recommendation_messages(metrics)
    return get_default_llm_client().call_structured(messages, RecommendationResult)
