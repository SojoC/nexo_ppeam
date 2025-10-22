import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from firebase_admin import firestore
from config.firebase import get_campaigns_collection_ref, get_db

logger = logging.getLogger(__name__)

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def create_campaign(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea la invitación/campaña con estado 'open' y accepted_count=0
    """
    col = get_campaigns_collection_ref()
    ref = col.document()
    data = {
        "title": payload.get("title"),
        "text": payload.get("text"),
        "media_urls": payload.get("media_urls") or [],
        "capacity": int(payload.get("capacity", 7)),
        "coordinator_id": payload.get("coordinator_id"),
        "created_at": _now_iso(),
        "status": "open",
        "accepted_count": 0,
        # filtros opcionales (para referencia)
        "circuito": payload.get("circuito"),
        "congregacion": payload.get("congregacion"),
        "privilegio": payload.get("privilegio"),
    }
    ref.set(data)
    out = {"id": ref.id, **data}
    logger.info(f"event=create_campaign id={ref.id} capacity={data['capacity']}")
    return out

def get_campaign(campaign_id: str) -> Optional[Dict[str, Any]]:
    snap = get_campaigns_collection_ref().document(campaign_id).get()
    if not snap.exists:
        return None
    return {"id": snap.id, **(snap.to_dict() or {})}

def list_campaigns(limit: int = 50) -> List[Dict[str, Any]]:
    col = get_campaigns_collection_ref()
    q = col.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
    docs = list(q.stream())
    return [{"id": d.id, **(d.to_dict() or {})} for d in docs]

# ---------- RSVP con transacción (capacidad atómica) ----------

def rsvp_campaign(campaign_id: str, contact_id: str, response: str) -> Dict[str, Any]:
    """
    response: 'yes' or 'no'
    - Si 'yes' y hay cupo -> se registra y aumenta accepted_count.
    - Si 'yes' y NO hay cupo -> rechazado (accepted=False).
    - Si 'no' -> solo registra/actualiza RSVP (no cambia cupo).
    NOTA: usamos el doc RSVP con id = contact_id para evitar duplicados.
    """
    db = get_db()
    camp_ref = get_campaigns_collection_ref().document(campaign_id)
    rsvp_ref = camp_ref.collection("rsvps").document(contact_id)

    @firestore.transactional
    def _tx(transaction):
        camp_snap = camp_ref.get(transaction=transaction)
        if not camp_snap.exists:
            raise ValueError("campaign_not_found")

        camp = camp_snap.to_dict() or {}
        status = camp.get("status", "open")
        capacity = int(camp.get("capacity", 7))
        accepted_count = int(camp.get("accepted_count", 0))

        if status != "open":
            # ya cerrada
            return {
                "accepted": False,
                "campaign_id": campaign_id,
                "remaining_slots": max(0, capacity - accepted_count),
                "status": status
            }

        rsvp_snap = rsvp_ref.get(transaction=transaction)
        prev = rsvp_snap.to_dict() if rsvp_snap.exists else None

        if response == "yes":
            # si ya tenía yes, devolvemos OK sin tocar cupo
            if prev and prev.get("response") == "yes":
                return {
                    "accepted": True,
                    "campaign_id": campaign_id,
                    "remaining_slots": max(0, capacity - accepted_count),
                    "status": status
                }

            # si no hay cupo, rechazamos
            if accepted_count >= capacity:
                # cerramos si justo se llenó
                transaction.update(camp_ref, {"status": "closed"})
                return {
                    "accepted": False,
                    "campaign_id": campaign_id,
                    "remaining_slots": 0,
                    "status": "closed"
                }

            # hay cupo -> registramos yes e incrementamos conteo
            transaction.set(rsvp_ref, {
                "contact_id": contact_id,
                "response": "yes",
                "at": datetime.now(timezone.utc).isoformat()
            }, merge=True)
            new_count = accepted_count + 1
            update_doc: Dict[str, Any] = {"accepted_count": new_count}
            if new_count >= capacity:
                update_doc["status"] = "closed"
            transaction.update(camp_ref, update_doc)

            return {
                "accepted": True,
                "campaign_id": campaign_id,
                "remaining_slots": max(0, capacity - new_count),
                "status": update_doc.get("status", "open")
            }

        else:  # response == "no"
            transaction.set(rsvp_ref, {
                "contact_id": contact_id,
                "response": "no",
                "at": datetime.now(timezone.utc).isoformat()
            }, merge=True)
            return {
                "accepted": False,
                "campaign_id": campaign_id,
                "remaining_slots": max(0, capacity - accepted_count),
                "status": status
            }

    transaction = db.transaction()
    result = _tx(transaction)
    logger.info(f"event=rsvp campaign_id={campaign_id} contact_id={contact_id} response={response} accepted={result['accepted']} status={result['status']}")
    return result
