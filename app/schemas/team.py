from pydantic import BaseModel


class TeamResponse(BaseModel):
    id: int
    name: str
    department: str
    manager_id: int

    class Config:
        orm_mode = True