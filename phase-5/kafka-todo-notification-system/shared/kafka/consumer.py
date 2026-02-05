from kafka import KafkaConsumer
import json
from typing import List, Callable, Any
from shared.kafka_config.config import KafkaConfig
import logging

logger = logging.getLogger(__name__)


class KafkaConsumerWrapper:
    """Wrapper for Kafka consumer with common functionality."""

    def __init__(self, bootstrap_servers: str = None, group_id: str = "default-group"):
        """
        Initialize the Kafka consumer wrapper.

        Args:
            bootstrap_servers: Kafka bootstrap servers (optional, defaults to config)
            group_id: Consumer group ID
        """
        self.bootstrap_servers = bootstrap_servers or KafkaConfig.BOOTSTRAP_SERVERS
        self.group_id = group_id
        self.consumer = None

    def subscribe(self, topics: List[str]):
        """
        Subscribe to Kafka topics.

        Args:
            topics: List of topic names to subscribe to
        """
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            max_poll_interval_ms=300000,  # 5 minutes for long-running processing
        )
        logger.info(f"Subscribed to topics: {topics}")

    def consume_messages(self, callback: Callable[[str, dict], None], timeout_ms: int = 1000):
        """
        Consume messages from subscribed topics.

        Args:
            callback: Function to call with topic and message value
            timeout_ms: Timeout in milliseconds for poll operation
        """
        if not self.consumer:
            raise ValueError("Consumer not initialized. Call subscribe() first.")

        for message in self.consumer:
            try:
                topic = message.topic
                value = message.value

                # Process the message
                callback(topic, value)

                # Commit the offset after successful processing
                self.consumer.commit()

                logger.debug(f"Processed message from topic {topic}")
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                # Depending on requirements, you might want to commit the offset anyway
                # or handle the error differently

    def close(self):
        """Close the consumer."""
        if self.consumer:
            self.consumer.close()