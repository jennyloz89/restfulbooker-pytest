import pytest
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")
# No usar USERNAME: en Windows es la variable de sesión del SO y oculta .env con load_dotenv(override=False).
BOOKER_USERNAME = os.getenv("BOOKER_USERNAME", "admin")
BOOKER_PASSWORD = os.getenv("BOOKER_PASSWORD", "password123")


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def auth_token():
    """Obtiene token de autenticación — se reutiliza en toda la sesión."""
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": BOOKER_USERNAME, "password": BOOKER_PASSWORD}
    )
    assert response.status_code == 200, f"Auth failed: {response.text}"
    token = response.json().get("token")
    assert token, "Token not found in response"
    return token


@pytest.fixture(scope="function")
def created_booking(base_url, auth_token):
    """Crea una reserva de prueba y la elimina después del test."""
    payload = {
        "firstname": "Jenny",
        "lastname": "Lozano",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-01-01",
            "checkout": "2025-01-10"
        },
        "additionalneeds": "Breakfast"
    }
    response = requests.post(f"{base_url}/booking", json=payload)
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]

    yield {"id": booking_id, "data": payload}

    # Teardown — elimina la reserva después del test
    requests.delete(
        f"{base_url}/booking/{booking_id}",
        headers={"Cookie": f"token={auth_token}"}
    )