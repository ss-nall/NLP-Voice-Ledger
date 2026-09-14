import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.seed_data import seed_database

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    seed_database()

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_voice_spoken_text_api():
    payload = {
        "transcript": "Ramesh Aidhu vandalu ivvali vache vaaram",
        "session_id": "test_api_voice",
        "confidence": 0.95
    }
    response = client.post("/api/voice/process-spoken-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "text_response" in data
    assert "nlp_diagnostics" in data
    assert data["nlp_diagnostics"]["entities"]["amounts"][0]["value"] == 500

def test_conversation_message_api():
    payload = {
        "message": "Venkat ninna 500 ichadu",
        "session_id": "test_api_conv_unique",
        "is_voice": False
    }
    response = client.post("/api/conversation/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message_type"] in ["TRANSACTION_EXECUTED", "CONTRADICTION_CONFIRMATION_REQUIRED"]
    assert "text_response" in data

def test_ledger_transactions_api():
    response = client.get("/api/ledger/transactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_analytics_overview_api():
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_receivables" in data
    assert "total_payables" in data

def test_benchmark_experiment_api():
    response = client.get("/api/benchmark/run-experiment")
    assert response.status_code == 200
    data = response.json()
    assert "approach_a" in data
    assert "approach_b" in data
    assert "approach_c" in data

def test_pavan_payable_reflection():
    client.post("/api/ledger/reset-all")
    payload = {
        "message": "pavan ki 5000 ivaali next week",
        "session_id": "test_pavan_payable",
        "is_voice": False
    }
    response = client.post("/api/conversation/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Pavan" in data["ledger_update"]["actor"] or data["ledger_update"].get("actor_english") == "Pavan"
    assert data["ledger_update"]["entity_type"] == "supplier"
    assert data["ledger_update"]["current_balance"] == 5000.0
    
    # Check that Pavan appears in suppliers API with 5000 balance
    supp_resp = client.get("/api/entities/suppliers")
    assert supp_resp.status_code == 200
    suppliers = supp_resp.json()
    pavan_supp = next((s for s in suppliers if (s.get("name_english") or "").lower() == "pavan" or "pavan" in s["name"].lower()), None)
    assert pavan_supp is not None
    assert pavan_supp["outstanding_balance"] == 5000.0
    
    # Check payment commitments
    comms_resp = client.get("/api/ledger/commitments")
    assert comms_resp.status_code == 200
    comms = comms_resp.json()
    pavan_comm = next((c for c in comms if "pavan" in c["entity_name"].lower()), None)
    assert pavan_comm is not None
    assert pavan_comm["amount"] == 5000.0

def test_reset_all_and_seed_demo():
    # Test reset
    reset_resp = client.post("/api/ledger/reset-all")
    assert reset_resp.status_code == 200
    
    # Check empty customers
    cust_resp = client.get("/api/entities/customers")
    assert cust_resp.status_code == 200
    assert len(cust_resp.json()) == 0
    
    # Test re-seed
    seed_resp = client.post("/api/ledger/seed-demo")
    assert seed_resp.status_code == 200
    
    # Check seeded customers restored
    cust_resp2 = client.get("/api/entities/customers")
    assert cust_resp2.status_code == 200
    assert len(cust_resp2.json()) > 0
