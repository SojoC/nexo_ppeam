# backend/repository/contacts_repository.py
#CRUD para contactos en Firestorefrom typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional
from backend.config.firebase import get_collection_ref

# Mapa canónico(minúsculas) -> Firestore(actual)
FS_FIELD = {
    "nombre": "Nombre",
    "circuito": "Circuito",
    "telefono": "Telefono",
    "congregacion": "Congregacion",
    "fecha_de_nacimiento": "Fecha_de_nacimiento",
    "fecha_de_bautismo": "Fecha_de_bautismo",
    "privilegio": "Privilegio",
    "direccion_de_habitacion": "Direccion de habitacion",  # con espacio
    "id_externo": "Id",
}

CANONICAL_FIELDS = set(FS_FIELD.keys())

def _to_firestore_doc(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convierte claves canónicas -> claves Firestore actuales y elimina None."""
    out: Dict[str, Any] = {}
    for k, v in payload.items():
        if v is None:
            continue
        if k in FS_FIELD:
            out[FS_FIELD[k]] = v
    return out

def _from_firestore_doc(doc_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Convierte claves Firestore actuales -> canónicas en minúsculas."""
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
    return {"id": ref.id, **_from_firestore_doc(data)}

def get_contact(contact_id: str) -> Optional[Dict[str, Any]]:
    snap = get_collection_ref().document(contact_id).get()
    if not snap.exists:
        return None
    body = _from_firestore_doc(snap.to_dict() or {})
    return {"id": snap.id, **body}

def list_contacts(limit: int = 50, circuito: Optional[str] = None) -> List[Dict[str, Any]]:
    col = get_collection_ref()
    q = col
    if circuito:
        # Firestore tiene "Circuito"
        q = q.where("Circuito", "==", circuito)
    docs = q.limit(limit).stream()
    return [{"id": d.id, **_from_firestore_doc(d.to_dict() or {})} for d in docs]

def update_contact(contact_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ref = get_collection_ref().document(contact_id)
    if not ref.get().exists:
        return None
    data = _to_firestore_doc(payload)
    if data:
        ref.update(data)
    snap = ref.get()
    return {"id": snap.id, **_from_firestore_doc(snap.to_dict() or {})}

def delete_contact(contact_id: str) -> bool:
    ref = get_collection_ref().document(contact_id)
    if not ref.get().exists:
        return False
    ref.delete()
    return True

#prueba del crud
def prueba():
    # Crear un contacto
    nuevo_contacto = {
        "nombre": "Juan Pérez",
        "telefono": "123456789",
        "congregacion": "Congregación Central",
        "fechaNacimiento": "1990-01-01",
        "fechaBautismo": "2020-01-01",
        "privilegio": "Miembro",
        "direccion": "Calle Falsa 123",
        "id_externo": "ext_001"
    }
    creado = create_contact(nuevo_contacto)
    print("Contacto creado:", creado)

    # Listar contactos
    contactos = list_contacts()
    print("Lista de contactos:")
    for c in contactos:
        print(c)

    # Obtener un contacto
    contacto = get_contact(creado["id"])
    print("Contacto obtenido:", contacto)

    # Actualizar un contacto
    actualizado = update_contact(creado["id"], {"telefono": "987654321"})
    print("Contacto actualizado:", actualizado)

  

#prueba()
#python -m backend.repository.contacts_repository