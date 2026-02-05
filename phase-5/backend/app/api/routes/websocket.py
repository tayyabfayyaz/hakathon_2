"""WebSocket endpoint for real-time notifications."""

import json
import logging
from typing import Dict, Set

import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manages WebSocket connections per user."""

    def __init__(self):
        # user_id -> set of WebSocket connections
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Accept and register a WebSocket connection for a user."""
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self._connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Remove a WebSocket connection for a user."""
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                del self._connections[user_id]
            logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_to_user(self, user_id: str, message: dict) -> int:
        """Send a message to all connections for a specific user.

        Returns the number of successful sends.
        """
        if user_id not in self._connections:
            logger.debug(f"No WebSocket connections for user {user_id}")
            return 0

        sent_count = 0
        dead_connections = set()

        for websocket in self._connections[user_id]:
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                dead_connections.add(websocket)

        # Clean up dead connections
        for ws in dead_connections:
            self._connections[user_id].discard(ws)

        if not self._connections[user_id]:
            del self._connections[user_id]

        return sent_count

    async def broadcast(self, message: dict) -> int:
        """Broadcast a message to all connected users.

        Returns the total number of successful sends.
        """
        total_sent = 0
        for user_id in list(self._connections.keys()):
            total_sent += await self.send_to_user(user_id, message)
        return total_sent

    def get_connected_users(self) -> list[str]:
        """Get list of all connected user IDs."""
        return list(self._connections.keys())

    def get_connection_count(self, user_id: str) -> int:
        """Get number of connections for a user."""
        return len(self._connections.get(user_id, set()))


# Global connection manager instance
manager = ConnectionManager()


def validate_websocket_token(token: str) -> dict:
    """Validate JWT token and return payload.

    Raises ValueError if token is invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token: missing user ID")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
):
    """
    WebSocket endpoint for real-time notifications.

    Connect with: ws://host/ws/notifications?token=<jwt>

    Messages sent to client:
    - { "type": "new_notification", "payload": <notification_object> }
    - { "type": "notification_read", "payload": { "notification_ids": [...] } }
    - { "type": "all_read", "payload": {} }
    - { "type": "ping", "payload": {} }

    Client can send:
    - { "type": "pong" } - Response to ping
    """
    # Validate token before accepting connection
    try:
        payload = validate_websocket_token(token)
        user_id = payload["sub"]
    except ValueError as e:
        await websocket.close(code=4001, reason=str(e))
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            # Wait for messages from client (for ping/pong or future extensions)
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle client messages
                if message.get("type") == "pong":
                    logger.debug(f"Received pong from user {user_id}")
                elif message.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "payload": {}})

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from user {user_id}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)


# Helper function for other modules to send notifications
async def send_notification_to_user(user_id: str, notification: dict) -> bool:
    """Send a notification to a user via WebSocket.

    Returns True if at least one message was sent successfully.
    """
    message = {
        "type": "new_notification",
        "payload": notification,
    }
    sent_count = await manager.send_to_user(user_id, message)
    return sent_count > 0


async def notify_notifications_read(user_id: str, notification_ids: list) -> bool:
    """Notify user that notifications have been marked as read."""
    message = {
        "type": "notification_read",
        "payload": {"notification_ids": [str(id) for id in notification_ids]},
    }
    sent_count = await manager.send_to_user(user_id, message)
    return sent_count > 0


async def notify_all_read(user_id: str) -> bool:
    """Notify user that all notifications have been marked as read."""
    message = {
        "type": "all_read",
        "payload": {},
    }
    sent_count = await manager.send_to_user(user_id, message)
    return sent_count > 0
