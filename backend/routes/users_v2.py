# Rutas de usuarios refactorizadas usando el UserService
# CRUD endpoints limpios con paginación, filtros y validaciones robustas

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from services.user_service import get_user_service, UserService
from core.security import get_current_user, get_optional_current_user
from core.config import get_settings

# ==================== ROUTER ====================

router = APIRouter(tags=["users"], prefix="/users")

# ==================== MODELOS PYDANTIC ====================

class UserCreateRequest(BaseModel):
    """Modelo para crear usuario"""
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

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Carlos Pérez",
                "edad": 35,
                "fecha_nacimiento": "1988-05-15",
                "sexo": "Masculino",
                "estado_civil": "Casado",
                "fecha_bautismo": "2010-08-20",
                "privilegio": "Siervo Ministerial",
                "telefono": "+58 412 123 4567",
                "congregacion": "Monagas 1",
                "ciudad": "Maturín",
                "email": "juan.perez@example.com"
            }
        }

class UserUpdateRequest(BaseModel):
    """Modelo para actualizar usuario (todos los campos opcionales)"""
    nombre: Optional[str] = None
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

class UserResponse(BaseModel):
    """Respuesta con datos de usuario"""
    id: str
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
    email: Optional[str] = None
    active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class UserListResponse(BaseModel):
    """Respuesta de lista paginada de usuarios"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class UserStatsResponse(BaseModel):
    """Respuesta con estadísticas de usuarios"""
    total_usuarios: int
    congregaciones: dict
    ciudades: dict
    privilegios: dict
    por_sexo: dict

# ==================== ENDPOINTS ====================

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: Optional[str] = Depends(get_optional_current_user)
):
    """
    Crea un nuevo perfil de usuario.
    
    - **nombre**: Nombre completo (obligatorio, mínimo 2 caracteres)
    - **edad**: Edad en años (0-120)
    - **fecha_nacimiento**: Fecha en formato ISO (YYYY-MM-DD)
    - **sexo**: Masculino/Femenino
    - **estado_civil**: Soltero(a)/Casado(a)/Divorciado(a)/Viudo(a)
    - **fecha_bautismo**: Fecha de bautismo en formato ISO
    - **privilegio**: Publicador/Siervo Ministerial/Anciano/etc.
    - **telefono**: Número de teléfono (mínimo 10 dígitos)
    - **congregacion**: Nombre de la congregación
    - **ciudad**: Ciudad de residencia
    - **email**: Dirección de email (opcional, debe ser única)
    
    Returns:
        Perfil de usuario creado con ID asignado
        
    Raises:
        422: Si los datos son inválidos
        409: Si email o teléfono ya existen
    """
    user_data = body.dict(exclude_unset=True)
    
    result = await user_service.create_user(
        user_data=user_data,
        created_by=current_user
    )
    
    return UserResponse(**result)

@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(50, ge=1, le=200, description="Usuarios por página"),
    congregacion: Optional[str] = Query(None, description="Filtrar por congregación"),
    ciudad: Optional[str] = Query(None, description="Filtrar por ciudad"),
    privilegio: Optional[str] = Query(None, description="Filtrar por privilegio"),
    search: Optional[str] = Query(None, description="Buscar en nombre/email"),
    active_only: bool = Query(True, description="Solo usuarios activos"),
    user_service: UserService = Depends(get_user_service)
):
    """
    Lista usuarios con paginación y filtros opcionales.
    
    **Parámetros de paginación:**
    - **page**: Número de página (inicia en 1)
    - **per_page**: Cantidad de usuarios por página (máximo 200)
    
    **Filtros disponibles:**
    - **congregacion**: Filtra por congregación específica
    - **ciudad**: Filtra por ciudad específica
    - **privilegio**: Filtra por privilegio ministerial
    - **search**: Búsqueda por texto en nombre o email
    - **active_only**: Si incluir solo usuarios activos (true por defecto)
    
    Returns:
        Lista paginada con metadatos de paginación
        
    Example:
        GET /users?page=2&per_page=25&congregacion=Monagas%201&active_only=true
    """
    # Calcular offset
    offset = (page - 1) * per_page
    
    users, total_count = await user_service.list_users(
        limit=per_page,
        offset=offset,
        congregacion=congregacion,
        ciudad=ciudad,
        privilegio=privilegio,
        active_only=active_only,
        search=search
    )
    
    # Calcular metadatos de paginación
    total_pages = (total_count + per_page - 1) // per_page
    
    # Convertir usuarios a modelo de respuesta
    user_responses = [UserResponse(**user) for user in users]
    
    return UserListResponse(
        users=user_responses,
        total=total_count,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Obtiene un usuario específico por ID.
    
    - **user_id**: ID único del usuario
    
    Returns:
        Datos completos del usuario
        
    Raises:
        404: Si el usuario no existe
    """
    user_data = await user_service.get_user(user_id)
    
    return UserResponse(**user_data)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    body: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: Optional[str] = Depends(get_optional_current_user)
):
    """
    Actualiza un usuario existente.
    
    - **user_id**: ID del usuario a actualizar
    - Solo se actualizan los campos enviados (patch semántico)
    
    Returns:
        Usuario actualizado
        
    Raises:
        404: Si el usuario no existe
        422: Si los datos son inválidos
        409: Si email o teléfono entran en conflicto
    """
    update_data = body.dict(exclude_unset=True)
    
    # No actualizar si no hay cambios
    if not update_data:
        # Retornar usuario actual sin cambios
        user_data = await user_service.get_user(user_id)
        return UserResponse(**user_data)
    
    result = await user_service.update_user(
        user_id=user_id,
        update_data=update_data,
        updated_by=current_user
    )
    
    return UserResponse(**result)

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    hard_delete: bool = Query(False, description="Eliminación física (irreversible)"),
    user_service: UserService = Depends(get_user_service)
):
    """
    Elimina un usuario (soft delete por defecto).
    
    - **user_id**: ID del usuario a eliminar
    - **hard_delete**: Si true, elimina físicamente (irreversible)
    
    **Soft Delete (por defecto):**
    - Marca el usuario como inactivo
    - Los datos se conservan para auditoría
    - Puede reactivarse posteriormente
    
    **Hard Delete (hard_delete=true):**
    - Elimina completamente el registro
    - Acción irreversible
    - Use con extrema precaución
    
    Returns:
        Confirmación de eliminación
        
    Raises:
        404: Si el usuario no existe
    """
    await user_service.delete_user(
        user_id=user_id,
        soft_delete=not hard_delete
    )
    
    delete_type = "eliminado físicamente" if hard_delete else "desactivado"
    
    return {
        "message": f"Usuario {delete_type} exitosamente",
        "user_id": user_id,
        "type": "hard_delete" if hard_delete else "soft_delete"
    }

# ==================== BÚSQUEDAS ESPECIALIZADAS ====================

@router.get("/by-email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: EmailStr,
    user_service: UserService = Depends(get_user_service)
):
    """
    Busca un usuario por su dirección de email.
    
    - **email**: Dirección de email a buscar
    
    Returns:
        Usuario encontrado
        
    Raises:
        404: Si no se encuentra usuario con ese email
    """
    user_data = await user_service.get_user_by_email(str(email))
    
    if not user_data:
        from core.exceptions import NotFoundError
        raise NotFoundError(f"Usuario con email {email}")
    
    return UserResponse(**user_data)

@router.get("/by-phone/{phone}", response_model=UserResponse)
async def get_user_by_phone(
    phone: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Busca un usuario por su número de teléfono.
    
    - **phone**: Número de teléfono a buscar
    
    Returns:
        Usuario encontrado
        
    Raises:
        404: Si no se encuentra usuario con ese teléfono
    """
    user_data = await user_service.get_user_by_phone(phone)
    
    if not user_data:
        from core.exceptions import NotFoundError
        raise NotFoundError(f"Usuario con teléfono {phone}")
    
    return UserResponse(**user_data)

# ==================== ESTADÍSTICAS ====================

@router.get("/stats/general", response_model=UserStatsResponse)
async def get_user_statistics(
    user_service: UserService = Depends(get_user_service)
):
    """
    Obtiene estadísticas generales de usuarios.
    
    Returns:
        Estadísticas agrupadas por:
        - Total de usuarios activos
        - Distribución por congregaciones
        - Distribución por ciudades
        - Distribución por privilegios ministeriales
        - Distribución por sexo
        
    Útil para dashboards y reportes administrativos.
    """
    stats = await user_service.get_user_stats()
    
    return UserStatsResponse(**stats)

@router.get("/congregaciones/list")
async def list_congregaciones(
    user_service: UserService = Depends(get_user_service)
):
    """
    Lista todas las congregaciones registradas en el sistema.
    
    Returns:
        Lista única de congregaciones con conteo de usuarios
        
    Útil para filtros y formularios.
    """
    stats = await user_service.get_user_stats()
    
    congregaciones = [
        {
            "nombre": cong,
            "usuarios_count": count
        }
        for cong, count in stats["congregaciones"].items()
        if cong != "Sin congregación"
    ]
    
    # Ordenar por nombre
    congregaciones.sort(key=lambda x: x["nombre"])
    
    return {
        "congregaciones": congregaciones,
        "total_congregaciones": len(congregaciones)
    }