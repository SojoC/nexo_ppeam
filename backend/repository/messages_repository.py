import logging                                        # Logging estructurado (auditoría/depuración)
from typing import Any, Dict, List, Optional, Tuple   # Tipos para anotar entradas/salidas
from datetime import datetime, timezone               # Timestamps en UTC (ISO)
from uuid import uuid4                                # Para generar campaign_id si no viene
from config.firebase import get_messages_collection_ref, get_db
# ^ get_messages_collection_ref(): atajo a la colección 'messages'
# ^ get_db(): devuelve el cliente Firestore (para batch/transactions)

logger = logging.getLogger(__name__)                  # Logger del módulo (nombre = ruta del archivo)

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()     # Fecha/hora actual en ISO-8601 (UTC)

def create_message(payload: Dict[str, Any]) -> Dict[str, Any]:
    ref = get_messages_collection_ref().document()    # Crea referencia a doc con ID nuevo (aún no escribe)
    data = {
        "contact_id": payload.get("contact_id"),      # ID del contacto destino
        "text": payload.get("text"),                  # Texto (opcional)
        "media_urls": payload.get("media_urls") or [],# Lista de URLs (si viene None, usa lista vacía)
        "template_id": payload.get("template_id"),    # Plantilla predefinida (opcional)
        "status": "queued",                           # Estado inicial
        "created_at": _now_iso(),                     # Timestamp ISO (string)
        "campaign_id": payload.get("campaign_id"),    # Campaña (si aplica)
        "coordinator_id": payload.get("coordinator_id"), # Quien envía (si aplica)
    }
    ref.set(data)                                     # Persiste el documento en Firestore
    result = {"id": ref.id, **data}                   # Agrega el ID (como clave 'id') en el dict de salida
    logger.info(f"event=create_message id={ref.id} data={result}")  # Log de auditoría
    return result                                     # Devuelve el mensaje creado (para response)

def get_message(message_id: str) -> Optional[Dict[str, Any]]:
    ref = get_messages_collection_ref().document(message_id)  # Ref a /messages/{message_id}
    snap = ref.get()                                          # Lee snapshot del doc
    if not snap.exists:                                       # Si no existe, None
        return None
    result = {"id": snap.id, **(snap.to_dict() or {})}        # Convierte a dict y coloca 'id'
    logger.info(f"event=get_message id={snap.id}")            # Log
    return result

def list_messages(contact_id: str, limit: int = 50, page_token: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    col = get_messages_collection_ref()                       # Atajo a la colección
    q = col.where("contact_id", "==", contact_id).order_by("created_at")
    # ^ Filtro por contact_id y orden por created_at (ascendente)
    if page_token:
        start_snap = col.document(page_token).get()           # Obtiene snapshot del último doc de la página anterior
        if start_snap.exists:
            q = q.start_after(start_snap)                     # Empieza después de ese snapshot (paginación)
    docs = list(q.limit(limit).stream())                      # Ejecuta query (limit) y materializa la lista
    items = [{"id": d.id, **(d.to_dict() or {})} for d in docs]   # Convierte snapshots a dict con 'id'
    next_token = docs[-1].id if len(docs) == limit else None  # Si llenaste la página, da cursor para la siguiente
    logger.info(f"event=list_messages contact_id={contact_id} count={len(items)} next_token={next_token}")
    return items, next_token                                  # Devuelve resultados + próximo cursor (o None)

def update_message(message_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ref = get_messages_collection_ref().document(message_id)  # Ref al doc
    snap = ref.get()                                          # Lee estado actual
    if not snap.exists:
        return None
    allowed = {"text", "media_urls", "status", "template_id", "campaign_id"}  # Campos permitidos para update
    update_doc = {k: v for k, v in payload.items() if k in allowed and v is not None}
    # ^ Construye solo los cambios presentes y no-None
    if update_doc:
        ref.update(update_doc)                                # Aplica patch en Firestore (merge de campos)
    result = {"id": message_id, **(ref.get().to_dict() or {})}# Vuelve a leer para retornar estado actualizado
    logger.info(f"event=update_message id={message_id} fields={list(update_doc.keys())}")  # Log de campos cambiados
    return result

def delete_message(message_id: str) -> bool:
    ref = get_messages_collection_ref().document(message_id)  # Ref al doc
    if not ref.get().exists:                                  # Si no existe, False
        return False
    ref.delete()                                              # Borra
    logger.info(f"event=delete_message id={message_id}")      # Log
    return True                                               # Ok, se borró

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
        campaign_id = str(uuid4())                            # Si no viene campaña, genera una nueva

    col = get_messages_collection_ref()                       # Colección messages
    db = get_db()                                             # Cliente Firestore (necesario para batch)
    batch = db.batch()                                        # Crea batch (escrituras en lote)

    now = _now_iso()                                          # Timestamp común para todos los docs del lote
    message_ids: List[str] = []                               # Acumula IDs nuevos

    for cid in contact_ids:                                   # Recorre cada contacto destino
        doc_ref = col.document()                              # ID nuevo por cada mensaje
        message_ids.append(doc_ref.id)                        # Guarda el ID para el resumen
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
        batch.set(doc_ref, data)                              # Agrega la operación al batch (no escribe aún)

    batch.commit()                                            # Ejecuta TODAS las escrituras del lote
    logger.info(f"event=bulk_create_messages campaign_id={campaign_id} count={len(message_ids)} coordinator_id={coordinator_id}")
    return {"campaign_id": campaign_id, "count": len(message_ids), "message_ids": message_ids}
