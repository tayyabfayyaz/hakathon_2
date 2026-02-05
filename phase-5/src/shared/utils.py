"""Shared utilities for Dapr microservices."""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

from flask import jsonify


def setup_logging(service_name: str) -> logging.Logger:
    """Configure structured JSON logging for a service."""
    logger = logging.getLogger(service_name)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(service_name))
    logger.addHandler(handler)

    return logger


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "dapr_app_id": f"{self.service_name}-service",
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def generate_message_id() -> str:
    """Generate a UUID v4 message identifier."""
    return str(uuid4())


def get_timestamp() -> str:
    """Get current ISO 8601 timestamp."""
    return datetime.now(timezone.utc).isoformat()


def health_response(service_name: str, version: str = "1.0.0", checks: list = None):
    """Build a standardized health check response."""
    status = "healthy"
    if checks:
        statuses = [c.get("status") for c in checks]
        if "fail" in statuses:
            status = "unhealthy"
        elif "warn" in statuses:
            status = "degraded"

    response = {
        "status": status,
        "service": f"{service_name}-service",
        "version": version,
        "timestamp": get_timestamp(),
    }
    if checks:
        response["checks"] = checks

    status_code = 200 if status != "unhealthy" else 503
    return jsonify(response), status_code


def check_dapr_sidecar() -> dict:
    """Check if the Dapr sidecar is reachable."""
    import requests

    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
    try:
        resp = requests.get(
            f"http://localhost:{dapr_port}/v1.0/healthz", timeout=2
        )
        if resp.status_code == 204 or resp.status_code == 200:
            return {"name": "dapr_sidecar", "status": "pass", "message": "Dapr sidecar is healthy"}
    except Exception as e:
        return {"name": "dapr_sidecar", "status": "fail", "message": str(e)}
    return {"name": "dapr_sidecar", "status": "fail", "message": f"HTTP {resp.status_code}"}
