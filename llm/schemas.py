from typing import Literal
from pydantic import BaseModel, Field


class EmployeeMetrics(BaseModel):
    employee_id: str
    team: str
    job_role: str
    years_at_company: int = Field(ge=0)
    work_life_balance: str
    job_satisfaction: str
    performance_rating: str
    number_of_promotions: int = Field(ge=0)
    overtime_flag: str
    employee_recognition: str
    leadership_opportunities: str
    innovation_opportunities: str
    attrition: str

    model_config = {"extra": "forbid"}


class BurnoutScoreResult(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: Literal["low", "moderate", "high", "critical"]
    key_factors: list[str] = Field(default_factory=list)
    summary: str

    model_config = {"extra": "forbid"}


class ForecastPoint(BaseModel):
    day: int = Field(ge=1, le=365)
    predicted_score: int = Field(ge=0, le=100)
    risk_level: Literal["low", "moderate", "high", "critical"]

    model_config = {"extra": "forbid"}


class BurnoutForecastResult(BaseModel):
    horizon_days: int = Field(ge=1, le=365)
    trend: Literal["improving", "stable", "declining", "volatile"]
    forecast_summary: str
    confidence_note: str
    forecast_points: list[ForecastPoint] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class RecommendationResult(BaseModel):
    priority: Literal["low", "medium", "high"]
    manager_actions: list[str] = Field(default_factory=list)
    employee_support_actions: list[str] = Field(default_factory=list)
    watch_items: list[str] = Field(default_factory=list)
    summary: str

    model_config = {"extra": "forbid"}
