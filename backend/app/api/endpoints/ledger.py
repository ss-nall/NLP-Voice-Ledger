from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from backend.app.database.session import get_db
from backend.app.database.models import (
    Transaction, FinancialEventLog, PaymentCommitment, AuditLog
)

router = APIRouter(prefix="/ledger", tags=["Auditable Ledger"])

class CorrectionPayload(BaseModel):
    transaction_id: str
    corrected_amount: Optional[float] = None
    corrected_actor: Optional[str] = None
    corrected_type: Optional[str] = None
    reason: str

@router.get("/transactions")
def get_transactions(
    direction: Optional[str] = None,
    counterparty_type: Optional[str] = None,
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).order_by(Transaction.created_at.desc())
    if direction:
        query = query.filter(Transaction.direction == direction)
    if counterparty_type:
        query = query.filter(Transaction.counterparty_type == counterparty_type)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if status:
        query = query.filter(Transaction.status == status)
    if search:
        query = query.filter(Transaction.counterparty_name.ilike(f"%{search}%"))
        
    txs = query.limit(limit).all()
    return [
        {
            "id": t.id,
            "event_id": t.event_id,
            "counterparty_name": t.counterparty_name,
            "counterparty_type": t.counterparty_type,
            "transaction_type": t.transaction_type,
            "direction": t.direction,
            "amount": t.amount,
            "balance_after": t.balance_after,
            "payment_method": t.payment_method,
            "status": t.status,
            "date": t.date,
            "source_text": t.source_text,
            "confidence": t.confidence,
            "is_anomaly": t.is_anomaly,
            "created_at": t.created_at.isoformat()
        }
        for t in txs
    ]

@router.get("/events")
def get_financial_events(limit: int = 50, db: Session = Depends(get_db)):
    events = db.query(FinancialEventLog).order_by(FinancialEventLog.created_at.desc()).limit(limit).all()
    return [
        {
            "event_id": e.event_id,
            "event_type": e.event_type,
            "actor": e.actor,
            "amount": e.amount,
            "currency": e.currency,
            "direction": e.direction,
            "payment_method": e.payment_method,
            "event_date": e.event_date,
            "due_date": e.due_date,
            "source_text": e.source_text,
            "confidence": e.confidence,
            "explanation": e.explanation,
            "created_at": e.created_at.isoformat()
        }
        for e in events
    ]

@router.get("/commitments")
def get_payment_commitments(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PaymentCommitment).order_by(PaymentCommitment.due_date.asc())
    if status:
        query = query.filter(PaymentCommitment.status == status)
    commitments = query.all()
    return [
        {
            "id": c.id,
            "entity_name": c.entity_name,
            "entity_type": c.entity_type,
            "amount": c.amount,
            "due_date": c.due_date,
            "status": c.status,
            "source_text": c.source_text,
            "created_at": c.created_at.isoformat()
        }
        for c in commitments
    ]

@router.get("/audit-logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "action": l.action,
            "details": l.details,
            "actor": l.actor,
            "created_at": l.created_at.isoformat()
        }
        for l in logs
    ]

@router.get("/health")
def get_ledger_health(db: Session = Depends(get_db)):
    """
    Returns live Trial Balance, General Ledger vs Subledger invariant status,
    total debits, total credits, and discrepancy.
    """
    from backend.app.services.ledger_service import ledger_service
    return ledger_service.check_ledger_health(db)


@router.get("/journal")
def get_journal_entries(limit: int = 50, db: Session = Depends(get_db)):
    """
    Returns double-entry General Ledger journal entries with balanced Debit/Credit line items.
    """
    from backend.app.services.ledger_service import ledger_service
    return ledger_service.get_journal_entries(db, limit=limit)


class TransactionUpdateSchema(BaseModel):
    amount: Optional[float] = None
    counterparty_name: Optional[str] = None
    direction: Optional[str] = None
    transaction_type: Optional[str] = None
    payment_method: Optional[str] = None
    date: Optional[str] = None


@router.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: str, payload: TransactionUpdateSchema, db: Session = Depends(get_db)):
    """
    Updates transaction parameters, recalculates sub-ledger balances with differential delta,
    and updates General Ledger double-entry journal items.
    """
    from backend.app.services.ledger_service import ledger_service
    try:
        res = ledger_service.update_transaction(
            db=db,
            transaction_id=transaction_id,
            amount=payload.amount,
            counterparty_name=payload.counterparty_name,
            direction=payload.direction,
            transaction_type=payload.transaction_type,
            payment_method=payload.payment_method,
            date=payload.date
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """
    Safely deletes a transaction, voids GL journal line items, reverses sub-ledger balances,
    and maintains double-entry accounting integrity.
    """
    from backend.app.services.ledger_service import ledger_service
    try:
        res = ledger_service.delete_transaction(db=db, transaction_id=transaction_id)
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/correct-transaction")
def correct_transaction(payload: CorrectionPayload, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == payload.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    old_amt = tx.amount
    if payload.corrected_amount is not None:
        tx.amount = payload.corrected_amount
    if payload.corrected_actor:
        tx.counterparty_name = payload.corrected_actor
    if payload.corrected_type:
        tx.transaction_type = payload.corrected_type
        
    db.add(AuditLog(
        action="TRANSACTION_CORRECTION",
        details=f"Tx {tx.id} corrected by user. Amount: ₹{old_amt} -> ₹{tx.amount}. Reason: {payload.reason}"
    ))
    db.commit()
    db.refresh(tx)
    return {"success": True, "message": "Transaction corrected successfully", "transaction_id": tx.id}


@router.post("/reset-all")
def reset_all_ledger_data(db: Session = Depends(get_db)):
    """Wipes all transactions, journal entries, counterparties, logs, and resets to clean zero state."""
    from backend.app.database.models import (
        Customer, Supplier, Transaction, FinancialEventLog,
        PaymentCommitment, TransactionStateHistory, AuditLog, ConversationMessage,
        JournalEntry, JournalLineItem
    )
    db.query(JournalLineItem).delete()
    db.query(JournalEntry).delete()
    db.query(Transaction).delete()
    db.query(PaymentCommitment).delete()
    db.query(FinancialEventLog).delete()
    db.query(TransactionStateHistory).delete()
    db.query(ConversationMessage).delete()
    db.query(AuditLog).delete()
    db.query(Customer).delete()
    db.query(Supplier).delete()
    
    db.add(AuditLog(
        action="RESET_LEDGER_FRESH_START",
        details="User reset all transactions and entities to start with a fresh empty ledger."
    ))
    db.commit()
    return {"success": True, "message": "Ledger cleared completely. You are ready to start with a clean slate!"}


@router.post("/seed-demo")
def seed_demo_data(db: Session = Depends(get_db)):
    """Seeds sample data for testing purposes."""
    from backend.app.database.seed_data import seed_database
    seed_database()
    return {"success": True, "message": "Demo data seeded successfully."}
