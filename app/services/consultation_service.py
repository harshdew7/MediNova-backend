from sqlalchemy.orm import Session

from app.repositories.consultation_repository import ConsultationRepository


def list_consultations(
    db: Session,
    user_id: int,
):
    repository = ConsultationRepository(db)

    return repository.get_by_user(user_id)


def retrieve_consultation(
    db: Session,
    consultation_id: int,
    user_id: int,
):
    repository = ConsultationRepository(db)

    consultation = repository.get_by_id(consultation_id)

    if consultation is None:
        return None

    if consultation.user_id != user_id:
        return None

    return consultation


def delete_consultation(
    db: Session,
    consultation_id: int,
    user_id: int,
):
    repository = ConsultationRepository(db)

    consultation = repository.get_by_id(consultation_id)

    if consultation is None:
        return False

    if consultation.user_id != user_id:
        return False

    repository.delete(consultation)

    return True


def dashboard(
    db: Session,
    user_id: int,
):
    repository = ConsultationRepository(db)

    return repository.get_dashboard_stats(user_id)