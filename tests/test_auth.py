from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_register_and_login():
    # Test registration
    register_response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert register_response.status_code == 200
    assert register_response.json()["email"] == "test@example.com"
    
    # Test login
    login_response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()