from pydantic import BaseModel


class TeamResponse(BaseModel):
    team: str
    employee_count: int

    model_config = {"from_attributes": True}
