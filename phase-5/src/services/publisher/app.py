"""Publisher microservice for Dapr demo."""

import os
import sys
import uuid
from datetime import datetime, timezone

from flask import Flask, jsonify, request

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.utils import setup_logging, health_response, check_dapr_sidecar, generate_message_id, get_timestamp

app = Flask(__name__)
logger = setup_logging("publisher")

APP_ID = "publisher-service"
APP_VERSION = "1.0.0"
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "pubsub")
TOPIC_NAME = os.getenv("TOPIC_NAME", "orders")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    checks = [check_dapr_sidecar()]
    return health_response("publisher", APP_VERSION, checks)


@app.route("/health/ready", methods=["GET"])
def readiness():
    """Kubernetes readiness probe."""
    return "", 200


@app.route("/health/live", methods=["GET"])
def liveness():
    """Kubernetes liveness probe."""
    return "", 200


@app.route("/publish", methods=["POST"])
def publish():
    """Publish a message to the configured Pub/Sub topic."""
    import requests

    data = request.get_json(silent=True) or {}
    message_id = generate_message_id()
    timestamp = get_timestamp()

    message = {
        "id": message_id,
        "timestamp": timestamp,
        "source": APP_ID,
        "type": "order.created",
        "data": {
            "order_id": data.get("order_id", f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"),
            "amount": data.get("amount", 99.99),
            "customer": data.get("customer", "customer-demo"),
        },
    }

    try:
        dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{TOPIC_NAME}"
        resp = requests.post(dapr_url, json=message, timeout=5)
        resp.raise_for_status()

        logger.info(f"Published message {message_id} to topic {TOPIC_NAME}")
        return jsonify({
            "status": "published",
            "message_id": message_id,
            "topic": TOPIC_NAME,
            "timestamp": timestamp,
        }), 200

    except Exception as e:
        logger.error(f"Failed to publish message: {e}")
        return jsonify({
            "error": "Failed to publish message",
            "code": "PUBSUB_ERROR",
            "details": str(e),
            "timestamp": get_timestamp(),
        }), 500


@app.route("/cron-binding", methods=["POST"])
def cron_trigger():
    """Handle Dapr cron binding trigger."""
    import requests

    message_id = generate_message_id()
    timestamp = get_timestamp()

    message = {
        "id": message_id,
        "timestamp": timestamp,
        "source": APP_ID,
        "type": "order.created",
        "data": {
            "order_id": f"ORD-CRON-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "amount": round(50.0 + (hash(message_id) % 100), 2),
            "customer": "cron-scheduled",
        },
    }

    try:
        dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{TOPIC_NAME}"
        resp = requests.post(dapr_url, json=message, timeout=5)
        resp.raise_for_status()

        logger.info(f"Cron trigger: published message {message_id}")
        return jsonify({
            "status": "published",
            "message_id": message_id,
            "topic": TOPIC_NAME,
            "timestamp": timestamp,
        }), 200

    except Exception as e:
        logger.error(f"Cron trigger failed: {e}")
        return jsonify({
            "error": "Cron trigger failed",
            "code": "CRON_ERROR",
            "details": str(e),
            "timestamp": get_timestamp(),
        }), 500


@app.route("/invoke-subscriber", methods=["GET"])
def invoke_subscriber():
    """Invoke subscriber health via Dapr service invocation."""
    import requests

    try:
        dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/invoke/subscriber-service/method/health"
        resp = requests.get(dapr_url, timeout=5)
        resp.raise_for_status()

        logger.info("Successfully invoked subscriber service")
        return resp.json(), 200

    except Exception as e:
        logger.error(f"Failed to invoke subscriber: {e}")
        return jsonify({
            "error": "Failed to invoke subscriber",
            "code": "INVOKE_ERROR",
            "details": str(e),
            "timestamp": get_timestamp(),
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
