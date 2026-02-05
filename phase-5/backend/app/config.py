"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str

    # Authentication
    better_auth_secret: str

    # Gemini Configuration (Phase-3 AI Chatbot)
    gemini_api_key: str = ""

    # CORS
    cors_origins: str = "http://localhost:3000"

    # API
    api_version: str = "1.0.0"
    debug: bool = False

    # Kafka Configuration
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: str = ""
    kafka_sasl_username: str = ""
    kafka_sasl_password: str = ""

    # Kafka Topics
    kafka_topic_task_events: str = "task-events"
    kafka_topic_task_updates: str = "task-updates"
    kafka_topic_notification_request: str = "notification.request"

    # Kafka Consumer Group IDs
    kafka_consumer_group_audit: str = "audit-service"
    kafka_consumer_group_websocket: str = "websocket-service"
    kafka_consumer_group_notification: str = "notification-service"

    # Feature flags
    kafka_enabled: bool = True

    # SMTP Configuration for email notifications
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_sender_email: str = ""
    smtp_sender_password: str = ""
    smtp_use_tls: bool = True
    email_notifications_enabled: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def kafka_config(self) -> dict:
        """Get Kafka connection configuration."""
        config = {
            "bootstrap_servers": self.kafka_bootstrap_servers,
        }
        if self.kafka_security_protocol != "PLAINTEXT":
            config["security_protocol"] = self.kafka_security_protocol
            config["sasl_mechanism"] = self.kafka_sasl_mechanism
            config["sasl_plain_username"] = self.kafka_sasl_username
            config["sasl_plain_password"] = self.kafka_sasl_password
        return config

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env file


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
