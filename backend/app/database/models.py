import uuid
import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="నా వ్యాపార ఖాతా (My Khata Book)")
    owner_name = Column(String(100), default="Merchant")
    phone = Column(String(20), default="")
    currency = Column(String(10), default="INR")
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    name_telugu = Column(String(100), nullable=True)
    name_english = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    aliases_json = Column(Text, default="[]")  # e.g. ["Ramesh", "రమేష్", "Ramesh anna"]
    outstanding_balance = Column(Float, default=0.0)
    credit_limit = Column(Float, default=25000.0)
    credit_score = Column(Integer, default=720)  # 300 to 850
    risk_tier = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    last_payment_date = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @property
    def aliases(self):
        try:
            return json.loads(self.aliases_json)
        except Exception:
            return []
            
    @aliases.setter
    def aliases(self, val):
        self.aliases_json = json.dumps(val)

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    name_telugu = Column(String(100), nullable=True)
    name_english = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    aliases_json = Column(Text, default="[]")
    outstanding_balance = Column(Float, default=0.0)  # Amount we owe them
    last_payment_date = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @property
    def aliases(self):
        try:
            return json.loads(self.aliases_json)
        except Exception:
            return []
            
    @aliases.setter
    def aliases(self, val):
        self.aliases_json = json.dumps(val)

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: f"tx_{uuid.uuid4().hex[:8]}")
    event_id = Column(String(36), index=True)
    counterparty_type = Column(String(20))  # 'customer' or 'supplier'
    counterparty_id = Column(Integer, nullable=True)
    counterparty_name = Column(String(100), index=True)
    counterparty_name_telugu = Column(String(100), nullable=True)
    counterparty_name_english = Column(String(100), nullable=True)
    transaction_type = Column(String(50))  # CREDIT_SALE, PAYMENT_RECEIVED, PAYMENT_MADE, ADVANCE, REFUND
    direction = Column(String(20))  # 'receivable' or 'payable'
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, default=0.0)
    payment_method = Column(String(50), default="cash")
    status = Column(String(50), default="COMPLETED")  # DRAFT, COMPLETED, SETTLED, DISPUTED, CANCELLED
    date = Column(String(20))
    source_text = Column(Text)
    confidence = Column(Float, default=1.0)
    is_anomaly = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class FinancialEventLog(Base):
    """Immutable audit trail of every parsed NLP event."""
    __tablename__ = "financial_event_logs"
    
    event_id = Column(String(36), primary_key=True)
    event_type = Column(String(50))
    actor = Column(String(100))
    actor_telugu = Column(String(100), nullable=True)
    actor_english = Column(String(100), nullable=True)
    counterparty = Column(String(100), default="Business")
    amount = Column(Float)
    currency = Column(String(10), default="INR")
    direction = Column(String(20))
    payment_method = Column(String(50))
    event_date = Column(String(20))
    due_date = Column(String(20), nullable=True)
    source_text = Column(Text)
    confidence = Column(Float)
    explanation = Column(Text)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class PaymentCommitment(Base):
    __tablename__ = "payment_commitments"
    
    id = Column(String(36), primary_key=True, default=lambda: f"com_{uuid.uuid4().hex[:8]}")
    entity_type = Column(String(20))  # 'customer' or 'supplier'
    entity_id = Column(Integer, nullable=True)
    entity_name = Column(String(100), index=True)
    amount = Column(Float)
    due_date = Column(String(20), index=True)
    status = Column(String(20), default="PENDING")  # PENDING, FULFILLED, OVERDUE, BROKEN
    source_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class TransactionStateHistory(Base):
    """Tracks state lifecycle transitions: CREDIT_SALE -> PAYMENT_DUE -> PAYMENT_PROMISED -> PARTIAL_PAYMENT -> SETTLED."""
    __tablename__ = "transaction_state_history"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String(100), index=True)
    from_state = Column(String(50))
    to_state = Column(String(50))
    amount_change = Column(Float, default=0.0)
    current_balance = Column(Float)
    trigger_event_id = Column(String(36), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BusinessDocument(Base):
    """Unstructured documents for RAG (Invoices, Receipts, Credit policies)."""
    __tablename__ = "business_documents"
    
    id = Column(String(36), primary_key=True, default=lambda: f"doc_{uuid.uuid4().hex[:8]}")
    title = Column(String(200))
    doc_type = Column(String(50))  # INVOICE, CREDIT_POLICY, RECEIPT, AGREEMENT
    content = Column(Text)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    sender = Column(String(20))  # 'user' or 'system'
    message_text = Column(Text)
    is_voice = Column(Boolean, default=False)
    pipeline_dump_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100))
    details = Column(Text)
    actor = Column(String(50), default="system")
    created_at = Column(DateTime, default=datetime.utcnow)


class JournalEntry(Base):
    """
    General Ledger double-entry transaction header.
    Guarantees sum(Debits) == sum(Credits).
    """
    __tablename__ = "journal_entries"
    
    id = Column(String(36), primary_key=True, default=lambda: f"je_{uuid.uuid4().hex[:8]}")
    transaction_id = Column(String(36), nullable=True, index=True)
    event_id = Column(String(36), index=True)
    entry_date = Column(String(20), nullable=False)
    description = Column(Text)
    reference = Column(String(100), nullable=True)
    total_amount = Column(Float, nullable=False, default=0.0)
    is_balanced = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    lines = relationship("JournalLineItem", back_populates="journal_entry", cascade="all, delete-orphan")


class JournalLineItem(Base):
    """
    Individual debit or credit leg of a double entry transaction.
    """
    __tablename__ = "journal_line_items"
    
    id = Column(String(36), primary_key=True, default=lambda: f"jli_{uuid.uuid4().hex[:8]}")
    journal_entry_id = Column(String(36), ForeignKey("journal_entries.id"), index=True, nullable=False)
    account_type = Column(String(20), nullable=False)  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    account_name = Column(String(50), nullable=False)  # ACCOUNTS_RECEIVABLE, ACCOUNTS_PAYABLE, CASH_AND_BANK, SALES_REVENUE, PURCHASES_EXPENSE, OPERATING_EXPENSE
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    entity_type = Column(String(20), nullable=True)  # customer, supplier, other
    entity_id = Column(Integer, nullable=True)
    entity_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    journal_entry = relationship("JournalEntry", back_populates="lines")

