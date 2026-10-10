"""
Writes Event rows (Section 20/23) and broadcasts them over WebSocket.

This is the ONLY place that creates Event rows, and every meaningful
state change in the system goes through it -- which is what makes the
"no faked activity" rule enforceable: the UI can only ever show what
passed through here.
"""
from sqlalchemy.orm import Session

from app.models.event import Event
from app.services.ws_manager import ws_manager


async def emit(
    db: Session,
    project_id: int,
    event_type: str,
    message: str,
    task_id: int | None = None,
    metadata: dict | None = None,
) -> Event:
    event = Event(
        project_id=project_id,
        task_id=task_id,
        event_type=event_type,
        message=message,
        event_metadata=metadata or {},
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    await ws_manager.broadcast(
        project_id,
        {
            "id": event.id,
            "project_id": project_id,
            "task_id": task_id,
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {},
            "created_at": event.created_at.isoformat(),
        },
    )
    return event
