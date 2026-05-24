from pydantic import BaseModel


class EmployeeResponse(BaseModel):
    id: int
    employee_id: str
    team: str
    job_role: str
    years_at_company: int
    work_life_balance: str
    job_satisfaction: str
    performance_rating: str
    number_of_promotions: int
    overtime_flag: str
    employee_recognition: str
    leadership_opportunities: str
    innovation_opportunities: str
    attrition: str

    model_config = {"from_attributes": True}
