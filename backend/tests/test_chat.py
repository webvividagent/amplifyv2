import pytest
from unittest.mock import patch, AsyncMock
from llm.base import LLMResponse


class TestChat:
    @patch("routes.chat.ClaudeProvider")
    def test_chat_creates_session(self, mock_claude, client, test_user):
        mock_provider = AsyncMock()
        mock_provider.generate.return_value = LLMResponse(
            content="Test response",
            tokens_used=100,
            cost=0.01,
            model="claude-3-sonnet",
            finish_reason="stop",
        )
        mock_claude.return_value = mock_provider

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        token = response.json()["access_token"]

        repo_response = client.post(
            "/api/v1/repositories",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "test-repo"},
        )
        repo_id = repo_response.json()["id"]

        response = client.post(
            "/api/v1/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "repository_id": repo_id,
                "agent_type": "coding",
                "message": "Write a function to calculate fibonacci",
            },
        )
        assert response.status_code == 200
        assert "session_id" in response.json()
        assert "message_id" in response.json()
        assert response.json()["content"] == "Test response"

    def test_chat_without_auth(self, client):
        response = client.post(
            "/api/v1/chat",
            json={
                "repository_id": "test-repo",
                "agent_type": "coding",
                "message": "Test message",
            },
        )
        assert response.status_code == 403

    def test_list_sessions(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        token = response.json()["access_token"]

        response = client.get(
            "/api/v1/chat/sessions/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
