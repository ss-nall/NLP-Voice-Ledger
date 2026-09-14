import pytest
from backend.app.nlp.consistency_engine import consistency_engine

def test_contradiction_full_settlement():
    # Ledger shows ₹3000 pending, user claims complete settlement
    event = {
        "actor": "Ramesh",
        "amount": 0,
        "event_type": "full_settlement",
        "direction": "receivable",
        "source_text": "Ramesh complete ga payment ichesadu"
    }
    validation = consistency_engine.validate_event_against_ledger(
        event=event,
        current_entity_balance=3000.0,
        recent_transactions=[]
    )
    assert validation["requires_confirmation"] is True
    assert validation["is_consistent"] is False
    assert "CONTRADICTORY_SETTLEMENT" in [a["type"] for a in validation["alerts"]]
    assert "₹3,000.00" in validation["confirmation_prompt"]

def test_overpayment_defense():
    # Ledger balance is ₹2000, user states payment of ₹5000
    event = {
        "actor": "Ramesh",
        "amount": 5000.0,
        "event_type": "partial_payment",
        "direction": "receivable",
        "source_text": "Ramesh 5000 ichadu"
    }
    validation = consistency_engine.validate_event_against_ledger(
        event=event,
        current_entity_balance=2000.0,
        recent_transactions=[]
    )
    assert validation["requires_confirmation"] is True
    assert "OVERPAYMENT_EXCEEDS_BALANCE" in [a["type"] for a in validation["alerts"]]

def test_duplicate_transaction_defense():
    event = {
        "actor": "Ramesh",
        "amount": 2000.0,
        "event_type": "partial_payment",
        "direction": "receivable",
        "source_text": "Ramesh 2000 ichadu"
    }
    recent = [{"counterparty_name": "Ramesh", "amount": 2000.0, "date": "2026-09-10"}]
    validation = consistency_engine.validate_event_against_ledger(
        event=event,
        current_entity_balance=5000.0,
        recent_transactions=recent
    )
    assert validation["requires_confirmation"] is True
    assert "POTENTIAL_DUPLICATE_TRANSACTION" in [a["type"] for a in validation["alerts"]]
