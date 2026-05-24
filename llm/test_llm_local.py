from llm.scorer import (
    score_current_burnout,
    forecast_burnout,
    generate_recommendations,
)
from llm.schemas import EmployeeMetrics


metrics = EmployeeMetrics(
    employee_id="E001",
    job_role="Sales",
    years_at_company=6,
    work_life_balance="Poor",
    job_satisfaction="Low",
    performance_rating="Average",
    number_of_promotions=0,
    overtime_flag="Yes",
    employee_recognition="Low",
    leadership_opportunities="No",
    innovation_opportunities="No",
    attrition="Stayed",
)

print("=== CURRENT SCORE ===")
print(score_current_burnout(metrics).model_dump())

print("\n=== FORECAST ===")
print(forecast_burnout(metrics, 30).model_dump())

print("\n=== RECOMMENDATIONS ===")
print(generate_recommendations(metrics).model_dump())
