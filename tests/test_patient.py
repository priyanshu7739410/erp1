from fastapi.testclient import TestClient

def get_auth_headers(client: TestClient) -> dict:
    resp = client.post("/api/v1/auth/token", data={"username": "testadmin", "password": "testpass"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_patient(client: TestClient):
    headers = get_auth_headers(client)
    response = client.post(
        "/api/v1/patients/",
        headers=headers,
        json={
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "age": 28,
            "gender": "Female",
            "phone": "+15559876543",
            "insurance_provider": "Blue Cross"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["id"] is not None

def test_get_patients_list(client: TestClient):
    headers = get_auth_headers(client)
    # create patient first
    client.post(
        "/api/v1/patients/",
        headers=headers,
        json={"name": "Alice", "age": 30, "gender": "Female", "phone": "123456"}
    )
    
    response = client.get("/api/v1/patients/search", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
