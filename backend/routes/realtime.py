from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from realtime.ws import manager

router = APIRouter(tags=["realtime"])

@router.websocket("/ws/{contact_id}")
async def ws_contact(websocket: WebSocket, contact_id: str):
    await manager.connect(contact_id, websocket)
    try:
        while True:
            # Si el cliente envía algo (p.ej. ACK/lectura), lo recibimos aquí
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
         await manager.disconnect(contact_id, websocket)
