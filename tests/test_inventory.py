from fastapi.testclient import TestClient

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
