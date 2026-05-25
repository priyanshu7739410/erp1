from fastapi.testclient import TestClient
import pytest
from app.models.doctor import Doctor
from app.models.patient import Patient

def get_auth_headers(client: TestClient) -> dict:
    resp = client.post("/api/v1/auth/token", data={"username": "testadmin", "password": "testpass"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

def test_inventory_management(client: TestClient):
    headers = get_auth_headers(client)
    
    # Create item
    item_res = client.post("/api/v1/inventory/items", headers=headers, json={
        "name": "Paracetamol 500mg",
        "sku": "MED-PARA-500",
        "category": "medication",
        "unit": "tablet",
        "quantity": 100,
        "reorder_level": 20,
        "price": 0.50
    })
    assert item_res.status_code == 200
    item = item_res.json()
    assert item["name"] == "Paracetamol 500mg"
    assert item["quantity"] == 100
 
    # Record transaction
    tx_res = client.post("/api/v1/inventory/transactions", headers=headers, json={
        "item_id": item["id"],
        "quantity_change": 50,
        "transaction_type": "in",
        "notes": "Restock supplier",
        "recorded_by": "testadmin"
    })
    assert tx_res.status_code == 200
    assert tx_res.json()["quantity_change"] == 50

def test_doctor_prescription_form_security(client: TestClient, db_session):
    # Register doctor user
    reg_doc = client.post(
        "/api/v1/auth/register",
        json={
            "username": "doc_sarah",
            "email": "sarah@hospital.com",
            "password": "docpassword123",
            "role": "doctor"
        }
    )
    assert reg_doc.status_code == 200
    
    # Create doctor record directly in db so email matches
    doctor = Doctor(
        first_name="Sarah",
        last_name="Jenkins",
        specialty="Cardiology",
        license_number="LIC-123456",
        phone="555123",
        email="sarah@hospital.com",
        is_active=True
    )
    db_session.add(doctor)
    
    # Create another doctor record to verify the dropdown excludes them
    other_doctor = Doctor(
        first_name="Marcus",
        last_name="Vance",
        specialty="Pediatrics",
        license_number="LIC-654321",
        phone="555987",
        email="marcus@hospital.com",
        is_active=True
    )
    db_session.add(other_doctor)
    
    # Create patient record so there is a patient to prescribe to
    patient = Patient(
        name="John Doe",
        email="john@doe.com",
        age=30,
        gender="Male",
        phone="555111",
        is_active=True
    )
    db_session.add(patient)
    db_session.commit()
    
    # Log in as doctor
    login_resp = client.post(
        "/api/v1/auth/token",
        data={"username": "doc_sarah", "password": "docpassword123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    # Set cookie
    client.cookies.set("access_token", f"Bearer {token}")
    
    # Request /prescriptions/new
    resp = client.get("/prescriptions/new")
    assert resp.status_code == 200
    # The page should show Dr. Sarah Jenkins
    assert "Dr. Sarah Jenkins" in resp.text
    # The page should NOT show Dr. Marcus Vance in the selection options
    assert "Dr. Marcus Vance" not in resp.text
    
    # Post prescription for self (Dr. Sarah Jenkins)
    post_resp = client.post(
        "/prescriptions/new",
        data={
            "patient_id": patient.id,
            "doctor_id": doctor.id,
            "medication_name": "Amoxicillin",
            "dosage": "1 capsule",
            "frequency": "2 times daily",
            "duration_days": 7
        },
        follow_redirects=False
    )
    # Redirect back to inventory on success
    assert post_resp.status_code in [302, 307]
    assert post_resp.headers["location"] == "/inventory"
    
    # Post prescription for another doctor (Dr. Marcus Vance) - should fail with redirect to error
    bad_post_resp = client.post(
        "/prescriptions/new",
        data={
            "patient_id": patient.id,
            "doctor_id": other_doctor.id,
            "medication_name": "Ibuprofen",
            "dosage": "1 tablet",
            "frequency": "As needed",
            "duration_days": 5
        },
        follow_redirects=False
    )
    assert bad_post_resp.status_code in [302, 307]
    assert "error=Access%20Denied" in bad_post_resp.headers["location"]

