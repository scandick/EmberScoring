from datetime import date

from pydantic import BaseModel


class MetricResponse(BaseModel):
    id: int
    employee_id: int
    metric_date: date

    overtime_hours: float
    sick_leave_days: int
    vacation_gap_days: int
    night_activity_pct: float
    meeting_load: float

    class Config:
        orm_mode = True


class TeamMetricSummary(BaseModel):
    team_id: int

    avg_overtime_hours: float
    avg_sick_leave_days: float
    avg_vacation_gap_days: float
    avg_night_activity_pct: float
    avg_meeting_load: float