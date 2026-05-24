from pydantic import BaseModel


class TeamResponse(BaseModel):
    id: int
    name: str
    department: str
    manager_id: int

    model_config = {"from_attributes": True}
