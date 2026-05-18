from fastapi.testclient import TestClient

def test_login_success(client: TestClient):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testadmin", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure(client: TestClient):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testadmin", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_register_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newdoctor",
            "email": "doctor@hospital.com",
            "password": "docpassword123",
            "role": "doctor"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newdoctor"
    assert data["role"] == "doctor"
