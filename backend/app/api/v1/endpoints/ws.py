from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import jwt
from app.core.config import settings
from app.services.websocket import socket_manager

router = APIRouter()

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    protocols = websocket.headers.get("sec-websocket-protocol", "")
    token = None
    for p in protocols.split(","):
        p = p.strip()
        if p:
            token = p
            break

    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_user_id = int(payload.get("sub"))
        if token_user_id != user_id:
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return

    await socket_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        socket_manager.disconnect(user_id, websocket)
