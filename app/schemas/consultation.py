from datetime import datetime

from pydantic import BaseModel


class ConsultationResponse(BaseModel):
    id: int
    user_message: str
    ai_response: str
    risk_level: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }