from typing import Dict, List
import os


class KafkaConfig:
    """Configuration for Kafka connections"""

    BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    CLIENT_ID = os.getenv("KAFKA_CLIENT_ID", "todo-app")

    # Topic names
    TOPIC_TODO_CREATED = "todo.created"
    TOPIC_TODO_UPDATED = "todo.updated"
    TOPIC_TODO_DELETED = "todo.deleted"
    TOPIC_DEADLINE_SCHEDULED = "deadline.scheduled"
    TOPIC_DEADLINE_TRIGGERED = "deadline.triggered"
    TOPIC_NOTIFICATION_REQUEST = "notification.request"
    TOPIC_NOTIFICATION_SENT = "notification.sent"
    TOPIC_NOTIFICATION_FAILED = "notification.failed"

    # Consumer group IDs
    CONSUMER_GROUP_SCHEDULER = "scheduler-service-group"
    CONSUMER_GROUP_NOTIFICATION = "notification-service-group"

    @classmethod
    def get_all_topics(cls) -> List[str]:
        """Get all Kafka topic names"""
        return [
            cls.TOPIC_TODO_CREATED,
            cls.TOPIC_TODO_UPDATED,
            cls.TOPIC_TODO_DELETED,
            cls.TOPIC_DEADLINE_SCHEDULED,
            cls.TOPIC_DEADLINE_TRIGGERED,
            cls.TOPIC_NOTIFICATION_REQUEST,
            cls.TOPIC_NOTIFICATION_SENT,
            cls.TOPIC_NOTIFICATION_FAILED,
        ]

    @classmethod
    def get_producer_config(cls) -> Dict[str, str]:
        """Get configuration for Kafka producers"""
        return {
            "bootstrap.servers": cls.BOOTSTRAP_SERVERS,
            "client.id": f"{cls.CLIENT_ID}-producer",
            "acks": "all",  # Strongest consistency guarantee
            "retries": 3,
            "batch.num.messages": 100,
            "queue.buffering.max.ms": 5,
        }

    @classmethod
    def get_consumer_config(cls, group_id: str) -> Dict[str, str]:
        """Get configuration for Kafka consumers"""
        return {
            "bootstrap.servers": cls.BOOTSTRAP_SERVERS,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "max.poll.interval.ms": 300000,  # 5 minutes for long-running processing
        }