from sqlalchemy.orm import Session

from app.models.consultation import Consultation


class ConsultationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        user_message: str,
        ai_response: str,
        risk_level: str,
    ) -> Consultation:

        consultation = Consultation(
            user_id=user_id,
            user_message=user_message,
            ai_response=ai_response,
            risk_level=risk_level,
        )

        self.db.add(consultation)
        self.db.commit()
        self.db.refresh(consultation)

        return consultation

    def get_by_user(
        self,
        user_id: int,
    ):
        return (
            self.db.query(Consultation)
            .filter(Consultation.user_id == user_id)
            .order_by(Consultation.created_at.desc())
            .all()
        )

    def get_by_id(
        self,
        consultation_id: int,
    ):
        return (
            self.db.query(Consultation)
            .filter(Consultation.id == consultation_id)
            .first()
        )

    def delete(
        self,
        consultation: Consultation,
    ):
        self.db.delete(consultation)
        self.db.commit()

    def get_dashboard_stats(
        self,
        user_id: int,
    ):
        consultations = self.get_by_user(user_id)

        total = len(consultations)

        high = sum(
            1
            for consultation in consultations
            if consultation.risk_level == "high"
        )

        medium = sum(
            1
            for consultation in consultations
            if consultation.risk_level == "medium"
        )

        low = sum(
            1
            for consultation in consultations
            if consultation.risk_level == "low"
        )

        return {
            "total_consultations": total,
            "high_risk": high,
            "medium_risk": medium,
            "low_risk": low,
            "last_consultation": (
                consultations[0].created_at
                if consultations
                else None
            ),
            "recent_consultations": consultations[:5],
        }