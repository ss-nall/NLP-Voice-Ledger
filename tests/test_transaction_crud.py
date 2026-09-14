import pytest
from backend.app.database.session import SessionLocal
from backend.app.database.models import Customer, Supplier, Transaction, JournalEntry, JournalLineItem
from backend.app.services.conversation_service import conversation_service
from backend.app.services.ledger_service import ledger_service
from backend.app.api.endpoints.ledger import reset_all_ledger_data

def test_delete_transaction_customer_balance_rollback():
    db = SessionLocal()
    reset_all_ledger_data(db)

    # 1. Book a credit sale for Ramesh of ₹5,000
    res1 = conversation_service.process_message(db, "రమేష్ కి 5000 సరుకు అమ్మాను", session_id="test_crud_sess")
    assert res1["success"] is True
    cust = db.query(Customer).first()
    assert cust.outstanding_balance == 5000.0
    tx = db.query(Transaction).first()
    tx_id = tx.id

    # Verify Journal Entry was created
    je_count_before = db.query(JournalEntry).count()
    assert je_count_before >= 1

    # 2. Delete the transaction
    del_res = ledger_service.delete_transaction(db, tx_id)
    assert del_res["success"] is True

    # 3. Verify Customer balance rolled back to ₹0.0
    db.refresh(cust)
    assert cust.outstanding_balance == 0.0

    # 4. Verify transaction and journal entries deleted
    assert db.query(Transaction).filter(Transaction.id == tx_id).first() is None
    assert db.query(JournalEntry).filter(JournalEntry.transaction_id == tx_id).count() == 0

    reset_all_ledger_data(db)
    db.close()


def test_update_transaction_amount_and_actor():
    db = SessionLocal()
    reset_all_ledger_data(db)

    # 1. Book a supplier purchase: Prem ₹10,000
    res1 = conversation_service.process_message(db, "ప్రేమ్ దగ్గర 10000 సరుకు కొన్నాను", session_id="test_crud_sess")
    assert res1["success"] is True
    supp = db.query(Supplier).first()
    assert supp.outstanding_balance == 10000.0
    tx = db.query(Transaction).first()

    # 2. Update transaction: Amount changed to ₹15,000
    up_res = ledger_service.update_transaction(db, tx.id, amount=15000.0)
    assert up_res["success"] is True
    assert up_res["amount"] == 15000.0

    # Verify Supplier balance updated to ₹15,000
    db.refresh(supp)
    assert supp.outstanding_balance == 15000.0

    # 3. Update transaction counterparty to "దీపక్"
    up_res2 = ledger_service.update_transaction(db, tx.id, counterparty_name="దీపక్")
    assert up_res2["success"] is True

    # Prem balance should revert to ₹0.0, Deepak balance should be ₹15,000
    db.refresh(supp)
    assert supp.outstanding_balance == 0.0
    deepak_supp = ledger_service.get_supplier_by_name(db, "దీపక్")
    assert deepak_supp is not None
    assert deepak_supp.outstanding_balance == 15000.0

    reset_all_ledger_data(db)
    db.close()
