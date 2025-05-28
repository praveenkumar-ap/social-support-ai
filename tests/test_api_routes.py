import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_submit_application_422():
    # Missing required fields should cause validation error
    response = client.post("/applications/", json={"foo": "bar"})
    assert response.status_code == 422
