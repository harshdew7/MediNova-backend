from pydantic import BaseModel


class AIConsultRequest(BaseModel):
    message: str


class AIConsultResponse(BaseModel):
    response: str
    risk_level: str
    show_emergency_button: bool
    emergency_number: str | None = None