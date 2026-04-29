import random
import string
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_random_string(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))

test_user = {
    "email": f"{get_random_string()}@example.com",
    "password": "StrongPassword123!"
}

def test_swagger_docs_accessible():
    response = client.get("/docs")
    assert response.status_code == 200

def test_user_signup():
    response = client.post("/signup", json=test_user)
    assert response.status_code in (200, 201)
    
def test_user_login():
    response = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"