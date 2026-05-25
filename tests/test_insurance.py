from fastapi.testclient import TestClient

def get_auth_headers(client: TestClient) -> dict:
    resp = client.post("/api/v1/auth/token", data={"username": "testadmin", "password": "testpass"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

def test_insurance_policy_creation_and_check(client: TestClient):
    headers = get_auth_headers(client)
    
    # Create patient
    p_res = client.post("/api/v1/patients/", headers=headers, json={"name": "Charlie", "age": 25, "gender": "Male", "phone": "555333"})
    patient_id = p_res.json()["id"]

    # Upload insurance policy text
    policy_res = client.post("/api/v1/insurance/policies/upload-text", headers=headers, json={
        "patient_id": patient_id,
        "policy_text": "Provider: Aetna Health\nPolicy No: AET-555999\nDeductible: $250.00\nCopay: $25.00\nExclusions: Experimental therapies, Cosmetic surgery"
    })
    assert policy_res.status_code == 200
    policy = policy_res.json()
    assert policy["provider_name"] == "Aetna Health"
    assert policy["deductible"] == 250.0
    assert policy["co_pay"] == 25.0

def test_patient_insurance_web_access(client: TestClient):
    # Register patient user
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": "pat_charlie",
            "email": "charlie@hospital.com",
            "password": "patpassword123",
            "role": "patient"
        }
    )
    assert reg_resp.status_code == 200
    
    # Create patient record via API with same email so display name / ID matches
    admin_headers = get_auth_headers(client)
    client.post(
        "/api/v1/patients/",
        headers=admin_headers,
        json={
            "name": "Charlie", 
            "email": "charlie@hospital.com",
            "age": 25, 
            "gender": "Male", 
            "phone": "555333"
        }
    )
    
    # Log in as patient to get JWT token
    login_resp = client.post(
        "/api/v1/auth/token",
        data={"username": "pat_charlie", "password": "patpassword123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    # Set cookie
    client.cookies.set("access_token", f"Bearer {token}")
    
    # Request /insurance redirect
    redir_resp = client.get("/insurance", follow_redirects=False)
    assert redir_resp.status_code in [302, 307]
    assert redir_resp.headers["location"] == "/insurance/warnings"
    
    # Request /insurance/warnings
    warnings_resp = client.get("/insurance/warnings")
    assert warnings_resp.status_code == 200
    assert "My Insurance Benefits" in warnings_resp.text or "No Active Insurance Policy Registered" in warnings_resp.text
    
    # Request /insurance/upload
    upload_resp = client.get("/insurance/upload")
    assert upload_resp.status_code == 200
    assert "Patient Name" in upload_resp.text

