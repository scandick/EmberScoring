from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.employees import router as employees_router
from app.api.v1.forecast import router as forecast_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.score import router as score_router
from app.core.database import Base
from app.core.database import engine
from app.models.employee import Employee  # noqa: F401
from app.models.employee_score import EmployeeScore  # noqa: F401
from app.models.metric import Metric  # noqa: F401
from app.models.prediction import Prediction  # noqa: F401
from app.models.team import Team  # noqa: F401


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Burnout Analytics API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(employees_router)
app.include_router(metrics_router)
app.include_router(score_router)
app.include_router(forecast_router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "burnout-api",
    }
