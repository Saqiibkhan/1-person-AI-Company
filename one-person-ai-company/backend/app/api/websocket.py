from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.ws_manager import ws_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/projects/{project_id}")
async def project_events_ws(websocket: WebSocket, project_id: int):
    await ws_manager.connect(project_id, websocket)
    try:
        while True:
            # We don't expect incoming messages, but this keeps the
            # connection alive and lets us detect disconnects cleanly.
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(project_id, websocket)
