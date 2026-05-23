from pydantic import BaseModel


class EmployeeResponse(BaseModel):
    id: int
    team_id: int
    name: str
    role: str
    department: str
    tenure_months: int

    class Config:
        orm_mode = True