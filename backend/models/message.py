#Este archivo define los modelos de datos para los mensajes y envíos masivos (broadcast) en tu backend,
# usando Pydantic para validación y estructura. 
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional, Literal, Any, Dict
from uuid import uuid4

#Define los posibles estados de un mensaje: "queued", "sent", "delivered", "read", "failed".
MessageStatus = Literal["queued", "sent", "delivered", "read", "failed"]

# Modelo para crear un mensaje. Incluye el ID del contacto, texto, URLs de medios y plantilla.
class MessageIn(BaseModel):
    model_config = ConfigDict(extra="ignore") # Ignora campos extra no definidos en el modelo
    contact_id: str = Field(...,min_length= 3,  description="ID del contacto (documento de Firestore)") #campo obligatorio que representa el ID del contacto   
    text: Optional[str] = Field(default=None, description="Contenido de texto") #campo opcional que representa el contenido del mensaje
    media_urls: Optional[List[str]] = Field(default=None, description="URLs de imágenes u otros medios") #campo opcional que representa las URLs de medios asociados al mensaje, para manejo de multimedia
    template_id: Optional[str] = Field(default=None, description="ID de plantilla predefinida (opcional)") # Id que tu generastes en la bd por ejemplo: 501, 503, 1
    #Valida que al menos haya texto o URLs de medios
    @model_validator(mode="before")
    @classmethod
    def _text_or_media(cls, data):
        if not isinstance(data, dict): 
            return data
        if not data.get("text") and not data.get("media_urls"):
            raise ValueError("Debes enviar 'text' o al menos una URL en 'media_urls'.")
        return data
#Esta línea define el modelo de salida (respuesta de la API)
class MessageOut(MessageIn):
    id: str # Id del mensaje documento de firebase
    status: MessageStatus = "queued"# mensaje en cola
    created_at: str #Esta línea define el timestamp de creación en formato ISO (texto).
    # Campos de campaña (opcional)
    campaign_id: Optional[str] = None #base para “mensajes leídos” y analítica.
    coordinator_id: Optional[str] = None #ID del coordinador que generó el mensaje.

#Esta línea declara el modelo para actualizar solo el estado.
class MessageStatusUpdate(BaseModel):
    status: MessageStatus

class MessagePatch(BaseModel):
    text: Optional[str] = None #Esta línea define que puedes mandar texto nuevo o no mandar nada.
    media_urls: Optional[List[str]] = None #define que puedes cambiar la lista de multimedia.
    status: Optional[MessageStatus] = None #permite cambiar el estado si lo envías; si no, se deja como está.
    template_id: Optional[str] = None

# ======= Broadcast =======

#Sirve para seleccionar destinatarios por campos de contacto, filtrados por circuito, congregacion, privilegios
class BroadcastFilters(BaseModel):
    circuito: Optional[str] = None
    congregacion: Optional[str] = None
    privilegio: Optional[str] = None

#modelo de entrada para broadcast. cómo debe verse una petición de envío masivo.
class MessageBroadcastIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    coordinator_id: str = Field(..., description="ID del coordinador que envía") #identifica al emisor “autorizado”.
    #URLs de imágenes/videos masivos
    text: Optional[str] = None
    media_urls: Optional[List[str]] = None
    template_id: Optional[str] = None
    #permite enviar lista explícita de destinatarios. seleccionas a dedo a quiénes envia el mensaje
    recipients: Optional[List[str]] = Field(default=None, description="IDs de contacts seleccionados")
    # filtrado por selección dinámica por circuito/congregación/privilegio.
    filters: Optional[BroadcastFilters] = Field(default=None, description="Filtros para seleccionar recipients")

    #prueba segura antes del envío real.
    dry_run: bool = False
    #cada broadcast puede agruparse bajo una campaña.
    campaign_id: Optional[str] = None  # si no viene, se genera

    @model_validator(mode="before")
    @classmethod
    #aquí viven las reglas de “contenido y destinatarios”
    def _require_targets_and_content(cls, data: Any) -> Any:
        #un broadcast no puede ir vacío
        if not isinstance(data, dict):
            return data
        text = data.get("text")
        media = data.get("media_urls")
        if not text and not media:
            raise ValueError("Debes enviar 'text' o 'media_urls' (al menos uno).")

        #el sistema debe saber a quién enviar. por lista de distinatarios o filtros
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
