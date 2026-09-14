import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.session import SessionLocal, engine, Base
from backend.app.database.models import (
    Business, Customer, Supplier, Transaction, FinancialEventLog,
    PaymentCommitment, TransactionStateHistory, BusinessDocument
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if already seeded
    if db.query(Customer).count() > 0:
        db.close()
        return
        
    print("Seeding database with realistic bilingual financial records...")
    
    # 1. Create Business
    if db.query(Business).count() == 0:
        business = Business(
            name="Sri Lakshmi Kirana & General Stores",
            owner_name="Venkat Rao",
            phone="+91 9876543210",
            currency="INR"
        )
        db.add(business)
        db.commit()
    
    # 2. Create Customers
    customers = [
        Customer(
            name="Ramesh Kirana",
            phone="+91 9848012345",
            aliases_json=json.dumps(["Ramesh", "Ramesh anna", "Ramesh garu", "Ramesh Kirana"]),
            outstanding_balance=5000.0,
            credit_limit=25000.0,
            credit_score=720,
            risk_tier="LOW",
            last_payment_date=(datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d"),
            notes="Regular customer since 2023. Owns a nearby vegetable & kirana stall."
        ),
        Customer(
            name="Suresh Electricals",
            phone="+91 9848023456",
            aliases_json=json.dumps(["Suresh", "Suresh garu", "Suresh Electricals", "Suresh anna"]),
            outstanding_balance=3500.0,
            credit_limit=30000.0,
            credit_score=680,
            risk_tier="MEDIUM",
            last_payment_date=(datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"),
            notes="Electrical contractor, usually pays in weekly installments."
        ),
        Customer(
            name="Lakshmi Traders",
            phone="+91 9848034567",
            aliases_json=json.dumps(["Lakshmi", "Lakshmi Traders", "Lakshmi akka"]),
            outstanding_balance=12000.0,
            credit_limit=50000.0,
            credit_score=790,
            risk_tier="LOW",
            last_payment_date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            notes="Wholesale rice and pulses partner."
        ),
        Customer(
            name="Venkat Cloth Stores",
            phone="+91 9848045678",
            aliases_json=json.dumps(["Venkat", "Venkat Rao", "Venkat Cloths"]),
            outstanding_balance=1500.0,
            credit_limit=15000.0,
            credit_score=810,
            risk_tier="LOW",
            last_payment_date=(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            notes="Reliable payer, fast turnaround."
        ),
        Customer(
            name="Rajesh Hardware",
            phone="+91 9848056789",
            aliases_json=json.dumps(["Rajesh", "Rajesh Hardware", "Rajesh bhai"]),
            outstanding_balance=8500.0,
            credit_limit=20000.0,
            credit_score=590,
            risk_tier="HIGH",
            last_payment_date=(datetime.now() - timedelta(days=48)).strftime("%Y-%m-%d"),
            notes="Overdue payment on construction material stock."
        ),
        Customer(
            name="Priya Medicals",
            phone="+91 9848067890",
            aliases_json=json.dumps(["Priya", "Priya Medicals", "Dr Priya"]),
            outstanding_balance=0.0,
            credit_limit=40000.0,
            credit_score=840,
            risk_tier="LOW",
            last_payment_date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            notes="Immediate UPI payer, all balances settled."
        )
    ]
    db.add_all(customers)
    db.commit()
    
    # 3. Create Suppliers
    suppliers = [
        Supplier(
            name="Sri Balaji Wholesale",
            phone="+91 9900112233",
            aliases_json=json.dumps(["Supplier", "Balaji Wholesale", "Sri Balaji", "Balaji"]),
            outstanding_balance=8000.0,
            last_payment_date=(datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            notes="Primary wholesale supplier for edible oil and sugar."
        ),
        Supplier(
            name="Deccan Distributors",
            phone="+91 9900223344",
            aliases_json=json.dumps(["Deccan", "Deccan Distributors"]),
            outstanding_balance=15000.0,
            last_payment_date=(datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
            notes="Packaged snacks and beverage distributor."
        ),
        Supplier(
            name="Hyderabad Grain Mills",
            phone="+91 9900334455",
            aliases_json=json.dumps(["Grain Mills", "Hyderabad Mills", "Mills"]),
            outstanding_balance=6500.0,
            last_payment_date=(datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"),
            notes="Atta, rava and maida supply partner."
        )
    ]
    db.add_all(suppliers)
    db.commit()
    
    # 4. Create Initial Transactions & Event Logs
    transactions = [
        Transaction(
            event_id="evt_seed_01",
            counterparty_type="customer",
            counterparty_id=customers[0].id,
            counterparty_name="Ramesh Kirana",
            transaction_type="CREDIT_SALE",
            direction="receivable",
            amount=5000.0,
            balance_after=5000.0,
            payment_method="credit",
            status="PAYMENT_DUE",
            date=(datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
            source_text="Ramesh ki 5000 saraku ichamu credit meeda",
            confidence=0.98
        ),
        Transaction(
            event_id="evt_seed_02",
            counterparty_type="customer",
            counterparty_id=customers[1].id,
            counterparty_name="Suresh Electricals",
            transaction_type="CREDIT_SALE",
            direction="receivable",
            amount=6000.0,
            balance_after=6000.0,
            payment_method="credit",
            status="PARTIAL_PAYMENT",
            date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            source_text="Suresh garu 6000 items teesukunnaru",
            confidence=0.96
        ),
        Transaction(
            event_id="evt_seed_03",
            counterparty_type="customer",
            counterparty_id=customers[1].id,
            counterparty_name="Suresh Electricals",
            transaction_type="PAYMENT_RECEIVED",
            direction="receivable",
            amount=2500.0,
            balance_after=3500.0,
            payment_method="upi",
            status="PARTIAL_PAYMENT",
            date=(datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"),
            source_text="Suresh ninna 2500 gpay chesadu",
            confidence=0.95
        ),
        Transaction(
            event_id="evt_seed_04",
            counterparty_type="supplier",
            counterparty_id=suppliers[0].id,
            counterparty_name="Sri Balaji Wholesale",
            transaction_type="PURCHASE",
            direction="payable",
            amount=12000.0,
            balance_after=12000.0,
            payment_method="credit",
            status="PAYMENT_DUE",
            date=(datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
            source_text="Balaji daggara 12000 stock konnam",
            confidence=0.95
        ),
        Transaction(
            event_id="evt_seed_05",
            counterparty_type="supplier",
            counterparty_id=suppliers[0].id,
            counterparty_name="Sri Balaji Wholesale",
            transaction_type="PAYMENT_MADE",
            direction="payable",
            amount=4000.0,
            balance_after=8000.0,
            payment_method="bank_transfer",
            status="PARTIAL_PAYMENT",
            date=(datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            source_text="Balaji ki 4000 transfer chesa",
            confidence=0.97
        )
    ]
    db.add_all(transactions)
    db.commit()
    
    # 5. Create Payment Commitments
    commitments = [
        PaymentCommitment(
            entity_type="customer",
            entity_id=customers[0].id,
            entity_name="Ramesh Kirana",
            amount=3000.0,
            due_date=(datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            status="PENDING",
            source_text="Ramesh Friday ki remaining 3000 istanu annadu"
        ),
        PaymentCommitment(
            entity_type="customer",
            entity_id=customers[1].id,
            entity_name="Suresh Electricals",
            amount=3500.0,
            due_date=(datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            status="PENDING",
            source_text="Suresh vache vaaram complete payment chestha annadu"
        ),
        PaymentCommitment(
            entity_type="supplier",
            entity_id=suppliers[0].id,
            entity_name="Sri Balaji Wholesale",
            amount=8000.0,
            due_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            status="PENDING",
            source_text="Balaji ki next Monday remaining 8000 ivvali"
        )
    ]
    db.add_all(commitments)
    db.commit()
    
    # 6. Add Unstructured Documents for RAG
    docs = [
        BusinessDocument(
            title="Store Credit & Payment Terms 2026",
            doc_type="CREDIT_POLICY",
            content="""
            Sri Lakshmi Kirana & General Stores Credit Policy:
            1. Standard credit limit is ₹25,000 for verified retail customers and ₹50,000 for wholesale partners.
            2. Payment due window is strictly 30 days from credit delivery.
            3. After 45 days of non-payment, an overdue surcharge of 2% per month is applied and credit is frozen.
            4. Immediate cash/UPI settlements on bulk orders over ₹10,000 receive an instant 2.5% discount.
            5. Payment commitments given in writing or voice notes are tracked with automated WhatsApp reminders 2 days prior to due date.
            """
        ),
        BusinessDocument(
            title="Invoice INV-2026-089 (Lakshmi Traders)",
            doc_type="INVOICE",
            content="""
            TAX INVOICE: INV-2026-089
            Date: 2026-08-20
            Billed To: Lakshmi Traders, Main Road, Guntur
            Items:
            - Premium Sona Masoori Rice (40 bags @ ₹2,200) = ₹88,000
            - Toor Dal Superfine (10 bags @ ₹3,200) = ₹32,000
            Total Bill: ₹1,20,000
            Advance Payment Received: ₹1,08,000 (via NEFT Bank Transfer)
            Balance Due: ₹12,000
            Payment Term: Net 30 Days.
            """
        ),
        BusinessDocument(
            title="Supplier Agreement: Sri Balaji Wholesale",
            doc_type="AGREEMENT",
            content="""
            SUPPLIER PURCHASE AGREEMENT - SRI BALAJI WHOLESALE
            Contract Terms:
            - Weekly order delivery on Mondays and Thursdays.
            - Credit ceiling: ₹20,000.
            - Settlement cycle: Fortnightly (every 15 days).
            - Preferred settlement mode: RTGS or UPI to Balaji Trade Account (SBIN0012345).
            - Returns accepted within 48 hours of damaged stock receipt.
            """
        )
    ]
    db.add_all(docs)
    db.commit()
    
    db.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
