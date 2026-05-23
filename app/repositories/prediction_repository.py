from sqlalchemy.orm import Session

from app.models.prediction import Prediction


class PredictionRepository:

    @staticmethod
    def save_prediction(db: Session, prediction: Prediction):
        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return prediction

    @staticmethod
    def get_prediction_history(db: Session, employee_id: int):
        return (
            db.query(Prediction)
            .filter(Prediction.employee_id == employee_id)
            .order_by(Prediction.created_at.desc())
            .all()
        )