"""Unit tests for subscriber microservice."""

import json
import sys
import os
from unittest.mock import patch, MagicMock

import pytest

# Add source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'services', 'subscriber'))

from services.subscriber.app import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_liveness_returns_200(self, client):
        resp = client.get('/health/live')
        assert resp.status_code == 200

    def test_readiness_returns_200(self, client):
        resp = client.get('/health/ready')
        assert resp.status_code == 200

    @patch('services.subscriber.app.check_dapr_sidecar')
    def test_health_returns_status(self, mock_check, client):
        mock_check.return_value = {"name": "dapr_sidecar", "status": "pass", "message": "ok"}
        resp = client.get('/health')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['service'] == 'subscriber-service'
        assert data['status'] == 'healthy'

    @patch('services.subscriber.app.check_dapr_sidecar')
    def test_health_unhealthy_when_sidecar_fails(self, mock_check, client):
        mock_check.return_value = {"name": "dapr_sidecar", "status": "fail", "message": "unreachable"}
        resp = client.get('/health')
        data = json.loads(resp.data)
        assert resp.status_code == 503
        assert data['status'] == 'unhealthy'


class TestSubscriptionDeclaration:
    """Tests for /dapr/subscribe endpoint."""

    def test_subscribe_returns_subscriptions(self, client):
        resp = client.get('/dapr/subscribe')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['pubsubname'] == 'pubsub'
        assert data[0]['topic'] == 'orders'
        assert data[0]['route'] == '/events/orders'


class TestEventHandler:
    """Tests for /events/orders endpoint."""

    @patch('services.subscriber.app.requests.post')
    def test_handle_order_event_success(self, mock_post, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        event = {
            "id": "test-msg-001",
            "source": "publisher-service",
            "type": "order.created",
            "data": {
                "order_id": "ORD-001",
                "amount": 42.0,
                "customer": "test-user"
            }
        }
        resp = client.post('/events/orders',
                           data=json.dumps(event),
                           content_type='application/json')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['status'] == 'SUCCESS'
        assert data['message_id'] == 'test-msg-001'

    @patch('services.subscriber.app.requests.post')
    def test_handle_order_event_state_save_failure(self, mock_post, client):
        mock_post.side_effect = Exception("State store unavailable")

        event = {
            "id": "test-msg-002",
            "source": "publisher-service",
            "type": "order.created",
            "data": {"order_id": "ORD-002"}
        }
        resp = client.post('/events/orders',
                           data=json.dumps(event),
                           content_type='application/json')
        data = json.loads(resp.data)
        assert resp.status_code == 500
        assert data['status'] == 'RETRY'

    @patch('services.subscriber.app.requests.post')
    def test_handle_cloudevent_format(self, mock_post, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        cloudevent = {
            "specversion": "1.0",
            "type": "order.created",
            "source": "publisher-service",
            "id": "ce-msg-001",
            "data": {
                "order_id": "ORD-CE-001",
                "amount": 99.99,
                "customer": "ce-user"
            }
        }
        resp = client.post('/events/orders',
                           data=json.dumps(cloudevent),
                           content_type='application/json')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['status'] == 'SUCCESS'


class TestStateQuery:
    """Tests for /state/<key> endpoint."""

    @patch('services.subscriber.app.requests.get')
    def test_get_state_success(self, mock_get, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"message_id": "test-001", "status": "completed"}'
        mock_resp.json.return_value = {"message_id": "test-001", "status": "completed"}
        mock_get.return_value = mock_resp

        resp = client.get('/state/message%7C%7Ctest-001')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['message_id'] == 'test-001'

    @patch('services.subscriber.app.requests.get')
    def test_get_state_not_found(self, mock_get, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.text = ''
        mock_get.return_value = mock_resp

        resp = client.get('/state/nonexistent-key')
        data = json.loads(resp.data)
        assert resp.status_code == 404
        assert data['code'] == 'NOT_FOUND'

    @patch('services.subscriber.app.requests.get')
    def test_get_state_error(self, mock_get, client):
        mock_get.side_effect = Exception("Connection error")

        resp = client.get('/state/error-key')
        data = json.loads(resp.data)
        assert resp.status_code == 500
        assert data['code'] == 'STATE_ERROR'


class TestServiceInvocation:
    """Tests for /invoke-publisher endpoint."""

    @patch('services.subscriber.app.requests.get')
    def test_invoke_publisher_success(self, mock_get, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"status": "healthy", "service": "publisher-service"}
        mock_get.return_value = mock_resp

        resp = client.get('/invoke-publisher')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['service'] == 'publisher-service'

    @patch('services.subscriber.app.requests.get')
    def test_invoke_publisher_failure(self, mock_get, client):
        mock_get.side_effect = Exception("Service unavailable")

        resp = client.get('/invoke-publisher')
        data = json.loads(resp.data)
        assert resp.status_code == 500
        assert data['code'] == 'INVOKE_ERROR'
