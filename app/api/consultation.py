from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.exceptions import MediNovaException
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.consultation import ConsultationResponse
from app.services.consultation_service import (
    delete_consultation,
    list_consultations,
    retrieve_consultation,
)

router = APIRouter(
    prefix="/consultations",
    tags=["Consultations"],
)


@router.get(
    "/",
    response_model=list[ConsultationResponse],
)
def get_consultations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_consultations(
        db,
        current_user.id,
    )


@router.get(
    "/{consultation_id}",
    response_model=ConsultationResponse,
)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    consultation = retrieve_consultation(
        db,
        consultation_id,
        current_user.id,
    )

    if consultation is None:
        raise MediNovaException(
            message="Consultation not found",
            status_code=404,
        )

    return consultation


@router.delete(
    "/{consultation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_consultation(
        db,
        consultation_id,
        current_user.id,
    )

    if not deleted:
        raise MediNovaException(
            message="Consultation not found",
            status_code=404,
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )