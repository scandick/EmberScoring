from scorer import (
    score_current_burnout,
    forecast_burnout,
    generate_recommendations,
)
from schemas import EmployeeMetrics


metrics = EmployeeMetrics(
    employee_id="E001",
    team_id="sales",
    overtime=26,
    sick_leave=4,
    vacation_gap=180,
    night_activity=12,
    meeting_load=18,
)

print("=== CURRENT SCORE ===")
print(score_current_burnout(metrics).model_dump())

print("\n=== FORECAST ===")
print(forecast_burnout(metrics, 30).model_dump())

print("\n=== RECOMMENDATIONS ===")
print(generate_recommendations(metrics).model_dump())