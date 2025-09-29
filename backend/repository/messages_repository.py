import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
from uuid import uuid4
from backend.config.firebase import get_messages_collection_ref, get_db

logger = logging.getLogger(__name__)

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def create_message(payload: Dict[str, Any]) -> Dict[str, Any]:
    ref = get_messages_collection_ref().document()
    data = {
        "contact_id": payload.get("contact_id"),
        "text": payload.get("text"),
        "media_urls": payload.get("media_urls") or [],
        "template_id": payload.get("template_id"),
        "status": "queued",
        "created_at": _now_iso(),
        "campaign_id": payload.get("campaign_id"),
        "coordinator_id": payload.get("coordinator_id"),
    }
    ref.set(data)
    result = {"id": ref.id, **data}
    logger.info(f"event=create_message id={ref.id} data={result}")
    return result

def get_message(message_id: str) -> Optional[Dict[str, Any]]:
    ref = get_messages_collection_ref().document(message_id)
    snap = ref.get()
    if not snap.exists:
        return None
    result = {"id": snap.id, **(snap.to_dict() or {})}
    logger.info(f"event=get_message id={snap.id}")
    return result

def list_messages(contact_id: str, limit: int = 50, page_token: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    col = get_messages_collection_ref()
    q = col.where("contact_id", "==", contact_id).order_by("created_at")
    if page_token:
        start_snap = col.document(page_token).get()
        if start_snap.exists:
            q = q.start_after(start_snap)
    docs = list(q.limit(limit).stream())
    items = [{"id": d.id, **(d.to_dict() or {})} for d in docs]
    next_token = docs[-1].id if len(docs) == limit else None
    logger.info(f"event=list_messages contact_id={contact_id} count={len(items)} next_token={next_token}")
    return items, next_token

def update_message(message_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ref = get_messages_collection_ref().document(message_id)
    snap = ref.get()
    if not snap.exists:
        return None
    allowed = {"text", "media_urls", "status", "template_id", "campaign_id"}
    update_doc = {k: v for k, v in payload.items() if k in allowed and v is not None}
    if update_doc:
        ref.update(update_doc)
    result = {"id": message_id, **(ref.get().to_dict() or {})}
    logger.info(f"event=update_message id={message_id} fields={list(update_doc.keys())}")
    return result

def delete_message(message_id: str) -> bool:
    ref = get_messages_collection_ref().document(message_id)
    if not ref.get().exists:
        return False
    ref.delete()
    logger.info(f"event=delete_message id={message_id}")
    return True

def bulk_create_messages(
    contact_ids: List[str],
    base_payload: Dict[str, Any],
    coordinator_id: Optional[str] = None,
    campaign_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crea mensajes 'queued' en batch para múltiples contacts.
    base_payload: {text?, media_urls?, template_id?}
    Devuelve: {"campaign_id": str, "count": int, "message_ids": [str]}
    """
    if not campaign_id:
        campaign_id = str(uuid4())

    col = get_messages_collection_ref()
    db = get_db()
    batch = db.batch()

    now = _now_iso()
    message_ids: List[str] = []

    for cid in contact_ids:
        doc_ref = col.document()
        message_ids.append(doc_ref.id)
        data = {
            "contact_id": cid,
            "text": base_payload.get("text"),
            "media_urls": base_payload.get("media_urls") or [],
            "template_id": base_payload.get("template_id"),
            "status": "queued",
            "created_at": now,
            "campaign_id": campaign_id,
            "coordinator_id": coordinator_id,
        }
        batch.set(doc_ref, data)

    batch.commit()
    logger.info(f"event=bulk_create_messages campaign_id={campaign_id} count={len(message_ids)} coordinator_id={coordinator_id}")
    return {"campaign_id": campaign_id, "count": len(message_ids), "message_ids": message_ids}
