from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional, Literal, Any, Dict
from uuid import uuid4

MessageStatus = Literal["queued", "sent", "delivered", "read", "failed"]

class MessageIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    contact_id: str = Field(..., description="ID del contacto (documento de Firestore)")
    text: Optional[str] = Field(default=None, description="Contenido de texto")
    media_urls: Optional[List[str]] = Field(default=None, description="URLs de imágenes u otros medios")
    template_id: Optional[str] = Field(default=None, description="ID de plantilla predefinida (opcional)")

class MessageOut(MessageIn):
    id: str
    status: MessageStatus = "queued"
    created_at: str
    # Campos de campaña (opcional)
    campaign_id: Optional[str] = None
    coordinator_id: Optional[str] = None

class MessageStatusUpdate(BaseModel):
    status: MessageStatus

class MessagePatch(BaseModel):
    text: Optional[str] = None
    media_urls: Optional[List[str]] = None
    status: Optional[MessageStatus] = None
    template_id: Optional[str] = None

# ======= Broadcast =======

class BroadcastFilters(BaseModel):
    circuito: Optional[str] = None
    congregacion: Optional[str] = None
    privilegio: Optional[str] = None

class MessageBroadcastIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    coordinator_id: str = Field(..., description="ID del coordinador que envía")
    text: Optional[str] = None
    media_urls: Optional[List[str]] = None
    template_id: Optional[str] = None

    recipients: Optional[List[str]] = Field(default=None, description="IDs de contacts seleccionados")
    filters: Optional[BroadcastFilters] = Field(default=None, description="Filtros para seleccionar recipients")

    dry_run: bool = False
    campaign_id: Optional[str] = None  # si no viene, se genera

    @model_validator(mode="before")
    @classmethod
    def _require_targets_and_content(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        text = data.get("text")
        media = data.get("media_urls")
        if not text and not media:
            raise ValueError("Debes enviar 'text' o 'media_urls' (al menos uno).")

        has_recipients = bool(data.get("recipients"))
        has_filters = bool(data.get("filters"))
        if not (has_recipients or has_filters):
            raise ValueError("Debes proporcionar 'recipients' o 'filters' para seleccionar destinatarios.")

        # campaign_id por defecto
        if not data.get("campaign_id"):
            data["campaign_id"] = str(uuid4())
        return data

class MessageBroadcastOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    campaign_id: str
    coordinator_id: str
    count: int
    message_ids: List[str]
