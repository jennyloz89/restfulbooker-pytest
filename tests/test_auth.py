import pytest
import requests


@pytest.mark.auth
class TestAuthentication:

    def test_auth_returns_token(self, base_url):
        """TC01 — Auth con credenciales válidas retorna token."""
        response = requests.post(
            f"{base_url}/auth",
            json={"username": "admin", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 0

    def test_auth_invalid_credentials(self, base_url):
        """TC02 — Auth con credenciales inválidas retorna bad credentials."""
        response = requests.post(
            f"{base_url}/auth",
            json={"username": "invalid", "password": "wrongpass"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("reason") == "Bad credentials"

    def test_auth_empty_credentials(self, base_url):
        """TC03 — Auth con campos vacíos retorna bad credentials."""
        response = requests.post(
            f"{base_url}/auth",
            json={"username": "", "password": ""}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("reason") == "Bad credentials"

    def test_auth_missing_fields(self, base_url):
        """TC04 — Auth sin body retorna error."""
        response = requests.post(
            f"{base_url}/auth",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert "reason" in data