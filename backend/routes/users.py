# Rutas CRUD de "usuarios" con los campos solicitados.
# Estos usuarios son "registros" con info de perfil (no necesariamente
# los mismos de autenticación). Pueden coexistir con /auth/*.
#
# Campos:
# - nombre (str)
# - edad (int|None)
# - fecha_nacimiento (str ISO o date)  -> guardamos como string ISO
# - sexo (str)
# - estado_civil (str)
# - fecha_bautismo (str ISO)
# - privilegio (str)
# - telefono (str)
# - congregacion (str)
# - ciudad (str)
# - email (str|None)  -> opcional, pero si viene validar único si usamos email como índice aparte
#
# Nota: para simplicidad usamos IDs autogenerados por Firestore en este CRUD.

from typing import Optional, List
import os
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr

router = APIRouter(tags=["users"])

def get_db():
    """
    Inicializa Firebase Admin 1 sola vez y retorna el cliente de Firestore.
    Reutiliza la misma configuración que auth.py
    """
    cred_path = os.environ.get("FIREBASE_CREDENTIALS", "/app/keys/firebase.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(cred_path))
    return firestore.client()

# ===================== MODELOS =====================

class UserIn(BaseModel):
    """Modelo para entrada de datos de usuario (creación/actualización)"""
    nombre: str
    edad: Optional[int] = None
    fecha_nacimiento: Optional[str] = None  # ISO format: "YYYY-MM-DD"
    sexo: Optional[str] = None
    estado_civil: Optional[str] = None
    fecha_bautismo: Optional[str] = None    # ISO format: "YYYY-MM-DD"
    privilegio: Optional[str] = None
    telefono: Optional[str] = None
    congregacion: Optional[str] = None
    ciudad: Optional[str] = None
    email: Optional[EmailStr] = None

class UserOut(UserIn):
    """Modelo para salida de datos (incluye ID de Firestore)"""
    id: str

# ===================== ENDPOINTS CRUD =====================

@router.post("/users", response_model=UserOut)
def create_user(body: UserIn):
    """
    Crear un nuevo usuario en la colección 'users' de Firestore.
    - Valida email único si se proporciona.
    - Genera ID automático.
    - Añade timestamp de creación.
    """
    db = get_db()
    col = db.collection("users")
    
    # Validación de email único (opcional)
    if body.email:
        # Buscar si ya existe otro usuario con ese email
        query = col.where("email", "==", body.email.lower()).limit(1).get()
        if query:
            raise HTTPException(
                status_code=409, 
                detail="Ya existe un usuario con ese email en el sistema."
            )
    
    # Crear documento con ID autogenerado
    doc_ref = col.document()
    
    # Preparar datos para guardar
    user_data = {
        **body.model_dump(),  # todos los campos del modelo
        "email": body.email.lower() if body.email else None,  # normalizar email
        "created_at": firestore.SERVER_TIMESTAMP,  # type: ignore[attr-defined]
        "updated_at": firestore.SERVER_TIMESTAMP  # type: ignore[attr-defined]
    }
    
    # Guardar en Firestore
    doc_ref.set(user_data)
    
    # Retornar usuario creado con su ID
    return UserOut(id=doc_ref.id, **body.model_dump())

@router.get("/users", response_model=List[UserOut])
def list_users(
    limit: int = Query(50, ge=1, le=200, description="Número máximo de usuarios a retornar"),
    congregacion: Optional[str] = Query(None, description="Filtrar por congregación")
):
    """
    Listar usuarios con paginación simple y filtro opcional por congregación.
    - Ordenado por fecha de creación (más recientes primero).
    - Límite configurable (1-200).
    """
    db = get_db()
    
    # Construir query base
    query = db.collection("users")
    
    # Aplicar filtro por congregación si se especifica
    if congregacion:
        query = query.where("congregacion", "==", congregacion)
    
    # Ordenar por fecha de creación y aplicar límite
    query = query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)  # type: ignore[attr-defined]
    
    # Ejecutar query
    docs = query.get()
    
    # Convertir documentos a modelos
    users = []
    for doc in docs:
        data = doc.to_dict() or {}
        # Extraer solo los campos que pertenecen al modelo UserIn
        # Asegurar que 'nombre' (requerido) no sea None para evitar errores de tipo
        user_data = {
            k: (data.get(k) if not (k == "nombre" and data.get(k) is None) else "")
            for k in UserIn.model_fields.keys()
        }
    users.append(UserOut(id=doc.id, **user_data))  # type: ignore[arg-type]
    
    return users

@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: str):
    """
    Obtener un usuario específico por ID.
    - Retorna 404 si no existe.
    """
    db = get_db()
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Extraer datos del documento
    data = doc.to_dict() or {}
    user_data = {k: (data.get(k) if not (k == "nombre" and data.get(k) is None) else "") for k in UserIn.model_fields.keys()}
    
    return UserOut(id=doc.id, **user_data)  # type: ignore[arg-type]

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, body: UserIn):
    """
    Actualizar un usuario existente.
    - Verifica que el usuario existe.
    - Valida email único si se cambia.
    - Actualiza timestamp de modificación.
    """
    db = get_db()
    doc_ref = db.collection("users").document(user_id)
    
    # Verificar que el usuario existe
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Validar email único si se está cambiando
    if body.email:
        # Buscar otros usuarios con el mismo email (excluyendo el actual)
        col = db.collection("users")
        query = col.where("email", "==", body.email.lower()).get()
        for doc in query:
            if doc.id != user_id:  # si hay otro usuario con el mismo email
                raise HTTPException(
                    status_code=409,
                    detail="Ya existe otro usuario con ese email."
                )
    
    # Preparar datos de actualización
    update_data = {
        **body.model_dump(),
        "email": body.email.lower() if body.email else None,
        "updated_at": firestore.SERVER_TIMESTAMP  # type: ignore[attr-defined]
    }
    
    # Actualizar documento
    doc_ref.update(update_data)
    
    # Obtener documento actualizado para retornar
    updated_doc = doc_ref.get()
    data = updated_doc.to_dict() or {}
    user_data = {k: (data.get(k) if not (k == "nombre" and data.get(k) is None) else "") for k in UserIn.model_fields.keys()}
    
    return UserOut(id=user_id, **user_data)  # type: ignore[arg-type]

@router.delete("/users/{user_id}")
def delete_user(user_id: str):
    """
    Eliminar un usuario por ID.
    - Soft delete: podría marcarse como inactivo en lugar de eliminar.
    - Por ahora hace hard delete del documento.
    """
    db = get_db()
    doc_ref = db.collection("users").document(user_id)
    
    # Verificar que existe antes de eliminar
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Eliminar documento
    doc_ref.delete()
    
    return {"status": "ok", "message": f"Usuario {user_id} eliminado correctamente"}

# ===================== ENDPOINTS ADICIONALES =====================

@router.get("/users/by-phone/{phone}")
def get_user_by_phone(phone: str):
    """
    Buscar usuario por número de teléfono.
    Útil para vincular con autenticación SMS.
    """
    db = get_db()
    query = db.collection("users").where("telefono", "==", phone).limit(1).get()
    
    if not query:
        raise HTTPException(status_code=404, detail="No se encontró usuario con ese teléfono")
    
    doc = query[0]
    data = doc.to_dict() or {}
    user_data = {k: (data.get(k) if not (k == "nombre" and data.get(k) is None) else "") for k in UserIn.model_fields.keys()}
    
    return UserOut(id=doc.id, **user_data)  # type: ignore[arg-type]

@router.get("/users/stats/congregaciones")
def get_congregacion_stats():
    """
    Estadísticas básicas: conteo de usuarios por congregación.
    Útil para dashboards administrativos.
    """
    db = get_db()
    users = db.collection("users").get()
    
    # Contar por congregación
    stats = {}
    for doc in users:
        data = doc.to_dict() or {}
        congregacion = data.get("congregacion", "Sin congregación")
        stats[congregacion] = stats.get(congregacion, 0) + 1
    
    return {"congregaciones": stats, "total_usuarios": len(users)}