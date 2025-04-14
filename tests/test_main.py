from fastapi.testclient import TestClient
from one_shot_api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the One-Shot API"}

def test_read_docs():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_read_openapi():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    schema = response.json()
    assert schema["info"]["title"] == "One-Shot API"
    assert schema["info"]["version"] == "0.1.0" 