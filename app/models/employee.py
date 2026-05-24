from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.core.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, nullable=False, index=True)
    team = Column(String, nullable=False, index=True)
    job_role = Column(String, nullable=False)
    years_at_company = Column(Integer, nullable=False)
    work_life_balance = Column(String, nullable=False)
    job_satisfaction = Column(String, nullable=False)
    performance_rating = Column(String, nullable=False)
    number_of_promotions = Column(Integer, nullable=False, default=0)
    overtime_flag = Column(String, nullable=False)
    employee_recognition = Column(String, nullable=False)
    leadership_opportunities = Column(String, nullable=False)
    innovation_opportunities = Column(String, nullable=False)
    attrition = Column(String, nullable=False)
