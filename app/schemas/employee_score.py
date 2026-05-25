from datetime import datetime

from pydantic import BaseModel


class EmployeeScoreSummaryResponse(BaseModel):
    employee_id: int
    created_at: datetime
    risk_score: float
    risk_level: str
    summary: str
    key_factors: list[str]

    model_config = {"from_attributes": True}


class EmployeeScoreStatsResponse(BaseModel):
    scored_employees: int
    at_risk_employees: int


class TeamDirectoryResponse(BaseModel):
    team: str
    employee_count: int
