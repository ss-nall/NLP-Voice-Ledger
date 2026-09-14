import pytest
from backend.app.database.session import SessionLocal
from backend.app.database.models import Customer, Supplier, Transaction
from backend.app.services.conversation_service import conversation_service
from backend.app.services.ledger_service import ledger_service
from backend.app.api.endpoints.ledger import reset_all_ledger_data

def test_multi_turn_canonical_entity_deduplication():
    db = SessionLocal()
    reset_all_ledger_data(db)

    # 1. First mention: English "Pavan"
    res1 = conversation_service.process_message(db, "Pavan naku 500 ichadu", session_id="test_sess_pavan")
    assert res1["success"] is True
    assert db.query(Customer).count() == 1
    cust = db.query(Customer).first()
    assert "Pavan" in cust.name or "పవన్" in cust.name
    initial_id = cust.id

    # 2. Second mention: Telugu script "పవన్ 1000 ఇచ్చాడు"
    res2 = conversation_service.process_message(db, "పవన్ 1000 ఇచ్చాడు", session_id="test_sess_pavan")
    assert res2["success"] is True
    # Must NOT create a second customer row!
    assert db.query(Customer).count() == 1
    assert db.query(Customer).first().id == initial_id

    # 3. Third mention: With Telugu honorific "Pavan garu 200 icharu"
    res3 = conversation_service.process_message(db, "Pavan garu 200 icharu", session_id="test_sess_pavan")
    assert res3["success"] is True
    assert db.query(Customer).count() == 1
    assert db.query(Customer).first().id == initial_id

    # 4. Fourth mention: Phonetic variant "Pawan 300 ichadu"
    res4 = conversation_service.process_message(db, "Pawan 300 ichadu", session_id="test_sess_pavan")
    assert res4["success"] is True
    assert db.query(Customer).count() == 1
    assert db.query(Customer).first().id == initial_id

    # Total 4 transactions all linked to the exact same customer ID!
    txs = db.query(Transaction).filter(Transaction.counterparty_id == initial_id).all()
    assert len(txs) == 4

    reset_all_ledger_data(db)
    db.close()

def test_supplier_canonical_entity_deduplication():
    db = SessionLocal()
    reset_all_ledger_data(db)

    # 1. First mention: Telugu script "రమేష్ కి 5000 ఇచ్చేశాను"
    res1 = conversation_service.process_message(db, "రమేష్ కి 5000 ఇచ్చేశాను", session_id="test_sess_supp")
    assert res1["success"] is True
    assert db.query(Supplier).count() == 1
    supp = db.query(Supplier).first()
    supp_id = supp.id

    # 2. Second mention: English Romanized "Ramesh ki 2000 kattanu"
    res2 = conversation_service.process_message(db, "Ramesh ki 2000 kattanu", session_id="test_sess_supp")
    assert res2["success"] is True
    assert db.query(Supplier).count() == 1
    assert db.query(Supplier).first().id == supp_id

    # 3. Third mention: With honorific "Ramesh seth ki 1000 kattanu"
    res3 = conversation_service.process_message(db, "Ramesh seth ki 1000 kattanu", session_id="test_sess_supp")
    assert res3["success"] is True
    assert db.query(Supplier).count() == 1
    assert db.query(Supplier).first().id == supp_id

    reset_all_ledger_data(db)
    db.close()
