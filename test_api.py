from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "alive"}

def test_predict_instruction():
    response = client.get("/predict")
    assert response.status_code == 200

def test_prediction_post():
    payload = {
        "data": {
            "area": 120,
            "property_type": "HOUSE",
            "rooms_number": 4,
            "zip_code": 1000
        }
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "prediction" in response.json()