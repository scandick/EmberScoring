import csv
from pathlib import Path
import sys

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import SessionLocal
from app.core.database import engine
from app.models.employee import Employee
from app.models.metric import Metric
from app.models.prediction import Prediction


CSV_PATH = PROJECT_ROOT / "data" / "full_attrition_dataset.csv"


def recreate_employees_table() -> None:
    Prediction.__table__.drop(bind=engine, checkfirst=True)
    Metric.__table__.drop(bind=engine, checkfirst=True)
    Employee.__table__.drop(bind=engine, checkfirst=True)
    Employee.__table__.create(bind=engine, checkfirst=True)
    Metric.__table__.create(bind=engine, checkfirst=True)
    Prediction.__table__.create(bind=engine, checkfirst=True)


def import_employees() -> int:
    session = SessionLocal()

    try:
        with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            employees = []

            for row in reader:
                employees.append(
                    Employee(
                        employee_id=row["employee_id"],
                        team=row["team"],
                        job_role=row["job_role"],
                        years_at_company=int(row["years_at_company"]),
                        work_life_balance=row["work_life_balance"],
                        job_satisfaction=row["job_satisfaction"],
                        performance_rating=row["performance_rating"],
                        number_of_promotions=int(row["number_of_promotions"]),
                        overtime_flag=row["overtime_flag"],
                        employee_recognition=row["employee_recognition"],
                        leadership_opportunities=row["leadership_opportunities"],
                        innovation_opportunities=row["innovation_opportunities"],
                        attrition=row["attrition"],
                    )
                )

        session.execute(text("DELETE FROM employees"))
        session.bulk_save_objects(employees)
        session.commit()

        return len(employees)
    finally:
        session.close()


def main() -> None:
    recreate_employees_table()
    imported_count = import_employees()
    print(f"Imported {imported_count} employees from {CSV_PATH}")


if __name__ == "__main__":
    main()
