from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RecentConsultation(BaseModel):
    id: int
    risk_level: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    total_consultations: int
    high_risk: int
    medium_risk: int
    low_risk: int
    last_consultation: datetime | None
    recent_consultations: list[RecentConsultation]

    model_config = ConfigDict(from_attributes=True)