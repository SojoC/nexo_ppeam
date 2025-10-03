# ---------------------------
# WebSocket ConnectionManager
# Opción B (pro): toda mutación de 'active' es atómica (con asyncio.Lock)
# y 'disconnect' es asíncrona (requiere poner 'await' donde la llames).
# ---------------------------

from typing import Dict, Set, Iterable            # Tipos para anotar estructuras (claridad y ayuda del editor)
from fastapi import WebSocket                     # Tipo de socket de FastAPI (con .accept, .send_json, etc.)
import asyncio                                    # Concurrencia async + Lock
import json                                       # (Opcional) Útil si algún día quieres serializar manualmente
from datetime import datetime, timezone           # Para timestamps en UTC con formato ISO-8601


def _iso_now() -> str:
    """Devuelve un timestamp ISO (UTC) como string. Ej: 2025-10-02T12:34:56.789+00:00"""
    return datetime.now(timezone.utc).isoformat()


class ConnectionManager:
    """
    Administra conexiones WebSocket por contact_id.
    Estructura:
      - active: Dict[str, Set[WebSocket]]  (contact_id -> conjunto de sockets/pestañas)
      - _lock: asyncio.Lock para evitar condiciones de carrera al modificar 'active'
    """

    def __init__(self):
        # Mapa en memoria: cada contacto puede tener varias pestañas (varios WebSockets)
        self.active: Dict[str, Set[WebSocket]] = {}
        # Candado asíncrono: asegura operaciones atómicas (agregar/quitar sockets, snapshots, etc.)
        self._lock = asyncio.Lock()

    async def connect(self, contact_id: str, ws: WebSocket):
        """
        Registra una nueva conexión:
          1) Acepta formalmente el WebSocket
          2) Agrega 'ws' al set de sockets de 'contact_id' bajo lock
        """
        await ws.accept()                                    # Paso 1: handshake listo (cliente ya puede enviar/recibir)
        async with self._lock:                               # Paso 2: sección crítica protegida
            self.active.setdefault(contact_id, set()).add(ws)# Crea set si no existe y agrega este socket

    async def disconnect(self, contact_id: str, ws: WebSocket):
        """
        Da de baja una conexión:
          - Remueve 'ws' del set del contact_id
          - Si el set queda vacío, elimina la entrada del dict
        NOTA: es async para usar el mismo lock y ser coherentes con 'connect'
        """
        async with self._lock:                               # Sección crítica protegida
            group = self.active.get(contact_id)              # Obtiene el set actual (si existe)
            if group and ws in group:                        # Solo removemos si realmente está registrado
                group.remove(ws)                             # Quita el socket
                if not group:                                # Si ya no quedan sockets para el contacto...
                    self.active.pop(contact_id, None)        # ...limpiamos la entrada del mapa

    async def send_personal_message(self, contact_id: str, payload: dict) -> int:
        """
        Envía 'payload' a TODAS las pestañas del contacto.
        Devuelve cuántos sockets recibieron OK (útil para logs/métricas).
        """
        async with self._lock:
            # Hacemos un "snapshot" (lista) de los sockets actuales para no mantener el lock durante el envío.
            sockets = list(self.active.get(contact_id, set()))

        ok = 0
        for ws in sockets:
            try:
                await ws.send_json(payload)                  # Envía el dict como JSON (server -> cliente)
                ok += 1                                      # Contador de entregas correctas
            except Exception:
                # Si el socket está roto o el cliente se desconectó, lo limpiamos del registro.
                await self.disconnect(contact_id, ws)        # OJO: ahora es async, hay que 'await'
        return ok

    async def broadcast_to_contacts(self, contact_ids: Iterable[str], payload: dict) -> int:
        """
        Envía el mismo 'payload' a muchos contactos.
        - Acepta cualquier Iterable[str] (lista, set, tupla, generador).
        - Deduplica contact_ids (set(...)) para evitar envíos repetidos.
        Devuelve el total de sockets que recibieron OK.
        """
        ok_total = 0
        for cid in set(contact_ids):                         # set(...) elimina duplicados
            ok_total += await self.send_personal_message(cid, payload)
        return ok_total


# Instancia global para usar en rutas/servicios: from backend.realtime.ws import manager
manager = ConnectionManager()
