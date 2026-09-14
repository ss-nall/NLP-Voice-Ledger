import pytest
from backend.app.database.session import SessionLocal
from backend.app.services.conversation_service import conversation_service
from backend.app.services.analytics_service import analytics_service
from backend.app.api.endpoints.ledger import reset_all_ledger_data

def test_tense_separation_payable_and_paid():
    db = SessionLocal()
    reset_all_ledger_data(db)
    
    # 1. Payable obligation created
    res1 = conversation_service.process_message(db, "రమేష్ కి 1000 కట్టాలి", session_id="test_tense_sess")
    assert res1["success"] is True
    assert res1["ledger_update"]["transaction_type"] == "PAYABLE_OBLIGATION"
    assert res1["ledger_update"]["current_balance"] == 1000.0
    
    ov1 = analytics_service.get_overview(db)
    assert ov1["total_payables"] == 1000.0
    assert ov1["monthly_outflow"] == 0.0
    
    # 2. Payment made reduces payable
    res2 = conversation_service.process_message(db, "రమేష్ కి 500 ఇచ్చేశాను", session_id="test_tense_sess")
    assert res2["success"] is True
    assert res2["ledger_update"]["transaction_type"] == "PAYMENT_MADE"
    assert res2["ledger_update"]["current_balance"] == 500.0
    
    ov2 = analytics_service.get_overview(db)
    assert ov2["total_payables"] == 500.0
    assert ov2["monthly_outflow"] == 500.0
    
    reset_all_ledger_data(db)
    db.close()

def test_tense_separation_receivable_and_received():
    db = SessionLocal()
    reset_all_ledger_data(db)
    
    # 1. Receivable invoice created (సురేష్ నుండి 1000 రావాలి)
    res1 = conversation_service.process_message(db, "సురేష్ నుండి 1000 రావాలి", session_id="test_tense_sess2")
    assert res1["success"] is True
    assert res1["ledger_update"]["transaction_type"] in ["RECEIVABLE_INVOICE", "CREDIT_SALE"]
    assert res1["ledger_update"]["current_balance"] == 1000.0
    
    ov1 = analytics_service.get_overview(db)
    assert ov1["total_receivables"] == 1000.0
    assert ov1["monthly_inflow"] == 0.0
    
    # 2. Customer payment received reduces receivable (సురేష్ 500 ఇచ్చాడు)
    res2 = conversation_service.process_message(db, "సురేష్ 500 ఇచ్చాడు", session_id="test_tense_sess2")
    assert res2["success"] is True
    assert res2["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert res2["ledger_update"]["current_balance"] == 500.0
    
    ov2 = analytics_service.get_overview(db)
    assert ov2["total_receivables"] == 500.0
    assert ov2["monthly_inflow"] == 500.0
    
    reset_all_ledger_data(db)
    db.close()

def test_receivables_with_naaku_and_vachindi():
    db = SessionLocal()
    reset_all_ledger_data(db)
    
    # 1. Receivable: రమేష్ నుంచి 2000 రావాలి
    res1 = conversation_service.process_message(db, "రమేష్ నుంచి 2000 రావాలి", session_id="test_naaku_sess")
    assert res1["success"] is True
    assert res1["ledger_update"]["transaction_type"] in ["RECEIVABLE_INVOICE", "CREDIT_SALE"]
    assert res1["ledger_update"]["current_balance"] == 2000.0
    assert res1["ledger_update"]["entity_type"] == "customer"
    
    # 2. Customer payment with "నాకు": రమేష్ నాకు 500 ఇచ్చాడు
    res2 = conversation_service.process_message(db, "రమేష్ నాకు 500 ఇచ్చాడు", session_id="test_naaku_sess")
    assert res2["success"] is True
    assert res2["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert res2["ledger_update"]["current_balance"] == 1500.0
    assert res2["ledger_update"]["entity_type"] == "customer"
    
    # 3. Customer payment with "వచ్చింది": రమేష్ నుంచి 400 వచ్చింది
    res3 = conversation_service.process_message(db, "రమేష్ నుంచి 400 వచ్చింది", session_id="test_naaku_sess")
    assert res3["success"] is True
    assert res3["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert res3["ledger_update"]["current_balance"] == 1100.0
    
    # 4. Customer payment with "కట్టాడు": రమేష్ 600 కట్టాడు
    res4 = conversation_service.process_message(db, "రమేష్ 600 కట్టాడు", session_id="test_naaku_sess")
    assert res4["success"] is True
    assert res4["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert res4["ledger_update"]["current_balance"] == 500.0
    
    # 5. Customer payment with "చెల్లించాడు": రమేష్ 500 చెల్లించాడు -> Settled!
    res5 = conversation_service.process_message(db, "రమేష్ 500 చెల్లించాడు", session_id="test_naaku_sess")
    assert res5["success"] is True
    assert res5["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert res5["ledger_update"]["current_balance"] == 0.0
    assert res5["ledger_update"]["status"] == "SETTLED"
    
    ov = analytics_service.get_overview(db)
    assert ov["total_receivables"] == 0.0
    assert ov["monthly_inflow"] == 2000.0
    
    reset_all_ledger_data(db)
    db.close()

def test_baki_unnadu_and_honorific_payments():
    db = SessionLocal()
    reset_all_ledger_data(db)
    
    # 1. Receivable with బాకీ ఉన్నాడు: కిరణ్ 3000 బాకీ ఉన్నాడు
    res1 = conversation_service.process_message(db, "కిరణ్ 3000 బాకీ ఉన్నాడు", session_id="test_baki_sess")
    assert res1["success"] is True
    assert res1["ledger_update"]["transaction_type"] in ["RECEIVABLE_INVOICE", "CREDIT_SALE"]
    assert res1["ledger_update"]["current_balance"] == 3000.0
    
    # 2. Payment received with honorific ఇచ్చేశారు: కిరణ్ 1000 ఇచ్చేశారు
    res2 = conversation_service.process_message(db, "కిరణ్ 1000 ఇచ్చేశారు", session_id="test_baki_sess")
    assert res2["success"] is True
    assert res2["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert res2["ledger_update"]["current_balance"] == 2000.0
    
    # 3. Full settlement claim: కిరణ్ మొత్తం ఇచ్చేశాడు (Triggers confirmation modal)
    res3 = conversation_service.process_message(db, "కిరణ్ మొత్తం ఇచ్చేశాడు", session_id="test_baki_sess")
    assert res3["requires_confirmation"] is True
    assert res3["current_balance"] == 2000.0
    
    # User confirms the settlement in modal
    conf_res = conversation_service.confirm_and_apply_event(db, res3["proposed_event"])
    assert conf_res["success"] is True
    assert conf_res["ledger_update"]["current_balance"] == 0.0
    
    reset_all_ledger_data(db)
    db.close()

def test_romanized_and_english_receivables():
    db = SessionLocal()
    reset_all_ledger_data(db)
    
    # 1. Romanized: Ramesh nundi 2000 ravali
    res1 = conversation_service.process_message(db, "Ramesh nundi 2000 ravali", session_id="test_rom_sess")
    assert res1["ledger_update"]["transaction_type"] in ["RECEIVABLE_INVOICE", "CREDIT_SALE"]
    assert res1["ledger_update"]["current_balance"] == 2000.0
    
    # 2. Romanized: Ramesh 1000 ichadu
    res2 = conversation_service.process_message(db, "Ramesh 1000 ichadu", session_id="test_rom_sess")
    assert res2["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert res2["ledger_update"]["current_balance"] == 1000.0
    
    # 3. Romanized: Ramesh nundi 600 vachindi
    res3 = conversation_service.process_message(db, "Ramesh nundi 600 vachindi", session_id="test_rom_sess")
    assert res3["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert res3["ledger_update"]["current_balance"] == 400.0
    
    # 4. English: Received 400 from Ramesh
    res4 = conversation_service.process_message(db, "Received 400 from Ramesh", session_id="test_rom_sess")
    assert res4["ledger_update"]["transaction_type"] == "PAYMENT_RECEIVED"
    assert res4["ledger_update"]["current_balance"] == 0.0
    
    ov = analytics_service.get_overview(db)
    assert ov["total_receivables"] == 0.0
    assert ov["monthly_inflow"] == 2000.0
    
    reset_all_ledger_data(db)
    db.close()

def test_romanized_kattali_and_kattesa():
    db = SessionLocal()
    reset_all_ledger_data(db)
    
    # 1. Ramesh ki 1000 kattali
    res1 = conversation_service.process_message(db, "Ramesh ki 1000 kattali", session_id="test_tense_sess3")
    assert res1["ledger_update"]["transaction_type"] == "PAYABLE_OBLIGATION"
    assert res1["ledger_update"]["current_balance"] == 1000.0
    
    # 2. Ramesh ki 500 kattesa
    res2 = conversation_service.process_message(db, "Ramesh ki 500 kattesa", session_id="test_tense_sess3")
    assert res2["ledger_update"]["transaction_type"] == "PAYMENT_MADE"
    assert res2["ledger_update"]["current_balance"] == 500.0
    
    ov = analytics_service.get_overview(db)
    assert ov["total_payables"] == 500.0
    assert ov["monthly_outflow"] == 500.0
    
    reset_all_ledger_data(db)
    db.close()

def test_idempotency_duplicate_prevention():
    db = SessionLocal()
    reset_all_ledger_data(db)
    
    # Rapid duplicate call (simulating voice onend + Enter key simultaneous trigger)
    res1 = conversation_service.process_message(db, "Ramesh ki 1000 kattali", session_id="test_dup_sess")
    res2 = conversation_service.process_message(db, "Ramesh ki 1000 kattali", session_id="test_dup_sess")
    
    # Second call should be deduplicated and not double-charge balance to 2000
    assert res1["ledger_update"]["current_balance"] == 1000.0
    assert res2["ledger_update"]["current_balance"] == 1000.0
    
    ov = analytics_service.get_overview(db)
    assert ov["total_payables"] == 1000.0
    
    reset_all_ledger_data(db)
    db.close()

def test_indian_accent_spoken_accounting_entry():
    db = SessionLocal()
    reset_all_ledger_data(db)
    
    # 1. "Kiran nundi 5 thouzad ravali" -> Customer Receivable (5000)
    res1 = conversation_service.process_message(db, "Kiran nundi 5 thouzad ravali", session_id="test_accent_acct")
    assert res1["ledger_update"]["direction"] == "receivable"
    assert res1["ledger_update"]["amount"] == 5000.0
    assert res1["ledger_update"]["current_balance"] == 5000.0
    
    # 2. "Kiran 2 thoujand ichadu" -> Payment Received (reduces receivable to 3000)
    res2 = conversation_service.process_message(db, "Kiran 2 thoujand ichadu", session_id="test_accent_acct")
    assert res2["ledger_update"]["direction"] == "receivable"
    assert res2["ledger_update"]["amount"] == 2000.0
    assert res2["ledger_update"]["current_balance"] == 3000.0
    
    # 3. "Supplier ki 10 thouzad ivvali" -> Supplier Payable (10000)
    res3 = conversation_service.process_message(db, "Supplier ki 10 thouzad ivvali", session_id="test_accent_acct_supp")
    assert res3["ledger_update"]["direction"] == "payable"
    assert res3["ledger_update"]["amount"] == 10000.0
    assert res3["ledger_update"]["current_balance"] == 10000.0
    
    # 4. "Supplier ki 4 taujand chellincha" -> Payment Made (reduces payable to 6000)
    res4 = conversation_service.process_message(db, "Supplier ki 4 taujand chellincha", session_id="test_accent_acct_supp")
    assert res4["ledger_update"]["direction"] == "payable"
    assert res4["ledger_update"]["amount"] == 4000.0
    assert res4["ledger_update"]["current_balance"] == 6000.0
    
    reset_all_ledger_data(db)
    db.close()
