from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from app.core.database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    metric_date = Column(Date, nullable=False)

    overtime_hours = Column(Float, default=0)
    sick_leave_days = Column(Integer, default=0)
    vacation_gap_days = Column(Integer, default=0)
    night_activity_pct = Column(Float, default=0)
    meeting_load = Column(Float, default=0)