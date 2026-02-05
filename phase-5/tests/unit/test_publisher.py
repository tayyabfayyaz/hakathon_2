"""Unit tests for publisher microservice."""

import json
import sys
import os
from unittest.mock import patch, MagicMock

import pytest

# Add source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'services', 'publisher'))

from services.publisher.app import app


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

    @patch('services.publisher.app.check_dapr_sidecar')
    def test_health_returns_status(self, mock_check, client):
        mock_check.return_value = {"name": "dapr_sidecar", "status": "pass", "message": "ok"}
        resp = client.get('/health')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['service'] == 'publisher-service'
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

    @patch('services.publisher.app.check_dapr_sidecar')
    def test_health_unhealthy_when_sidecar_fails(self, mock_check, client):
        mock_check.return_value = {"name": "dapr_sidecar", "status": "fail", "message": "unreachable"}
        resp = client.get('/health')
        data = json.loads(resp.data)
        assert resp.status_code == 503
        assert data['status'] == 'unhealthy'


class TestPublishEndpoint:
    """Tests for /publish endpoint."""

    @patch('services.publisher.app.requests.post')
    def test_publish_success(self, mock_post, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        resp = client.post('/publish',
                           data=json.dumps({"order_id": "TEST-001", "amount": 42.0, "customer": "test"}),
                           content_type='application/json')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['status'] == 'published'
        assert 'message_id' in data
        assert data['topic'] == 'orders'

    @patch('services.publisher.app.requests.post')
    def test_publish_without_body(self, mock_post, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        resp = client.post('/publish')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['status'] == 'published'

    @patch('services.publisher.app.requests.post')
    def test_publish_dapr_failure(self, mock_post, client):
        mock_post.side_effect = Exception("Connection refused")

        resp = client.post('/publish',
                           data=json.dumps({"order_id": "FAIL-001"}),
                           content_type='application/json')
        data = json.loads(resp.data)
        assert resp.status_code == 500
        assert data['code'] == 'PUBSUB_ERROR'


class TestCronBinding:
    """Tests for /cron-binding endpoint."""

    @patch('services.publisher.app.requests.post')
    def test_cron_trigger_success(self, mock_post, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        resp = client.post('/cron-binding',
                           data=json.dumps({}),
                           content_type='application/json')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['status'] == 'published'

    @patch('services.publisher.app.requests.post')
    def test_cron_trigger_failure(self, mock_post, client):
        mock_post.side_effect = Exception("Dapr unavailable")

        resp = client.post('/cron-binding')
        data = json.loads(resp.data)
        assert resp.status_code == 500
        assert data['code'] == 'CRON_ERROR'


class TestServiceInvocation:
    """Tests for /invoke-subscriber endpoint."""

    @patch('services.publisher.app.requests.get')
    def test_invoke_subscriber_success(self, mock_get, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"status": "healthy", "service": "subscriber-service"}
        mock_get.return_value = mock_resp

        resp = client.get('/invoke-subscriber')
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data['service'] == 'subscriber-service'

    @patch('services.publisher.app.requests.get')
    def test_invoke_subscriber_failure(self, mock_get, client):
        mock_get.side_effect = Exception("Service unavailable")

        resp = client.get('/invoke-subscriber')
        data = json.loads(resp.data)
        assert resp.status_code == 500
        assert data['code'] == 'INVOKE_ERROR'
