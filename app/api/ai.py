from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.service import AIService
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.ai import (
    AIConsultRequest,
    AIConsultResponse,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)

service = AIService()


@router.post(
    "/consult",
    response_model=AIConsultResponse,
)
def consult(
    request: AIConsultRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.consult(
        db=db,
        user=current_user,
        message=request.message,
    )