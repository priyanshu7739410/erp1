from fastapi.testclient import TestClient

def get_auth_headers(client: TestClient) -> dict:
    resp = client.post("/api/v1/auth/token", data={"username": "testadmin", "password": "testpass"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_staff(client: TestClient):
    headers = get_auth_headers(client)
    response = client.post(
        "/api/v1/staff/",
        headers=headers,
        json={
            "first_name": "Test",
            "last_name": "Staff",
            "role": "nurse",
            "employee_id": "EMP-TST-001",
            "phone": "+15551234567",
            "email": "test.staff@hospital.erp",
            "salary": 4500.0,
            "shift_time": "night"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["employee_id"] == "EMP-TST-001"
    assert data["salary"] == 4500.0
    assert data["shift_time"] == "night"

def test_list_staff(client: TestClient):
    headers = get_auth_headers(client)
    # Create a staff member
    client.post(
        "/api/v1/staff/",
        headers=headers,
        json={
            "first_name": "List",
            "last_name": "Staff",
            "role": "receptionist",
            "employee_id": "EMP-TST-002",
            "phone": "+15557654321",
            "email": "list.staff@hospital.erp",
            "salary": 3000.0,
            "shift_time": "day"
        }
    )
    response = client.get("/api/v1/staff/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    # Check if new fields are present
    item = [x for x in data["items"] if x["employee_id"] == "EMP-TST-002"][0]
    assert item["salary"] == 3000.0
    assert item["shift_time"] == "day"

def test_update_staff(client: TestClient):
    headers = get_auth_headers(client)
    # Create staff
    resp = client.post(
        "/api/v1/staff/",
        headers=headers,
        json={
            "first_name": "Update",
            "last_name": "Staff",
            "role": "pharmacist",
            "employee_id": "EMP-TST-003",
            "phone": "+15551112222",
            "email": "up.staff@hospital.erp",
            "salary": 4000.0,
            "shift_time": "day"
        }
    )
    staff_id = resp.json()["id"]

    # Update salary and shift
    update_resp = client.put(
        f"/api/v1/staff/{staff_id}",
        headers=headers,
        json={
            "salary": 4800.5,
            "shift_time": "night"
        }
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["salary"] == 4800.5
    assert data["shift_time"] == "night"
