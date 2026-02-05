from kafka import KafkaProducer
import json
from typing import Any, Dict
from shared.kafka_config.config import KafkaConfig
import logging

logger = logging.getLogger(__name__)


class KafkaProducerWrapper:
    """Wrapper for Kafka producer with common functionality."""

    def __init__(self, bootstrap_servers: str = None):
        """
        Initialize the Kafka producer wrapper.

        Args:
            bootstrap_servers: Kafka bootstrap servers (optional, defaults to config)
        """
        self.bootstrap_servers = bootstrap_servers or KafkaConfig.BOOTSTRAP_SERVERS
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',  # Strongest consistency guarantee
            retries=3,
            linger_ms=5,  # Small delay to batch messages
        )

    def send_event(self, topic: str, key: str, value: Dict[str, Any]):
        """
        Send an event to a Kafka topic.

        Args:
            topic: Kafka topic name
            key: Message key (used for partitioning)
            value: Message value (will be serialized to JSON)
        """
        try:
            future = self.producer.send(topic, key=key.encode('utf-8'), value=value)
            # Wait for the message to be sent
            record_metadata = future.get(timeout=10)
            logger.info(f"Message sent to topic {record_metadata.topic} "
                       f"partition {record_metadata.partition} "
                       f"offset {record_metadata.offset}")
        except Exception as e:
            logger.error(f"Failed to send message to topic {topic}: {str(e)}")
            raise

    def flush(self):
        """Flush all pending messages."""
        self.producer.flush()

    def close(self):
        """Close the producer."""
        self.producer.close()


# Global producer instance
producer_instance = None


def get_kafka_producer() -> KafkaProducerWrapper:
    """Get a singleton instance of the Kafka producer wrapper."""
    global producer_instance
    if producer_instance is None:
        producer_instance = KafkaProducerWrapper()
    return producer_instance