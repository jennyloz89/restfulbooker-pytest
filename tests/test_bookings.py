import pytest
import requests
import json


@pytest.mark.functional
class TestGetBookings:

    def test_get_all_bookings(self, base_url):
        """TC05 — GET /booking retorna lista de reservas."""
        response = requests.get(f"{base_url}/booking")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_all_bookings_have_id(self, base_url):
        """TC06 — Cada reserva tiene bookingid."""
        response = requests.get(f"{base_url}/booking")
        data = response.json()
        for booking in data:
            assert "bookingid" in booking
            assert isinstance(booking["bookingid"], int)

    def test_get_booking_by_id(self, base_url, created_booking):
        """TC07 — GET /booking/{id} retorna datos correctos."""
        booking_id = created_booking["id"]
        response = requests.get(f"{base_url}/booking/{booking_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["firstname"] == created_booking["data"]["firstname"]
        assert data["lastname"] == created_booking["data"]["lastname"]
        assert data["totalprice"] == created_booking["data"]["totalprice"]

    def test_get_nonexistent_booking(self, base_url):
        """TC08 — GET /booking/99999 retorna 404."""
        response = requests.get(f"{base_url}/booking/99999")
        assert response.status_code == 404

    def test_get_booking_schema(self, base_url, created_booking):
        """TC09 — Schema de respuesta tiene todos los campos requeridos."""
        booking_id = created_booking["id"]
        response = requests.get(f"{base_url}/booking/{booking_id}")
        data = response.json()
        required_fields = [
            "firstname", "lastname", "totalprice",
            "depositpaid", "bookingdates", "additionalneeds"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        assert "checkin" in data["bookingdates"]
        assert "checkout" in data["bookingdates"]


@pytest.mark.functional
class TestCreateBooking:

    def test_create_booking(self, base_url):
        """TC10 — POST /booking crea reserva correctamente."""
        payload = {
            "firstname": "Test",
            "lastname": "User",
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2025-03-01",
                "checkout": "2025-03-05"
            },
            "additionalneeds": "None"
        }
        response = requests.post(f"{base_url}/booking", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "bookingid" in data
        assert data["booking"]["firstname"] == payload["firstname"]
        assert data["booking"]["totalprice"] == payload["totalprice"]

    def test_create_booking_response_schema(self, base_url):
        """TC11 — Respuesta de creación tiene bookingid y booking."""
        payload = {
            "firstname": "Schema",
            "lastname": "Test",
            "totalprice": 50,
            "depositpaid": False,
            "bookingdates": {
                "checkin": "2025-04-01",
                "checkout": "2025-04-03"
            }
        }
        response = requests.post(f"{base_url}/booking", json=payload)
        data = response.json()
        assert "bookingid" in data
        assert "booking" in data
        assert isinstance(data["bookingid"], int)


@pytest.mark.functional
class TestUpdateBooking:

    def test_update_booking(self, base_url, auth_token, created_booking):
        """TC12 — PUT /booking/{id} actualiza reserva completa."""
        booking_id = created_booking["id"]
        updated = {
            "firstname": "Jennifer",
            "lastname": "Lozano",
            "totalprice": 200,
            "depositpaid": False,
            "bookingdates": {
                "checkin": "2025-05-01",
                "checkout": "2025-05-10"
            },
            "additionalneeds": "Lunch"
        }
        response = requests.put(
            f"{base_url}/booking/{booking_id}",
            json=updated,
            headers={"Cookie": f"token={auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["firstname"] == updated["firstname"]
        assert data["totalprice"] == updated["totalprice"]

    def test_partial_update_booking(self, base_url, auth_token, created_booking):
        """TC13 — PATCH /booking/{id} actualiza campos parciales."""
        booking_id = created_booking["id"]
        response = requests.patch(
            f"{base_url}/booking/{booking_id}",
            json={"firstname": "Patched"},
            headers={"Cookie": f"token={auth_token}"}
        )
        assert response.status_code == 200
        assert response.json()["firstname"] == "Patched"

    def test_update_without_auth(self, base_url, created_booking):
        """TC14 — PUT sin token retorna 403."""
        booking_id = created_booking["id"]
        response = requests.put(
            f"{base_url}/booking/{booking_id}",
            json={"firstname": "NoAuth"}
        )
        assert response.status_code == 403

    def test_delete_booking(self, base_url, auth_token, created_booking):
        """TC15 — DELETE /booking/{id} elimina reserva."""
        booking_id = created_booking["id"]
        response = requests.delete(
            f"{base_url}/booking/{booking_id}",
            headers={"Cookie": f"token={auth_token}"}
        )
        assert response.status_code == 201

        # Verificar que ya no existe
        get_response = requests.get(f"{base_url}/booking/{booking_id}")
        assert get_response.status_code == 404

    def test_delete_without_auth(self, base_url, created_booking):
        """TC16 — DELETE sin token retorna 403."""
        booking_id = created_booking["id"]
        response = requests.delete(f"{base_url}/booking/{booking_id}")
        assert response.status_code == 403