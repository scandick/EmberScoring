from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String

from app.core.database import Base


class EmployeeScore(Base):
    __tablename__ = "employee_scores"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    key_factors = Column(JSON, nullable=False, default=list)
    raw_response = Column(JSON, nullable=False)
