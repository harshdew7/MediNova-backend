from sqlalchemy.orm import Session

from app.models.consultation import Consultation


def get_consultations_by_user(
    db: Session,
    user_id: int,
):
    return (
        db.query(Consultation)
        .filter(Consultation.user_id == user_id)
        .order_by(Consultation.created_at.desc())
        .all()
    )


def get_consultation_by_id(
    db: Session,
    consultation_id: int,
    user_id: int,
):
    return (
        db.query(Consultation)
        .filter(
            Consultation.id == consultation_id,
            Consultation.user_id == user_id,
        )
        .first()
    )