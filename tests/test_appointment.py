from fastapi.testclient import TestClient

def get_auth_headers(client: TestClient) -> dict:
    resp = client.post("/api/v1/auth/token", data={"username": "testadmin", "password": "testpass"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

def test_create_appointment(client: TestClient):
    headers = get_auth_headers(client)
    
    # Create patient
    p_res = client.post("/api/v1/patients/", headers=headers, json={"name": "Bob", "age": 40, "gender": "Male", "phone": "555111"})
    patient_id = p_res.json()["id"]
    
    # Create doctor
    d_res = client.post("/api/v1/doctors/", headers=headers, json={"first_name": "Gregory", "last_name": "House", "specialty": "Diagnostic Medicine", "license_number": "LIC998", "phone": "555222", "email": "house@hospital.com", "department": "Diagnostics"})
    doctor_id = d_res.json()["id"]

    # Schedule appointment
    appt_res = client.post("/api/v1/appointments/", headers=headers, json={
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "scheduled_start": "2026-06-01T10:00:00",
        "scheduled_end": "2026-06-01T10:30:00",
        "reason": "Leg pain"
    })
    assert appt_res.status_code == 200
    appt = appt_res.json()
    assert appt["patient_id"] == patient_id
    assert appt["status"] == "scheduled"
