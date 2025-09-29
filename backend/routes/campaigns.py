from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel  # <-- IMPORT NECESARIO
from typing import Dict, Any, Optional, List

from backend.models.campaign import (
    CampaignIn, CampaignOut, CampaignListOut, RSVPIn, RSVPOut
)
from backend.repository.campaigns_repository import (
    create_campaign, get_campaign, list_campaigns, rsvp_campaign
)
from backend.repository.messages_repository import bulk_create_messages
from backend.repository.contacts_repository import (
    find_contact_ids_by_filters, get_contact
)
from backend.realtime.ws import manager  # para avisar en tiempo real

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# --- helper: asegurar que quien envía es coordinador ---
def _ensure_coordinator(coordinator_id: str):
    c = get_contact(coordinator_id)
    if not c or not c.get("es_coordinador"):
        raise HTTPException(
            status_code=403,
            detail="coordinator_id no autorizado: marque es_coordinador=true en ese contacto"
        )

@router.post("", response_model=CampaignOut)
def create_campaign_endpoint(body: CampaignIn):
    _ensure_coordinator(body.coordinator_id)
    created = create_campaign(body.model_dump())
    return CampaignOut(**created)

@router.get("", response_model=CampaignListOut)
def list_campaigns_endpoint(limit: int = Query(50, ge=1, le=200)):
    items = [CampaignOut(**c) for c in list_campaigns(limit)]
    return {"items": items}

@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign_endpoint(campaign_id: str):
    it = get_campaign(campaign_id)
    if not it:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignOut(**it)

# ----- Envío masivo ligado a campaña -----

class BroadcastBody(BaseModel):
    coordinator_id: str
    text: Optional[str] = None
    media_urls: Optional[List[str]] = None
    template_id: Optional[str] = None
    recipients: Optional[List[str]] = None
    circuito: Optional[str] = None
    congregacion: Optional[str] = None
    privilegio: Optional[str] = None
    dry_run: bool = False

class BroadcastOut(BaseModel):
    campaign_id: str
    count: int
    message_ids: List[str]

@router.post("/{campaign_id}/broadcast", response_model=BroadcastOut)
async def broadcast_for_campaign(campaign_id: str, body: BroadcastBody):
    _ensure_coordinator(body.coordinator_id)

    camp = get_campaign(campaign_id)
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found")

    recipients = body.recipients or []
    if not recipients:
        recipients = find_contact_ids_by_filters(
            circuito=body.circuito,
            congregacion=body.congregacion,
            privilegio=body.privilegio,
            limit=10000
        )

    if body.dry_run:
        return BroadcastOut(campaign_id=campaign_id, count=len(recipients), message_ids=[])

    if not recipients:
        raise HTTPException(status_code=400, detail="No hay destinatarios (revisa filters o recipients).")

    result = bulk_create_messages(
        contact_ids=recipients,
        base_payload={
            "text": body.text or camp.get("text"),
            "media_urls": body.media_urls or camp.get("media_urls"),
            "template_id": body.template_id
        },
        coordinator_id=body.coordinator_id,
        campaign_id=campaign_id
    )

    # Notificación en tiempo real a todos los destinatarios conectados
    await manager.broadcast_to_contacts(
        recipients,
        {"type": "campaign_broadcast", "data": {"campaign_id": campaign_id}}
    )

    return BroadcastOut(
        campaign_id=result["campaign_id"],
        count=result["count"],
        message_ids=result["message_ids"]
    )

# ----- RSVP (sí/no con cupo) -----

@router.post("/{campaign_id}/rsvp", response_model=RSVPOut)
async def rsvp_endpoint(campaign_id: str, body: RSVPIn):
    res = rsvp_campaign(campaign_id, body.contact_id, body.response)
    # Notifica a quien respondió
    await manager.send_personal_message(
        body.contact_id,
        {"type": "rsvp_result", "data": {"campaign_id": campaign_id, **res}}
    )
    # Notifica al coordinador
    if (camp := get_campaign(campaign_id)):
        coord_id = camp.get("coordinator_id")
        if coord_id:
            await manager.send_personal_message(
                coord_id,
                {"type": "rsvp_update", "data": {"campaign_id": campaign_id, "contact_id": body.contact_id, **res}}
            )
    return RSVPOut(**res)
