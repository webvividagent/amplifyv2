import pytest
from uuid import uuid4


class TestRepositories:
    def test_create_repository(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        token = response.json()["access_token"]

        response = client.post(
            "/api/v1/repositories",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "test-repo",
                "git_url": "https://github.com/example/repo",
                "language": "python",
            },
        )
        assert response.status_code == 200
        assert response.json()["name"] == "test-repo"
        assert response.json()["indexed"] is False

    def test_list_repositories(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        token = response.json()["access_token"]

        client.post(
            "/api/v1/repositories",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "repo1"},
        )

        response = client.get(
            "/api/v1/repositories",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "repo1"

    def test_get_repository(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        token = response.json()["access_token"]

        create_response = client.post(
            "/api/v1/repositories",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "test-repo"},
        )
        repo_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/repositories/{repo_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "test-repo"

    def test_repository_not_found(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        token = response.json()["access_token"]

        response = client.get(
            f"/api/v1/repositories/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
