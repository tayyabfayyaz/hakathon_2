"""Subscriber microservice for Dapr demo."""

import os
import sys
from datetime import datetime, timezone

from flask import Flask, jsonify, request

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.utils import setup_logging, health_response, check_dapr_sidecar, get_timestamp

app = Flask(__name__)
logger = setup_logging("subscriber")

APP_ID = "subscriber-service"
APP_VERSION = "1.0.0"
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "pubsub")
STATESTORE_NAME = os.getenv("STATESTORE_NAME", "statestore")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    checks = [check_dapr_sidecar()]
    return health_response("subscriber", APP_VERSION, checks)


@app.route("/health/ready", methods=["GET"])
def readiness():
    """Kubernetes readiness probe."""
    return "", 200


@app.route("/health/live", methods=["GET"])
def liveness():
    """Kubernetes liveness probe."""
    return "", 200


@app.route("/dapr/subscribe", methods=["GET"])
def subscribe():
    """Dapr subscription declaration."""
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "orders",
            "route": "/events/orders",
        }
    ]
    return jsonify(subscriptions)


@app.route("/events/orders", methods=["POST"])
def handle_order_event():
    """Handle incoming Pub/Sub messages from the orders topic."""
    import requests

    event = request.get_json(silent=True) or {}
    logger.info(f"Received event: {event.get('id', 'unknown')}")

    # Extract message data (handle both CloudEvents and raw format)
    message_data = event.get("data", event)
    message_id = event.get("id", message_data.get("id", "unknown"))
    received_at = get_timestamp()

    # Build state entry
    state_key = f"message||{message_id}"
    state_value = {
        "message_id": message_id,
        "received_at": received_at,
        "processed_at": get_timestamp(),
        "status": "completed",
        "original_payload": message_data,
        "result": {
            "success": True,
            "details": "Order processed successfully",
        },
        "retry_count": 0,
        "metadata": {
            "source_topic": "orders",
        },
    }

    # Save state via Dapr
    try:
        dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{STATESTORE_NAME}"
        state_payload = [{"key": state_key, "value": state_value}]
        resp = requests.post(dapr_url, json=state_payload, timeout=5)
        resp.raise_for_status()
        logger.info(f"Saved state for message {message_id}")
    except Exception as e:
        logger.error(f"Failed to save state for message {message_id}: {e}")
        state_value["status"] = "failed"
        state_value["result"] = {"success": False, "details": str(e)}
        return jsonify({"status": "RETRY"}), 500

    return jsonify({
        "status": "SUCCESS",
        "message_id": message_id,
        "processed_at": state_value["processed_at"],
    }), 200


@app.route("/state/<key>", methods=["GET"])
def get_state(key):
    """Query stored state by key."""
    import requests

    try:
        dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{STATESTORE_NAME}/{key}"
        resp = requests.get(dapr_url, timeout=5)

        if resp.status_code == 204 or not resp.text:
            return jsonify({
                "error": "State entry not found",
                "code": "NOT_FOUND",
                "timestamp": get_timestamp(),
            }), 404

        return resp.json(), 200

    except Exception as e:
        logger.error(f"Failed to get state for key {key}: {e}")
        return jsonify({
            "error": "Failed to retrieve state",
            "code": "STATE_ERROR",
            "details": str(e),
            "timestamp": get_timestamp(),
        }), 500


@app.route("/invoke-publisher", methods=["GET"])
def invoke_publisher():
    """Invoke publisher health via Dapr service invocation."""
    import requests

    try:
        dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/invoke/publisher-service/method/health"
        resp = requests.get(dapr_url, timeout=5)
        resp.raise_for_status()

        logger.info("Successfully invoked publisher service")
        return resp.json(), 200

    except Exception as e:
        logger.error(f"Failed to invoke publisher: {e}")
        return jsonify({
            "error": "Failed to invoke publisher",
            "code": "INVOKE_ERROR",
            "details": str(e),
            "timestamp": get_timestamp(),
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
