"""
In-memory WebSocket connection registry, keyed by project_id.

Simple and adequate for a single-process MVP (Section 15: "use the
simpler option that reliably provides real-time agent activity").
If the app ever runs multi-process, this would need to move to a
pub/sub backend (e.g. Redis) -- noted here rather than built
prematurely, per Section 29's cost-control principle.
"""
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, list[WebSocket]] = {}

    async def connect(self, project_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(project_id, []).append(websocket)

    def disconnect(self, project_id: int, websocket: WebSocket) -> None:
        conns = self._connections.get(project_id, [])
        if websocket in conns:
            conns.remove(websocket)

    async def broadcast(self, project_id: int, message: dict) -> None:
        for ws in list(self._connections.get(project_id, [])):
            try:
                await ws.send_json(message)
            except Exception:  # noqa: BLE001
                self.disconnect(project_id, ws)


ws_manager = ConnectionManager()
