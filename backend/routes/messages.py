from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from models.message import (
    MessageIn, MessageOut, MessageStatusUpdate, MessagePatch,
    MessageBroadcastIn, MessageBroadcastOut
)
from repository.messages_repository import (
    create_message, list_messages, get_message, update_message, delete_message, bulk_create_messages
)
from repository.contacts_repository import find_contact_ids_by_filters

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("", response_model=MessageOut)
def send_message_endpoint(body: MessageIn):
    saved = create_message(body.model_dump())
    return MessageOut(**saved)

@router.get("", response_model=Dict[str, Any])
def list_messages_endpoint(
    contact_id: str = Query(..., description="ID del contacto"),
    limit: int = Query(50, ge=1, le=200),
    page_token: Optional[str] = Query(None)
):
    items, next_token = list_messages(contact_id=contact_id, limit=limit, page_token=page_token)
    return {"items": [MessageOut(**i) for i in items], "next_page_token": next_token}

@router.get("/{message_id}", response_model=MessageOut)
def get_message_endpoint(message_id: str):
    msg = get_message(message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return MessageOut(**msg)

@router.patch("/{message_id}", response_model=MessageOut)
def patch_message_endpoint(message_id: str, body: MessagePatch):
    updated = update_message(message_id, body.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Message not found or no updates")
    return MessageOut(**updated)

@router.patch("/{message_id}/status", response_model=MessageOut)
def update_status_endpoint(message_id: str, body: MessageStatusUpdate):
    updated = update_message(message_id, {"status": body.status})
    if not updated:
        raise HTTPException(status_code=404, detail="Message not found")
    return MessageOut(**updated)

@router.delete("/{message_id}", status_code=204)
def delete_message_endpoint(message_id: str):
    ok = delete_message(message_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Message not found")
    return

# ======= Broadcast =======

@router.post("/broadcast", response_model=MessageBroadcastOut)
def broadcast_messages(body: MessageBroadcastIn):
    recipients: List[str] = body.recipients or []
    if not recipients and body.filters:
        recipients = find_contact_ids_by_filters(
            circuito=body.filters.circuito,
            congregacion=body.filters.congregacion,
            privilegio=body.filters.privilegio,
            limit=10000
        )

    if body.dry_run:
        return MessageBroadcastOut(
            campaign_id=body.campaign_id or "",
            coordinator_id=body.coordinator_id,
            count=len(recipients),
            message_ids=[]
        )

    if not recipients:
        raise HTTPException(status_code=400, detail="No hay destinatarios para el broadcast (revisa recipients o filters).")

    result = bulk_create_messages(
        contact_ids=recipients,
        base_payload={"text": body.text, "media_urls": body.media_urls, "template_id": body.template_id},
        coordinator_id=body.coordinator_id,
        campaign_id=body.campaign_id
    )
    return MessageBroadcastOut(
        campaign_id=result["campaign_id"],
        coordinator_id=body.coordinator_id,
        count=result["count"],
        message_ids=result["message_ids"]
    )
