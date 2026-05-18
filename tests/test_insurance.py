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
