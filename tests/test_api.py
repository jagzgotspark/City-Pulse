from fastapi.testclient import TestClient
from src.api.main import app


client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "City Pulse API is running"

def test_get_cities():
    response = client.get("/api/cities")
    assert response.status_code == 200
    assert "cities" in response.json()

def test_get_pulse_lucknow():
    response = client.get("/api/pulse/Lucknow")
    assert response.status_code == 200
    data = response.json()
    assert "pulse_score" in data
    assert "temperature" in data
    assert data["city"] == "Lucknow"

def test_get_pulse_invalid_city():
    response = client.get("/api/pulse/FakeCity123")
    assert response.status_code == 404

def test_get_dashboard():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert "cities" in response.json()

def test_history_invalid_hours():
    response = client.get("/api/history/Lucknow?hours=999")
    assert response.status_code == 422