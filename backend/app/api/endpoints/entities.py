from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import json
from backend.app.database.session import get_db
from backend.app.database.models import Business, Customer, Supplier, Transaction, PaymentCommitment

router = APIRouter(prefix="/entities", tags=["Entities & Sub-Ledgers"])

class BusinessUpdatePayload(BaseModel):
    name: str
    owner_name: Optional[str] = None
    phone: Optional[str] = None

@router.get("/business")
def get_business_info(db: Session = Depends(get_db)):
    biz = db.query(Business).first()
    if not biz:
        biz = Business(
            name="నా వ్యాపార ఖాతా (My Khata Book)",
            owner_name="Merchant Owner",
            phone="",
            currency="INR"
        )
        db.add(biz)
        db.commit()
        db.refresh(biz)
    return {
        "id": biz.id,
        "name": biz.name,
        "owner_name": biz.owner_name,
        "phone": biz.phone,
        "currency": biz.currency
    }

@router.put("/business")
def update_business_info(payload: BusinessUpdatePayload, db: Session = Depends(get_db)):
    biz = db.query(Business).first()
    if not biz:
        biz = Business(name=payload.name, owner_name=payload.owner_name or "", phone=payload.phone or "")
        db.add(biz)
    else:
        biz.name = payload.name
        if payload.owner_name is not None:
            biz.owner_name = payload.owner_name
        if payload.phone is not None:
            biz.phone = payload.phone
    db.commit()
    db.refresh(biz)
    return {"success": True, "business": {"name": biz.name, "owner_name": biz.owner_name}}

class CustomerCreatePayload(BaseModel):
    name: str
    phone: Optional[str] = None
    aliases: Optional[List[str]] = None
    credit_limit: Optional[float] = 25000.0
    notes: Optional[str] = None

class SupplierCreatePayload(BaseModel):
    name: str
    phone: Optional[str] = None
    aliases: Optional[List[str]] = None
    notes: Optional[str] = None

@router.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).order_by(Customer.outstanding_balance.desc()).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "name_telugu": c.name_telugu,
            "name_english": c.name_english,
            "phone": c.phone,
            "aliases": c.aliases,
            "outstanding_balance": c.outstanding_balance,
            "credit_limit": c.credit_limit,
            "credit_score": c.credit_score,
            "risk_tier": c.risk_tier,
            "last_payment_date": c.last_payment_date,
            "notes": c.notes
        }
        for c in customers
    ]

@router.get("/customers/{customer_id}")
def get_customer_details(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    txs = db.query(Transaction).filter(
        Transaction.counterparty_type == "customer",
        (Transaction.counterparty_name.ilike(f"%{c.name}%") | Transaction.counterparty_name.ilike(f"%{c.name_english or c.name}%"))
    ).order_by(Transaction.created_at.desc()).all()
    
    commitments = db.query(PaymentCommitment).filter(
        (PaymentCommitment.entity_name.ilike(f"%{c.name}%") | PaymentCommitment.entity_name.ilike(f"%{c.name_english or c.name}%"))
    ).all()
    
    return {
        "customer": {
            "id": c.id,
            "name": c.name,
            "name_telugu": c.name_telugu,
            "name_english": c.name_english,
            "phone": c.phone,
            "aliases": c.aliases,
            "outstanding_balance": c.outstanding_balance,
            "credit_limit": c.credit_limit,
            "credit_score": c.credit_score,
            "risk_tier": c.risk_tier,
            "last_payment_date": c.last_payment_date,
            "notes": c.notes
        },
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.transaction_type,
                "balance_after": t.balance_after,
                "date": t.date,
                "status": t.status,
                "source_text": t.source_text
            }
            for t in txs
        ],
        "commitments": [
            {
                "id": com.id,
                "amount": com.amount,
                "due_date": com.due_date,
                "status": com.status,
                "source_text": com.source_text
            }
            for com in commitments
        ]
    }

@router.post("/customers")
def create_customer(payload: CustomerCreatePayload, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.name.ilike(payload.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer already exists")
        
    c = Customer(
        name=payload.name,
        phone=payload.phone,
        aliases_json=json.dumps(payload.aliases or [payload.name]),
        credit_limit=payload.credit_limit or 25000.0,
        notes=payload.notes
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"success": True, "id": c.id, "name": c.name}

@router.get("/suppliers")
def get_suppliers(db: Session = Depends(get_db)):
    suppliers = db.query(Supplier).order_by(Supplier.outstanding_balance.desc()).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "name_telugu": s.name_telugu,
            "name_english": s.name_english,
            "phone": s.phone,
            "aliases": s.aliases,
            "outstanding_balance": s.outstanding_balance,
            "last_payment_date": s.last_payment_date,
            "notes": s.notes
        }
        for s in suppliers
    ]

@router.get("/suppliers/{supplier_id}")
def get_supplier_details(supplier_id: int, db: Session = Depends(get_db)):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    txs = db.query(Transaction).filter(
        Transaction.counterparty_type == "supplier",
        Transaction.counterparty_name.ilike(f"%{s.name}%")
    ).order_by(Transaction.created_at.desc()).all()
    
    return {
        "supplier": {
            "id": s.id,
            "name": s.name,
            "phone": s.phone,
            "aliases": s.aliases,
            "outstanding_balance": s.outstanding_balance,
            "last_payment_date": s.last_payment_date,
            "notes": s.notes
        },
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.transaction_type,
                "balance_after": t.balance_after,
                "date": t.date,
                "status": t.status,
                "source_text": t.source_text
            }
            for t in txs
        ]
    }

@router.post("/suppliers")
def create_supplier(payload: SupplierCreatePayload, db: Session = Depends(get_db)):
    existing = db.query(Supplier).filter(Supplier.name.ilike(payload.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Supplier already exists")
        
    s = Supplier(
        name=payload.name,
        phone=payload.phone,
        aliases_json=json.dumps(payload.aliases or [payload.name]),
        notes=payload.notes
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"success": True, "id": s.id, "name": s.name}
