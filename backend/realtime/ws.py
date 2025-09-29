from typing import Dict, Set
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # contact_id -> set(WebSocket)
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, contact_id: str, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(contact_id, set()).add(ws)

    def disconnect(self, contact_id: str, ws: WebSocket):
        try:
            self.active.get(contact_id, set()).discard(ws)
            if not self.active.get(contact_id):
                self.active.pop(contact_id, None)
        except Exception:
            pass

    async def send_personal_message(self, contact_id: str, payload: dict):
        for ws in list(self.active.get(contact_id, set())):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(contact_id, ws)

    async def broadcast_to_contacts(self, contact_ids, payload: dict):
        for cid in contact_ids:
            await self.send_personal_message(cid, payload)

manager = ConnectionManager()
