# Versión temporal de users.py sin Firebase para testing
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime

router = APIRouter(tags=["users"])

# Base de datos temporal en memoria
temp_users_db = {}

class UserIn(BaseModel):
    nombre: str
    edad: Optional[int] = None
    fecha_nacimiento: Optional[str] = None
    sexo: Optional[str] = None
    estado_civil: Optional[str] = None
    fecha_bautismo: Optional[str] = None
    privilegio: Optional[str] = None
    telefono: Optional[str] = None
    congregacion: Optional[str] = None
    ciudad: Optional[str] = None
    email: Optional[EmailStr] = None

class UserOut(UserIn):
    id: str

@router.post("/users", response_model=UserOut)
def create_user(body: UserIn):
    """Crear usuario temporal en memoria"""
    user_id = str(uuid.uuid4())
    
    # Validar email único si se proporciona
    if body.email:
        for existing_user in temp_users_db.values():
            if existing_user.get("email", "").lower() == body.email.lower():
                raise HTTPException(status_code=409, detail="Ya existe un usuario con ese email.")
    
    user_data = {
        **body.model_dump(),
        "id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    temp_users_db[user_id] = user_data
    
    return UserOut(id=user_id, **body.model_dump())

@router.get("/users", response_model=List[UserOut])
def list_users(
    limit: int = Query(50, ge=1, le=200),
    congregacion: Optional[str] = Query(None)
):
    """Listar usuarios temporales"""
    users = list(temp_users_db.values())
    
    # Filtrar por congregación si se especifica
    if congregacion:
        users = [u for u in users if u.get("congregacion") == congregacion]
    
    # Aplicar límite
    users = users[:limit]
    
    # Convertir a modelo de salida
    result = []
    for user_data in users:
        user_out_data = {k: user_data.get(k) for k in UserIn.model_fields.keys()}
        result.append(UserOut(id=user_data["id"], **user_out_data))
    
    return result

@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: str):
    """Obtener usuario temporal por ID"""
    user_data = temp_users_db.get(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user_out_data = {k: user_data.get(k) for k in UserIn.model_fields.keys()}
    return UserOut(id=user_id, **user_out_data)

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, body: UserIn):
    """Actualizar usuario temporal"""
    if user_id not in temp_users_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Validar email único si se cambia
    if body.email:
        for existing_id, existing_user in temp_users_db.items():
            if existing_id != user_id and existing_user.get("email", "").lower() == body.email.lower():
                raise HTTPException(status_code=409, detail="Ya existe otro usuario con ese email.")
    
    # Actualizar datos
    temp_users_db[user_id].update({
        **body.model_dump(),
        "updated_at": datetime.utcnow()
    })
    
    user_out_data = {k: temp_users_db[user_id].get(k) for k in UserIn.model_fields.keys()}
    return UserOut(id=user_id, **user_out_data)

@router.delete("/users/{user_id}")
def delete_user(user_id: str):
    """Eliminar usuario temporal"""
    if user_id not in temp_users_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    del temp_users_db[user_id]
    return {"status": "ok", "message": f"Usuario {user_id} eliminado correctamente"}