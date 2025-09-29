from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Literal, Any
from datetime import datetime, timezone
from uuid import uuid4

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class CampaignStatus(str):
    OPEN = "open"
    CLOSED = "closed"

class CampaignIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str = Field(..., min_length=1, max_length=140)
    text: Optional[str] = None
    media_urls: Optional[List[str]] = None
    capacity: int = Field(7, ge=1, le=1000)
    coordinator_id: str = Field(..., min_length=1)
    # opcional: para atajos (podrías no usarlos aquí y delegar al broadcast)
    circuito: Optional[str] = None
    congregacion: Optional[str] = None
    privilegio: Optional[str] = None

class CampaignOut(BaseModel):
    id: str
    title: str
    text: Optional[str] = None
    media_urls: Optional[List[str]] = None
    capacity: int
    coordinator_id: str
    created_at: str
    status: str = CampaignStatus.OPEN
    accepted_count: int = 0

class CampaignListOut(BaseModel):
    items: List[CampaignOut]

# RSVP
Affirm = Literal["yes", "no"]

class RSVPIn(BaseModel):
    contact_id: str
    response: str  # admite "yes"/"no", y también "👍" / "👎" / "si" / "sí"

    @model_validator(mode="before")
    @classmethod
    def _normalize(cls, data: Any) -> Any:
        if isinstance(data, dict):
            r = str(data.get("response", "")).strip().lower()
            if r in ("yes", "si", "sí", "👍", "ok"):
                data["response"] = "yes"
            elif r in ("no", "👎"):
                data["response"] = "no"
        return data

class RSVPOut(BaseModel):
    accepted: bool
    campaign_id: str
    remaining_slots: int
    status: str  # open/closed
