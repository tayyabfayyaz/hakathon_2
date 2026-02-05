"""Serializer/deserializer for Kafka messages."""

import json
from typing import Union, Dict, Any
from shared.schemas.events import (
    TodoCreatedEvent, TodoUpdatedEvent, TodoDeletedEvent,
    DeadlineScheduledEvent, DeadlineTriggeredEvent,
    NotificationRequestEvent, NotificationSentEvent, NotificationFailedEvent
)


def serialize_event(event_obj) -> Dict[str, Any]:
    """
    Serialize an event object to a dictionary for Kafka.

    Args:
        event_obj: Event object to serialize

    Returns:
        Serialized event as dictionary
    """
    return event_obj.dict()


def deserialize_event(topic: str, data: Dict[str, Any]):
    """
    Deserialize a Kafka message based on the topic.

    Args:
        topic: Kafka topic name
        data: Raw data from Kafka message

    Returns:
        Deserialized event object
    """
    if topic == "todo.created":
        return TodoCreatedEvent(**data)
    elif topic == "todo.updated":
        return TodoUpdatedEvent(**data)
    elif topic == "todo.deleted":
        return TodoDeletedEvent(**data)
    elif topic == "deadline.scheduled":
        return DeadlineScheduledEvent(**data)
    elif topic == "deadline.triggered":
        return DeadlineTriggeredEvent(**data)
    elif topic == "notification.request":
        return NotificationRequestEvent(**data)
    elif topic == "notification.sent":
        return NotificationSentEvent(**data)
    elif topic == "notification.failed":
        return NotificationFailedEvent(**data)
    else:
        raise ValueError(f"Unknown topic: {topic}")


def encode_message(value: Union[Dict[str, Any], str]) -> bytes:
    """
    Encode a message value for Kafka.

    Args:
        value: Value to encode

    Returns:
        Encoded bytes
    """
    if isinstance(value, dict):
        return json.dumps(value).encode('utf-8')
    elif isinstance(value, str):
        return value.encode('utf-8')
    else:
        return json.dumps(value).encode('utf-8')


def decode_message(data: bytes) -> Union[Dict[str, Any], str]:
    """
    Decode a message value from Kafka.

    Args:
        data: Raw bytes from Kafka

    Returns:
        Decoded value
    """
    decoded_str = data.decode('utf-8')
    try:
        return json.loads(decoded_str)
    except json.JSONDecodeError:
        return decoded_str