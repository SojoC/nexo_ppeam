# Servicio de usuarios - Lógica de negocio para gestión de usuarios
# Maneja CRUD de perfiles de usuario separado de la autenticación

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from google.cloud import firestore

from core.config import get_settings
from core.database import (
    get_collection, 
    create_document, 
    get_document, 
    update_document, 
    delete_document,
    query_collection
)
from core.exceptions import (
    NotFoundError,
    ConflictError,
    NexoValidationError,
    DatabaseError
)

# ==================== LOGGER ====================

logger = logging.getLogger(__name__)

# ==================== MODELOS DE DATOS ====================

class UserProfile:
    """
    Modelo para perfil de usuario con información personal y ministerial.
    
    Este modelo es independiente de la autenticación y contiene
    información específica del contexto de Nexo_PPEAM.
    """
    
    def __init__(
        self,
        nombre: str,
        edad: Optional[int] = None,
        fecha_nacimiento: Optional[str] = None,
        sexo: Optional[str] = None,
        estado_civil: Optional[str] = None,
        fecha_bautismo: Optional[str] = None,
        privilegio: Optional[str] = None,
        telefono: Optional[str] = None,
        congregacion: Optional[str] = None,
        ciudad: Optional[str] = None,
        email: Optional[str] = None,
        active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None
    ):
        self.nombre = nombre.strip()
        self.edad = edad
        self.fecha_nacimiento = fecha_nacimiento
        self.sexo = sexo
        self.estado_civil = estado_civil
        self.fecha_bautismo = fecha_bautismo
        self.privilegio = privilegio
        self.telefono = telefono
        self.congregacion = congregacion
        self.ciudad = ciudad
        self.email = email.lower().strip() if email else None
        self.active = active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.created_by = created_by
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para Firestore"""
        return {
            "nombre": self.nombre,
            "edad": self.edad,
            "fecha_nacimiento": self.fecha_nacimiento,
            "sexo": self.sexo,
            "estado_civil": self.estado_civil,
            "fecha_bautismo": self.fecha_bautismo,
            "privilegio": self.privilegio,
            "telefono": self.telefono,
            "congregacion": self.congregacion,
            "ciudad": self.ciudad,
            "email": self.email,
            "active": self.active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        """Crea instancia desde diccionario de Firestore"""
        return cls(
            nombre=data.get("nombre", ""),
            edad=data.get("edad"),
            fecha_nacimiento=data.get("fecha_nacimiento"),
            sexo=data.get("sexo"),
            estado_civil=data.get("estado_civil"),
            fecha_bautismo=data.get("fecha_bautismo"),
            privilegio=data.get("privilegio"),
            telefono=data.get("telefono"),
            congregacion=data.get("congregacion"),
            ciudad=data.get("ciudad"),
            email=data.get("email"),
            active=data.get("active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            created_by=data.get("created_by")
        )
    
    def validate(self) -> None:
        """
        Valida los datos del perfil.
        
        Raises:
            NexoValidationError: Si algún campo es inválido
        """
        # Nombre es obligatorio
        if not self.nombre or len(self.nombre.strip()) < 2:
            raise NexoValidationError("El nombre debe tener al menos 2 caracteres")
        
        # Validar edad si se proporciona
        if self.edad is not None and (self.edad < 0 or self.edad > 120):
            raise NexoValidationError("La edad debe estar entre 0 y 120 años")
        
        # Validar email si se proporciona
        if self.email and ("@" not in self.email or len(self.email) < 5):
            raise NexoValidationError("Formato de email inválido")
        
        # Validar teléfono si se proporciona
        if self.telefono:
            phone_clean = self.telefono.replace(" ", "").replace("-", "").replace("+", "")
            if len(phone_clean) < 10:
                raise NexoValidationError("El teléfono debe tener al menos 10 dígitos")

# ==================== SERVICIO DE USUARIOS ====================

class UserService:
    """
    Servicio que maneja toda la lógica de negocio para perfiles de usuario.
    
    Responsibilities:
    - CRUD de perfiles de usuario
    - Validaciones de negocio
    - Búsquedas y filtros
    - Estadísticas y reportes
    - Gestión de duplicados
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.users_collection = get_collection(self.settings.users_collection)
    
    # ==================== CREATE ====================
    
    async def create_user(
        self, 
        user_data: Dict[str, Any],
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo perfil de usuario.
        
        Args:
            user_data: Datos del usuario
            created_by: Usuario que crea el perfil (opcional)
            
        Returns:
            Perfil creado con ID asignado
            
        Raises:
            NexoValidationError: Si los datos son inválidos
            ConflictError: Si hay conflictos con datos existentes
        """
        try:
            # Crear modelo y validar
            user_profile = UserProfile(
                **user_data,
                created_by=created_by
            )
            user_profile.validate()
            
            # Verificar email único si se proporciona
            if user_profile.email:
                await self._check_email_unique(user_profile.email)
            
            # Verificar teléfono único si se proporciona
            if user_profile.telefono:
                await self._check_phone_unique(user_profile.telefono)
            
            # Crear documento con ID autogenerado
            doc_id = create_document(
                self.settings.users_collection,
                user_profile.to_dict()
            )
            
            logger.info(f"Usuario creado: {doc_id} - {user_profile.nombre}")
            
            # Retornar con ID
            result = user_profile.to_dict()
            result["id"] = doc_id
            
            return result
            
        except (NexoValidationError, ConflictError):
            raise
        except Exception as e:
            logger.error(f"Error creando usuario: {str(e)}")
            raise DatabaseError(f"Error al crear usuario: {str(e)}")
    
    # ==================== READ ====================
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Datos del usuario
            
        Raises:
            NotFoundError: Si el usuario no existe
        """
        try:
            user_data = get_document(self.settings.users_collection, user_id)
            if not user_data:
                raise NotFoundError(f"Usuario {user_id}")
            
            # Añadir ID a los datos
            user_data["id"] = user_id
            return user_data
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo usuario {user_id}: {str(e)}")
            raise DatabaseError(f"Error al obtener usuario: {str(e)}")
    
    async def list_users(
        self,
        limit: int = 50,
        offset: int = 0,
        congregacion: Optional[str] = None,
        ciudad: Optional[str] = None,
        privilegio: Optional[str] = None,
        active_only: bool = True,
        search: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Lista usuarios con filtros opcionales.
        
        Args:
            limit: Máximo número de resultados
            offset: Número de resultados a saltar (paginación)
            congregacion: Filtrar por congregación
            ciudad: Filtrar por ciudad
            privilegio: Filtrar por privilegio
            active_only: Solo usuarios activos
            search: Búsqueda por nombre (opcional)
            
        Returns:
            Tupla con (lista_usuarios, total_count)
        """
        try:
            # Construir filtros
            filters = []
            
            if active_only:
                filters.append(("active", "==", True))
            
            if congregacion:
                filters.append(("congregacion", "==", congregacion))
            
            if ciudad:
                filters.append(("ciudad", "==", ciudad))
            
            if privilegio:
                filters.append(("privilegio", "==", privilegio))
            
            # TODO: Implementar búsqueda por texto completo
            # Firestore no soporta búsqueda de texto nativa
            # Para producción considerar Algolia o Elasticsearch
            
            # Obtener resultados
            users = query_collection(
                self.settings.users_collection,
                filters=filters,
                order_by="created_at",
                limit=limit + offset  # Obtener más para simular offset
            )
            
            # Simular offset (no óptimo, mejora requerida para producción)
            if offset > 0:
                users = users[offset:]
            
            # Aplicar límite
            if limit:
                users = users[:limit]
            
            # Filtrar por búsqueda si se especifica
            if search:
                search_lower = search.lower()
                users = [
                    u for u in users 
                    if search_lower in u.get("nombre", "").lower()
                    or search_lower in u.get("email", "").lower()
                ]
            
            # Obtener conteo total (simplificado)
            total_count = len(users)  # En producción usar query separada
            
            logger.info(f"Lista de usuarios: {len(users)} resultados")
            
            return users, total_count
            
        except Exception as e:
            logger.error(f"Error listando usuarios: {str(e)}")
            raise DatabaseError(f"Error al listar usuarios: {str(e)}")
    
    # ==================== UPDATE ====================
    
    async def update_user(
        self,
        user_id: str,
        update_data: Dict[str, Any],
        updated_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Actualiza un usuario existente.
        
        Args:
            user_id: ID del usuario a actualizar
            update_data: Campos a actualizar
            updated_by: Usuario que realiza la actualización
            
        Returns:
            Usuario actualizado
            
        Raises:
            NotFoundError: Si el usuario no existe
            NexoValidationError: Si los datos son inválidos
            ConflictError: Si hay conflictos
        """
        try:
            # Verificar que existe
            current_data = get_document(self.settings.users_collection, user_id)
            if not current_data:
                raise NotFoundError(f"Usuario {user_id}")
            
            # Crear perfil actual
            current_profile = UserProfile.from_dict(current_data)
            
            # Aplicar cambios
            for field, value in update_data.items():
                if hasattr(current_profile, field):
                    setattr(current_profile, field, value)
            
            # Actualizar timestamp
            current_profile.updated_at = datetime.utcnow()
            if updated_by:
                current_profile.created_by = updated_by  # Track last modifier
            
            # Validar datos actualizados
            current_profile.validate()
            
            # Verificar conflictos de email si cambió
            if "email" in update_data and update_data["email"] != current_data.get("email"):
                if current_profile.email:
                    await self._check_email_unique(current_profile.email, exclude_id=user_id)
            
            # Verificar conflictos de teléfono si cambió
            if "telefono" in update_data and update_data["telefono"] != current_data.get("telefono"):
                if current_profile.telefono:
                    await self._check_phone_unique(current_profile.telefono, exclude_id=user_id)
            
            # Actualizar en Firestore
            update_document(
                self.settings.users_collection,
                user_id,
                current_profile.to_dict()
            )
            
            logger.info(f"Usuario actualizado: {user_id} - {current_profile.nombre}")
            
            # Retornar con ID
            result = current_profile.to_dict()
            result["id"] = user_id
            
            return result
            
        except (NotFoundError, NexoValidationError, ConflictError):
            raise
        except Exception as e:
            logger.error(f"Error actualizando usuario {user_id}: {str(e)}")
            raise DatabaseError(f"Error al actualizar usuario: {str(e)}")
    
    # ==================== DELETE ====================
    
    async def delete_user(self, user_id: str, soft_delete: bool = True) -> bool:
        """
        Elimina un usuario (soft delete por defecto).
        
        Args:
            user_id: ID del usuario a eliminar
            soft_delete: Si True, marca como inactivo. Si False, elimina físicamente.
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            NotFoundError: Si el usuario no existe
        """
        try:
            # Verificar que existe
            if not get_document(self.settings.users_collection, user_id):
                raise NotFoundError(f"Usuario {user_id}")
            
            if soft_delete:
                # Soft delete: marcar como inactivo
                update_document(
                    self.settings.users_collection,
                    user_id,
                    {
                        "active": False,
                        "updated_at": datetime.utcnow()
                    }
                )
                logger.info(f"Usuario desactivado: {user_id}")
            else:
                # Hard delete: eliminar físicamente
                delete_document(self.settings.users_collection, user_id)
                logger.info(f"Usuario eliminado físicamente: {user_id}")
            
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error eliminando usuario {user_id}: {str(e)}")
            raise DatabaseError(f"Error al eliminar usuario: {str(e)}")
    
    # ==================== BÚSQUEDAS ESPECIALIZADAS ====================
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Busca un usuario por email.
        
        Args:
            email: Email a buscar
            
        Returns:
            Usuario encontrado o None
        """
        try:
            users = query_collection(
                self.settings.users_collection,
                filters=[("email", "==", email.lower())],
                limit=1
            )
            
            return users[0] if users else None
            
        except Exception as e:
            logger.error(f"Error buscando usuario por email {email}: {str(e)}")
            return None
    
    async def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Busca un usuario por teléfono.
        
        Args:
            phone: Teléfono a buscar
            
        Returns:
            Usuario encontrado o None
        """
        try:
            users = query_collection(
                self.settings.users_collection,
                filters=[("telefono", "==", phone)],
                limit=1
            )
            
            return users[0] if users else None
            
        except Exception as e:
            logger.error(f"Error buscando usuario por teléfono {phone}: {str(e)}")
            return None
    
    # ==================== ESTADÍSTICAS ====================
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de usuarios.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Obtener todos los usuarios activos
            users = query_collection(
                self.settings.users_collection,
                filters=[("active", "==", True)]
            )
            
            # Calcular estadísticas
            stats = {
                "total_usuarios": len(users),
                "congregaciones": {},
                "ciudades": {},
                "privilegios": {},
                "por_sexo": {"Masculino": 0, "Femenino": 0, "No especificado": 0}
            }
            
            for user in users:
                # Por congregación
                cong = user.get("congregacion", "Sin congregación")
                stats["congregaciones"][cong] = stats["congregaciones"].get(cong, 0) + 1
                
                # Por ciudad
                ciudad = user.get("ciudad", "Sin ciudad")
                stats["ciudades"][ciudad] = stats["ciudades"].get(ciudad, 0) + 1
                
                # Por privilegio
                priv = user.get("privilegio", "Sin privilegio")
                stats["privilegios"][priv] = stats["privilegios"].get(priv, 0) + 1
                
                # Por sexo
                sexo = user.get("sexo", "No especificado")
                if sexo in ["M", "Masculino"]:
                    stats["por_sexo"]["Masculino"] += 1
                elif sexo in ["F", "Femenino"]:
                    stats["por_sexo"]["Femenino"] += 1
                else:
                    stats["por_sexo"]["No especificado"] += 1
            
            logger.info(f"Estadísticas calculadas: {stats['total_usuarios']} usuarios")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas: {str(e)}")
            raise DatabaseError(f"Error al calcular estadísticas: {str(e)}")
    
    # ==================== UTILIDADES PRIVADAS ====================
    
    async def _check_email_unique(self, email: str, exclude_id: Optional[str] = None) -> None:
        """
        Verifica que un email sea único.
        
        Args:
            email: Email a verificar
            exclude_id: ID a excluir de la verificación (para updates)
            
        Raises:
            ConflictError: Si el email ya existe
        """
        existing_user = await self.get_user_by_email(email)
        if existing_user and existing_user.get("id") != exclude_id:
            raise ConflictError(f"El email {email} ya está en uso")
    
    async def _check_phone_unique(self, phone: str, exclude_id: Optional[str] = None) -> None:
        """
        Verifica que un teléfono sea único.
        
        Args:
            phone: Teléfono a verificar
            exclude_id: ID a excluir de la verificación (para updates)
            
        Raises:
            ConflictError: Si el teléfono ya existe
        """
        existing_user = await self.get_user_by_phone(phone)
        if existing_user and existing_user.get("id") != exclude_id:
            raise ConflictError(f"El teléfono {phone} ya está en uso")

# ==================== SINGLETON ====================

_user_service: Optional[UserService] = None

def get_user_service() -> UserService:
    """
    Factory function que retorna instancia singleton del UserService.
    
    Returns:
        Instancia de UserService
        
    Usage:
        from services.user_service import get_user_service
        
        user_service = get_user_service()
        result = await user_service.create_user(user_data)
    """
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service