# Conexión centralizada a Firebase Firestore
# Este módulo maneja toda la conectividad con Firestore de manera singleton

import os
import logging
from typing import Optional, Dict, Any, List
from functools import lru_cache
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client, CollectionReference, DocumentReference

from core.config import get_settings, get_firebase_credentials_path
from core.exceptions import DatabaseError

# ==================== LOGGER ====================

logger = logging.getLogger(__name__)

# ==================== FIREBASE CONNECTION ====================

class FirestoreConnection:
    """
    Clase singleton para manejar la conexión con Firestore.
    
    Provides:
    - Inicialización única de Firebase Admin
    - Métodos helper para operaciones comunes
    - Manejo de errores de conexión
    - Logging de operaciones
    """
    
    _instance: Optional["FirestoreConnection"] = None
    _client: Optional[Client] = None
    
    def __new__(cls) -> "FirestoreConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._initialize_firebase()
    
    def _initialize_firebase(self) -> None:
        """
        Inicializa Firebase Admin SDK una sola vez.
        
        Raises:
            DatabaseError: Si no se puede inicializar Firebase
        """
        try:
            # Evitar múltiples inicializaciones
            if not firebase_admin._apps:
                cred_path = get_firebase_credentials_path()
                logger.info(f"Inicializando Firebase con credenciales: {cred_path}")
                
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                
            self._client = firestore.client()
            logger.info("Conexión a Firestore establecida exitosamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar Firebase: {str(e)}")
            raise DatabaseError(f"No se pudo conectar a Firestore: {str(e)}")
    
    @property
    def client(self) -> Client:
        """
        Obtiene el cliente de Firestore.
        
        Returns:
            Cliente de Firestore inicializado
            
        Raises:
            DatabaseError: Si no se pudo inicializar el cliente
        """
        if self._client is None:
            raise DatabaseError("Cliente de Firestore no inicializado")
        return self._client
    
    def collection(self, name: str) -> CollectionReference:
        """
        Obtiene una referencia a una colección.
        
        Args:
            name: Nombre de la colección
            
        Returns:
            Referencia a la colección
        """
        return self.client.collection(name)
    
    def document(self, collection: str, doc_id: str) -> DocumentReference:
        """
        Obtiene una referencia a un documento específico.
        
        Args:
            collection: Nombre de la colección
            doc_id: ID del documento
            
        Returns:
            Referencia al documento
        """
        return self.client.collection(collection).document(doc_id)

# ==================== FACTORY FUNCTIONS ====================

@lru_cache()
def get_firestore_connection() -> FirestoreConnection:
    """
    Factory function que retorna la instancia singleton de FirestoreConnection.
    
    Returns:
        Instancia de FirestoreConnection
    """
    return FirestoreConnection()

def get_db() -> Client:
    """
    Obtiene el cliente de Firestore.
    
    Esta es la función principal que deben usar otros módulos
    para obtener acceso a la base de datos.
    
    Returns:
        Cliente de Firestore
        
    Usage:
        from core.database import get_db
        
        db = get_db()
        users_ref = db.collection("users")
    """
    return get_firestore_connection().client

# ==================== HELPER FUNCTIONS ====================

def get_collection(name: str) -> CollectionReference:
    """
    Obtiene una referencia a una colección por nombre.
    
    Args:
        name: Nombre de la colección
        
    Returns:
        Referencia a la colección
        
    Usage:
        users_col = get_collection("users")
        docs = users_col.get()
    """
    return get_firestore_connection().collection(name)

def create_document(collection: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> str:
    """
    Crea un documento en una colección.
    
    Args:
        collection: Nombre de la colección
        data: Datos del documento
        doc_id: ID del documento (opcional, se autogenera si no se proporciona)
        
    Returns:
        ID del documento creado
        
    Raises:
        DatabaseError: Si hay error al crear el documento
        
    Usage:
        doc_id = create_document("users", {"name": "Juan", "email": "juan@example.com"})
    """
    try:
        conn = get_firestore_connection()
        
        if doc_id:
            doc_ref = conn.document(collection, doc_id)
            doc_ref.set(data)
            logger.info(f"Documento creado: {collection}/{doc_id}")
            return doc_id
        else:
            col_ref = conn.collection(collection)
            doc_ref = col_ref.add(data)[1]  # add() returns (timestamp, doc_ref)
            logger.info(f"Documento creado: {collection}/{doc_ref.id}")
            return doc_ref.id
            
    except Exception as e:
        logger.error(f"Error creando documento en {collection}: {str(e)}")
        raise DatabaseError(f"No se pudo crear el documento: {str(e)}")

def get_document(collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un documento por su ID.
    
    Args:
        collection: Nombre de la colección
        doc_id: ID del documento
        
    Returns:
        Datos del documento o None si no existe
        
    Usage:
        user_data = get_document("users", "user123")
        if user_data:
            print(f"Usuario: {user_data['name']}")
    """
    try:
        conn = get_firestore_connection()
        doc_ref = conn.document(collection, doc_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
        
    except Exception as e:
        logger.error(f"Error obteniendo documento {collection}/{doc_id}: {str(e)}")
        raise DatabaseError(f"No se pudo obtener el documento: {str(e)}")

def update_document(collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
    """
    Actualiza un documento existente.
    
    Args:
        collection: Nombre de la colección
        doc_id: ID del documento
        data: Datos a actualizar
        
    Returns:
        True si se actualizó correctamente
        
    Raises:
        DatabaseError: Si hay error al actualizar
        
    Usage:
        success = update_document("users", "user123", {"name": "Juan Carlos"})
    """
    try:
        conn = get_firestore_connection()
        doc_ref = conn.document(collection, doc_id)
        
        # Verificar que el documento existe
        if not doc_ref.get().exists:
            raise DatabaseError(f"Documento {doc_id} no existe en {collection}")
            
        doc_ref.update(data)
        logger.info(f"Documento actualizado: {collection}/{doc_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error actualizando documento {collection}/{doc_id}: {str(e)}")
        raise DatabaseError(f"No se pudo actualizar el documento: {str(e)}")

def delete_document(collection: str, doc_id: str) -> bool:
    """
    Elimina un documento.
    
    Args:
        collection: Nombre de la colección
        doc_id: ID del documento
        
    Returns:
        True si se eliminó correctamente
        
    Raises:
        DatabaseError: Si hay error al eliminar
        
    Usage:
        success = delete_document("users", "user123")
    """
    try:
        conn = get_firestore_connection()
        doc_ref = conn.document(collection, doc_id)
        
        # Verificar que el documento existe
        if not doc_ref.get().exists:
            raise DatabaseError(f"Documento {doc_id} no existe en {collection}")
            
        doc_ref.delete()
        logger.info(f"Documento eliminado: {collection}/{doc_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error eliminando documento {collection}/{doc_id}: {str(e)}")
        raise DatabaseError(f"No se pudo eliminar el documento: {str(e)}")

def query_collection(
    collection: str,
    filters: Optional[List[tuple]] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Realiza una consulta en una colección con filtros opcionales.
    
    Args:
        collection: Nombre de la colección
        filters: Lista de filtros (field, operator, value)
        order_by: Campo para ordenar
        limit: Límite de resultados
        
    Returns:
        Lista de documentos que cumplen los criterios
        
    Usage:
        users = query_collection(
            "users",
            filters=[("active", "==", True)],
            order_by="created_at",
            limit=10
        )
    """
    try:
        conn = get_firestore_connection()
        query = conn.collection(collection)
        
        # Aplicar filtros
        if filters:
            for field, operator, value in filters:
                query = query.where(field, operator, value)
        
        # Aplicar ordenamiento
        if order_by:
            query = query.order_by(order_by)
            
        # Aplicar límite
        if limit:
            query = query.limit(limit)
            
        # Ejecutar consulta
        docs = query.get()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id  # Incluir el ID del documento
            results.append(data)
            
        logger.info(f"Consulta ejecutada en {collection}: {len(results)} resultados")
        return results
        
    except Exception as e:
        logger.error(f"Error en consulta {collection}: {str(e)}")
        raise DatabaseError(f"Error en la consulta: {str(e)}")

# ==================== HEALTH CHECK ====================

def check_database_health() -> Dict[str, Any]:
    """
    Verifica el estado de la conexión con Firestore.
    
    Returns:
        Diccionario con información del estado de la base de datos
        
    Usage:
        health = check_database_health()
        if health["connected"]:
            print("Base de datos OK")
    """
    try:
        # Intentar una operación simple
        conn = get_firestore_connection()
        test_ref = conn.collection("_health_check").document("test")
        
        # Escribir y leer un documento de prueba
        test_data = {"timestamp": firestore.SERVER_TIMESTAMP, "status": "healthy"}
        test_ref.set(test_data)
        
        # Verificar que se puede leer
        doc = test_ref.get()
        
        # Limpiar el documento de prueba
        test_ref.delete()
        
        return {
            "connected": True,
            "message": "Firestore connection healthy",
            "timestamp": doc.to_dict().get("timestamp") if doc.exists else None
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "connected": False,
            "message": f"Firestore connection failed: {str(e)}",
            "timestamp": None
        }