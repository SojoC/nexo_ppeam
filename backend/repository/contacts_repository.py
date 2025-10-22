import logging
from typing import Any, Dict, List, Optional, Tuple
from config.firebase import get_collection_ref
from config.settings import get_field_map

logger = logging.getLogger(__name__)

FS_FIELD = get_field_map()  # canónico(minúscula) -> Firestore(actual)

def _to_firestore_doc(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in payload.items():
        if v is None:
            continue
        fs_key = FS_FIELD.get(k)
        if fs_key:
            out[fs_key] = v
    return out

def _from_firestore_doc(doc_dict: Dict[str, Any]) -> Dict[str, Any]:
    inv = {v: k for k, v in FS_FIELD.items()}
    out: Dict[str, Any] = {}
    for fk, fv in (doc_dict or {}).items():
        if fk in inv:
            out[inv[fk]] = fv
    return out

def create_contact(payload: Dict[str, Any]) -> Dict[str, Any]:
    ref = get_collection_ref().document()
    data = _to_firestore_doc(payload)
    ref.set(data)
    result = {"id": ref.id, **_from_firestore_doc(data)}
    logger.info(f"event=create_contact id={ref.id} data={result}")
    return result

def get_contact(contact_id: str) -> Optional[Dict[str, Any]]:
    snap = get_collection_ref().document(contact_id).get()
    if not snap.exists:
        return None
    body = _from_firestore_doc(snap.to_dict() or {})
    result = {"id": snap.id, **body}
    logger.info(f"event=get_contact id={snap.id}")
    return result

def list_contacts(
    limit: int = 50,
    circuito: Optional[str] = None,
    congregacion: Optional[str] = None,
    privilegio: Optional[str] = None,
    order_by_canonical: str = "nombre",
    page_token: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    col = get_collection_ref()
    q = col
    if circuito:
        fs_circuito = FS_FIELD.get("circuito", "Circuito")
        q = q.where(fs_circuito, "==", circuito)
    if congregacion:
        fs_cong = FS_FIELD.get("congregacion", "Congregacion")
        q = q.where(fs_cong, "==", congregacion)
    if privilegio:
        fs_priv = FS_FIELD.get("privilegio", "Privilegio")
        q = q.where(fs_priv, "==", privilegio)

    order_field = FS_FIELD.get(order_by_canonical, FS_FIELD.get("nombre", "Nombre"))
    q = q.order_by(order_field)

    # Paginación por docId (simple y estable con order_by)
    if page_token:
        start_snap = col.document(page_token).get()
        if start_snap.exists:
            q = q.start_after(start_snap)

    docs = list(q.limit(limit).stream())
    items = [{"id": d.id, **_from_firestore_doc(d.to_dict() or {})} for d in docs]
    next_token = docs[-1].id if len(docs) == limit else None
    logger.info(f"event=list_contacts count={len(items)} next_token={next_token}")
    return items, next_token

def find_contact_ids_by_filters(
    circuito: Optional[str] = None,
    congregacion: Optional[str] = None,
    privilegio: Optional[str] = None,
    limit: int = 1000
) -> List[str]:
    col = get_collection_ref()
    q = col
    if circuito:
        q = q.where(FS_FIELD.get("circuito", "Circuito"), "==", circuito)
    if congregacion:
        q = q.where(FS_FIELD.get("congregacion", "Congregacion"), "==", congregacion)
    if privilegio:
        q = q.where(FS_FIELD.get("privilegio", "Privilegio"), "==", privilegio)

    docs = list(q.limit(limit).stream())
    ids = [d.id for d in docs]
    logger.info(f"event=find_contact_ids_by_filters circuito={circuito} congregacion={congregacion} privilegio={privilegio} count={len(ids)}")
    return ids

def update_contact(contact_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ref = get_collection_ref().document(contact_id)
    if not ref.get().exists:
        return None
    data = _to_firestore_doc(payload)
    if data:
        ref.update(data)
    snap = ref.get()
    result = {"id": snap.id, **_from_firestore_doc(snap.to_dict() or {})}
    logger.info(f"event=update_contact id={snap.id} data={result}")
    return result

def delete_contact(contact_id: str) -> bool:
    ref = get_collection_ref().document(contact_id)
    if not ref.get().exists:
        return False
    ref.delete()
    logger.info(f"event=delete_contact id={contact_id}")
    return True
