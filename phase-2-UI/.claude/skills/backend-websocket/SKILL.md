---
name: backend-websocket
description: WebSocket implementation for real-time features with connection management and authentication. Use when building real-time notifications, live updates, or bidirectional communication.
argument-hint: "[feature]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# WebSocket Implementation

Build real-time features using FastAPI WebSockets.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Browser   │◀───▶│  FastAPI WS      │◀────│   Kafka     │
│  (Client)   │     │  (Server)        │     │  Consumer   │
└─────────────┘     └──────────────────┘     └─────────────┘
                           │
                    ConnectionManager
                    ├── user_a: [ws1, ws2]
                    └── user_b: [ws3]
```

## Connection Manager

```python
# app/api/routes/websocket.py
import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections per user."""

    def __init__(self):
        # user_id -> set of websocket connections
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Accept and register a new connection."""
        await websocket.accept()

        if user_id not in self._connections:
            self._connections[user_id] = set()

        self._connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected (total: {len(self._connections[user_id])})")

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Remove a connection."""
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)

            if not self._connections[user_id]:
                del self._connections[user_id]

            logger.info(f"User {user_id} disconnected")

    async def send_to_user(self, user_id: str, message: dict) -> None:
        """Send message to all connections for a user."""
        if user_id not in self._connections:
            return

        dead_connections = set()

        for websocket in self._connections[user_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                dead_connections.add(websocket)

        # Clean up dead connections
        for ws in dead_connections:
            self._connections[user_id].discard(ws)

    async def broadcast(self, message: dict) -> None:
        """Send message to all connected users."""
        for user_id in list(self._connections.keys()):
            await self.send_to_user(user_id, message)

    def get_connected_users(self) -> list[str]:
        """Get list of connected user IDs."""
        return list(self._connections.keys())

    def is_connected(self, user_id: str) -> bool:
        """Check if user has any active connections."""
        return user_id in self._connections and len(self._connections[user_id]) > 0


# Global instance
manager = ConnectionManager()
```

## WebSocket Authentication

```python
# app/api/routes/websocket.py
import jwt
from fastapi import WebSocket, WebSocketDisconnect

from app.config import get_settings

settings = get_settings()


async def authenticate_websocket(websocket: WebSocket) -> str | None:
    """
    Authenticate WebSocket connection via query parameter.

    URL format: ws://host/ws/notifications?token=<jwt_token>
    """
    token = websocket.query_params.get("token")

    if not token:
        logger.warning("WebSocket connection without token")
        return None

    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        logger.debug(f"WebSocket authenticated: {user_id}")
        return user_id
    except jwt.ExpiredSignatureError:
        logger.warning("WebSocket token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"WebSocket invalid token: {e}")
        return None
```

## WebSocket Endpoint

```python
# app/api/routes/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json

router = APIRouter()


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications.

    Connection: ws://host/ws/notifications?token=<jwt>

    Messages from server:
    - {"type": "new_notification", "payload": {...}}
    - {"type": "notification_read", "payload": {"notification_ids": [...]}}
    - {"type": "all_read", "payload": {}}
    - {"type": "ping", "payload": {}}

    Messages from client:
    - {"type": "pong"}
    - {"type": "ping"}
    """
    # Authenticate
    user_id = await authenticate_websocket(websocket)

    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    # Connect
    await manager.connect(websocket, user_id)

    try:
        # Start ping task
        ping_task = asyncio.create_task(_ping_loop(websocket))

        # Message handling loop
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=60.0  # 1 minute timeout
                )
                await _handle_message(user_id, data)
            except asyncio.TimeoutError:
                # Send ping on timeout
                await websocket.send_json({"type": "ping", "payload": {}})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ping_task.cancel()
        manager.disconnect(websocket, user_id)


async def _ping_loop(websocket: WebSocket):
    """Send periodic pings to keep connection alive."""
    while True:
        await asyncio.sleep(30)
        try:
            await websocket.send_json({"type": "ping", "payload": {}})
        except Exception:
            break


async def _handle_message(user_id: str, data: dict):
    """Handle incoming WebSocket message."""
    msg_type = data.get("type")

    if msg_type == "pong":
        pass  # Keep-alive response
    elif msg_type == "ping":
        # Client-initiated ping (for testing)
        pass
    else:
        logger.warning(f"Unknown message type: {msg_type}")
```

## Sending Real-Time Updates

```python
# app/services/notification_service.py
from app.api.routes.websocket import manager


async def send_notification_to_user(user_id: str, notification: dict):
    """Send notification via WebSocket if user is connected."""
    if manager.is_connected(user_id):
        await manager.send_to_user(user_id, {
            "type": "new_notification",
            "payload": notification
        })
        return True
    return False


async def notify_task_update(user_id: str, task: dict, action: str):
    """Notify user of task update via WebSocket."""
    await manager.send_to_user(user_id, {
        "type": "task_update",
        "payload": {
            "action": action,
            "task": task
        }
    })
```

## Integration with Routes

```python
# app/api/routes/notifications.py
from app.api.routes.websocket import manager


@router.post("/notifications/mark-read")
async def mark_notifications_read(
    notification_ids: list[UUID],
    current_user: CurrentUserDep,
    session: SessionDep,
):
    # Update database
    for nid in notification_ids:
        notification = await session.get(Notification, nid)
        if notification and notification.user_id == current_user.id:
            notification.status = "read"
            notification.read_at = datetime.now(timezone.utc)

    await session.commit()

    # Notify via WebSocket
    await manager.send_to_user(current_user.id, {
        "type": "notification_read",
        "payload": {"notification_ids": [str(nid) for nid in notification_ids]}
    })

    return {"status": "ok"}
```

## Frontend Client

```typescript
// frontend/src/hooks/use-notification-websocket.ts
import { useEffect, useRef, useCallback } from "react";

export function useNotificationWebSocket(onMessage: (data: any) => void) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    const token = localStorage.getItem("bearer_token");
    if (!token) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/ws/notifications?token=${token}`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log("WebSocket connected");
      reconnectAttempts.current = 0;
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "ping") {
        wsRef.current?.send(JSON.stringify({ type: "pong" }));
        return;
      }

      onMessage(data);
    };

    wsRef.current.onclose = (event) => {
      console.log("WebSocket closed:", event.code);

      if (reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.pow(2, reconnectAttempts.current) * 1000;
        setTimeout(() => {
          reconnectAttempts.current++;
          connect();
        }, delay);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }, [onMessage]);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);
}
```

## Message Types

| Type | Direction | Payload |
|------|-----------|---------|
| `new_notification` | Server → Client | Notification object |
| `notification_read` | Server → Client | `{notification_ids: [...]}` |
| `all_read` | Server → Client | `{}` |
| `task_update` | Server → Client | `{action, task}` |
| `ping` | Server → Client | `{}` |
| `pong` | Client → Server | `{}` |

## Best Practices

1. **Authenticate on connect**: Validate JWT before accepting
2. **Connection cleanup**: Remove dead connections
3. **Ping/pong**: Keep connections alive
4. **Reconnect logic**: Exponential backoff on client
5. **Error handling**: Don't crash on send failures
6. **User isolation**: Send only to authorized connections
