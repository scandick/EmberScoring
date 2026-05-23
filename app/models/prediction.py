from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String

from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id"))

    created_at = Column(DateTime)

    horizon_months = Column(Integer)

    risk_score = Column(Float)
    risk_level = Column(String)

    forecast_text = Column(String)

    raw_response = Column(JSON)