"""
Financial Analytics & Predictive Intelligence Service.
Computes deterministic KPIs, aging buckets, cash flow projections,
customer risk scoring, and ledger insights across all 8 languages.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database.models import (
    Customer, Supplier, Transaction, PaymentCommitment
)

class AnalyticsService:
    """
    Computes business intelligence directly from the database (No LLM math hallucination).
    """
    
    @staticmethod
    def get_overview(db: Session) -> Dict[str, Any]:
        total_receivables = db.query(func.sum(Customer.outstanding_balance)).scalar() or 0.0
        total_payables = db.query(func.sum(Supplier.outstanding_balance)).scalar() or 0.0
        
        now = datetime.now()
        first_of_month = now.replace(day=1).strftime("%Y-%m-%d")
        
        inflow = db.query(func.sum(Transaction.amount)).filter(
            Transaction.direction == "receivable",
            Transaction.transaction_type == "PAYMENT_RECEIVED",
            Transaction.date >= first_of_month
        ).scalar() or 0.0
        
        outflow = db.query(func.sum(Transaction.amount)).filter(
            Transaction.direction == "payable",
            Transaction.transaction_type == "PAYMENT_MADE",
            Transaction.date >= first_of_month
        ).scalar() or 0.0
        
        today_str = now.strftime("%Y-%m-%d")
        overdue_amount = db.query(func.sum(PaymentCommitment.amount)).filter(
            PaymentCommitment.due_date < today_str,
            PaymentCommitment.status == "PENDING"
        ).scalar() or 0.0
        
        customer_count = db.query(Customer).count()
        supplier_count = db.query(Supplier).count()
        pending_commitments_count = db.query(PaymentCommitment).filter(PaymentCommitment.status == "PENDING").count()
        
        return {
            "total_receivables": round(total_receivables, 2),
            "total_payables": round(total_payables, 2),
            "net_position": round(total_receivables - total_payables, 2),
            "monthly_inflow": round(inflow, 2),
            "monthly_outflow": round(outflow, 2),
            "overdue_amount": round(overdue_amount, 2),
            "customer_count": customer_count,
            "supplier_count": supplier_count,
            "pending_commitments_count": pending_commitments_count
        }

    @staticmethod
    def get_total_receivables(db: Session) -> float:
        return db.query(func.sum(Customer.outstanding_balance)).scalar() or 0.0

    @staticmethod
    def get_total_payables(db: Session) -> float:
        return db.query(func.sum(Supplier.outstanding_balance)).scalar() or 0.0

    @staticmethod
    def get_top_debtors(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        customers = db.query(Customer).filter(Customer.outstanding_balance > 0).order_by(Customer.outstanding_balance.desc()).limit(limit).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "name_telugu": getattr(c, 'name_telugu', c.name),
                "outstanding_balance": c.outstanding_balance,
                "credit_score": c.credit_score,
                "risk_tier": c.risk_tier,
                "phone": c.phone,
                "last_payment_date": c.last_payment_date
            }
            for c in customers
        ]

    @staticmethod
    def get_highest_outflow(db: Session, time_range: str = "THIS_MONTH") -> Dict[str, Any]:
        """Calculates who the business paid the most to during the given period."""
        now = datetime.now()
        start_date = now.replace(day=1).strftime("%Y-%m-%d")
        if time_range == "TODAY":
            start_date = now.strftime("%Y-%m-%d")
        elif time_range == "THIS_WEEK":
            start_date = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        elif time_range == "LAST_MONTH":
            first_this_month = now.replace(day=1)
            last_month_end = first_this_month - timedelta(days=1)
            start_date = last_month_end.replace(day=1).strftime("%Y-%m-%d")

        query = db.query(
            Transaction.counterparty_name,
            func.sum(Transaction.amount).label("total_paid")
        ).filter(
            Transaction.direction == "payable",
            Transaction.transaction_type.in_(["PAYMENT_MADE", "PURCHASE", "DEBIT"]),
            Transaction.date >= start_date
        ).group_by(Transaction.counterparty_name).order_by(func.sum(Transaction.amount).desc()).first()

        if query:
            return {"entity_name": query[0], "total_amount": float(query[1]), "time_range": time_range}
        return {"entity_name": None, "total_amount": 0.0, "time_range": time_range}

    @staticmethod
    def get_last_payment_date(db: Session, entity_name: str) -> Dict[str, Any]:
        """Finds the most recent payment transaction date and amount for a specific entity."""
        from backend.app.nlp.indic_phonetics import indic_phonetic_matcher
        txs = db.query(Transaction).filter(
            Transaction.transaction_type.in_(["PAYMENT_RECEIVED", "PAYMENT_MADE", "SETTLEMENT"])
        ).order_by(Transaction.date.desc(), Transaction.id.desc()).all()

        for t in txs:
            if indic_phonetic_matcher.match_score(entity_name, t.counterparty_name) > 0.75:
                return {
                    "entity_name": t.counterparty_name,
                    "date": t.date,
                    "amount": t.amount,
                    "direction": t.direction,
                    "type": t.transaction_type
                }
        return {"entity_name": entity_name, "date": None, "amount": 0.0}

    @staticmethod
    def get_weekly_receivables(db: Session) -> Dict[str, Any]:
        """Retrieves total dues / commitments scheduled to be collected this week."""
        now = datetime.now()
        start_of_week = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        end_of_week = (now + timedelta(days=6 - now.weekday())).strftime("%Y-%m-%d")

        commitments = db.query(PaymentCommitment).filter(
            PaymentCommitment.entity_type == "customer",
            PaymentCommitment.due_date >= start_of_week,
            PaymentCommitment.due_date <= end_of_week,
            PaymentCommitment.status == "PENDING"
        ).all()

        total_due = sum(c.amount for c in commitments)
        items = [{"name": c.entity_name, "amount": c.amount, "due_date": c.due_date} for c in commitments]

        # If no explicit commitments, fallback to active customer balances
        if not items:
            active_custs = db.query(Customer).filter(Customer.outstanding_balance > 0).limit(5).all()
            total_due = sum(c.outstanding_balance for c in active_custs)
            items = [{"name": c.name, "amount": c.outstanding_balance, "due_date": "This Week"} for c in active_custs]

        return {"total_weekly_receivables": total_due, "items": items}

    @staticmethod
    def get_today_cashflow(db: Session) -> Dict[str, Any]:
        """Returns today's total collections (inflow) and payouts (outflow)."""
        today_str = datetime.now().strftime("%Y-%m-%d")

        inflow = db.query(func.sum(Transaction.amount)).filter(
            Transaction.direction == "receivable",
            Transaction.transaction_type.in_(["PAYMENT_RECEIVED", "CREDIT_SALE"]),
            Transaction.date == today_str
        ).scalar() or 0.0

        outflow = db.query(func.sum(Transaction.amount)).filter(
            Transaction.direction == "payable",
            Transaction.transaction_type.in_(["PAYMENT_MADE", "PURCHASE"]),
            Transaction.date == today_str
        ).scalar() or 0.0

        return {
            "date": today_str,
            "today_collections": float(inflow),
            "today_payouts": float(outflow),
            "net_flow": float(inflow - outflow)
        }

    @staticmethod
    def get_cash_flow_summary(db: Session) -> Dict[str, Any]:
        now = datetime.now()
        first_of_month = now.replace(day=1).strftime("%Y-%m-%d")
        
        inflow = db.query(func.sum(Transaction.amount)).filter(
            Transaction.direction == "receivable",
            Transaction.transaction_type == "PAYMENT_RECEIVED",
            Transaction.date >= first_of_month
        ).scalar() or 0.0
        
        outflow = db.query(func.sum(Transaction.amount)).filter(
            Transaction.direction == "payable",
            Transaction.transaction_type == "PAYMENT_MADE",
            Transaction.date >= first_of_month
        ).scalar() or 0.0

        return {
            "total_inflow": float(inflow),
            "total_outflow": float(outflow),
            "net_cash_position": float(inflow - outflow)
        }

    @staticmethod
    def get_aging_analysis(db: Session) -> Dict[str, Any]:
        customers = db.query(Customer).filter(Customer.outstanding_balance > 0).all()
        now = datetime.now()
        
        buckets = {
            "current_0_30": {"amount": 0.0, "count": 0, "customers": []},
            "overdue_31_60": {"amount": 0.0, "count": 0, "customers": []},
            "overdue_61_90": {"amount": 0.0, "count": 0, "customers": []},
            "critical_90_plus": {"amount": 0.0, "count": 0, "customers": []}
        }
        
        for c in customers:
            days = 15
            if c.last_payment_date:
                try:
                    lp_date = datetime.strptime(c.last_payment_date, "%Y-%m-%d")
                    days = (now - lp_date).days
                except Exception:
                    days = 15
                    
            c_info = {"id": c.id, "name": c.name, "balance": c.outstanding_balance, "days": days}
            if days <= 30:
                buckets["current_0_30"]["amount"] += c.outstanding_balance
                buckets["current_0_30"]["count"] += 1
                buckets["current_0_30"]["customers"].append(c_info)
            elif days <= 60:
                buckets["overdue_31_60"]["amount"] += c.outstanding_balance
                buckets["overdue_31_60"]["count"] += 1
                buckets["overdue_31_60"]["customers"].append(c_info)
            elif days <= 90:
                buckets["overdue_61_90"]["amount"] += c.outstanding_balance
                buckets["overdue_61_90"]["count"] += 1
                buckets["overdue_61_90"]["customers"].append(c_info)
            else:
                buckets["critical_90_plus"]["amount"] += c.outstanding_balance
                buckets["critical_90_plus"]["count"] += 1
                buckets["critical_90_plus"]["customers"].append(c_info)
                
        return buckets

    @staticmethod
    def get_cash_flow_forecast(db: Session, days_ahead: int = 30) -> List[Dict[str, Any]]:
        now = datetime.now()
        forecast = []
        commitments = db.query(PaymentCommitment).filter(PaymentCommitment.status == "PENDING").all()
        
        for d in range(days_ahead):
            target_date = now + timedelta(days=d)
            target_date_str = target_date.strftime("%Y-%m-%d")
            
            day_inflow = sum(c.amount for c in commitments if c.due_date == target_date_str and c.entity_type == "customer")
            day_outflow = sum(c.amount for c in commitments if c.due_date == target_date_str and c.entity_type == "supplier")
            
            forecast.append({
                "date": target_date_str,
                "day_name": target_date.strftime("%a"),
                "projected_inflow": day_inflow,
                "projected_outflow": day_outflow,
                "net": day_inflow - day_outflow
            })
            
        return forecast

    @staticmethod
    def get_reminders(db: Session) -> List[Dict[str, Any]]:
        import urllib.parse
        now = datetime.now()
        today_date = now.date()
        
        commitments = db.query(PaymentCommitment).order_by(PaymentCommitment.due_date.asc()).all()
        results = []
        
        month_names_te = {
            1: "జనవరి", 2: "ఫిబ్రవరి", 3: "మార్చి", 4: "ఏప్రిల్", 5: "మే", 6: "జూన్",
            7: "జూలై", 8: "ఆగస్టు", 9: "సెప్టెంబర్", 10: "అక్టోబర్", 11: "నవంబర్", 12: "డిసెంబర్"
        }
        
        for c in commitments:
            days_diff = 0
            formatted_date_te = c.due_date
            try:
                dt = datetime.strptime(c.due_date, "%Y-%m-%d").date()
                days_diff = (dt - today_date).days
                m_te = month_names_te.get(dt.month, str(dt.month))
                formatted_date_te = f"{dt.day} {m_te} {dt.year}"
            except Exception:
                pass
                
            if days_diff < 0:
                urgency = "OVERDUE"
                badge_te = f"గడువు దాటింది ({abs(days_diff)} రోజులు)"
                badge_en = f"Overdue by {abs(days_diff)} days"
            elif days_diff == 0:
                urgency = "TODAY"
                badge_te = "ఈ రోజే గడువు"
                badge_en = "Due Today"
            elif days_diff == 1:
                urgency = "TOMORROW"
                badge_te = "రేపు గడువు"
                badge_en = "Due Tomorrow"
            else:
                urgency = "UPCOMING"
                badge_te = f"{days_diff} రోజుల్లో"
                badge_en = f"In {days_diff} days"
                
            if c.entity_type == "customer":
                wa_text = (
                    f"నమస్కారం {c.entity_name} గారు,\n"
                    f"మీ వ్యాపార ఖాతా ప్రకారం ₹{c.amount:,.2f} బాకీ {formatted_date_te} నాటికి చెల్లించవలసి ఉంది.\n"
                    f"దయచేసి సమయానికి చెల్లించి సహకరించగలరు. ధన్యవాదాలు! 🙏"
                )
            else:
                wa_text = (
                    f"నమస్కారం {c.entity_name} గారు,\n"
                    f"మీకు చెల్లించవలసిన మొత్తం ₹{c.amount:,.2f} {formatted_date_te} నాటికి సిద్ధం చేసి చెల్లిస్తాము.\n"
                    f"ధన్యవాదాలు! 🙏"
                )
                
            encoded_wa = urllib.parse.quote(wa_text)
            wa_link = f"https://wa.me/?text={encoded_wa}"
            
            results.append({
                "id": c.id,
                "entity_name": c.entity_name,
                "entity_type": c.entity_type,
                "amount": c.amount,
                "due_date": c.due_date,
                "formatted_date_te": formatted_date_te,
                "days_remaining": days_diff,
                "urgency": urgency,
                "badge_te": badge_te,
                "badge_en": badge_en,
                "status": c.status,
                "source_text": c.source_text,
                "whatsapp_message": wa_text,
                "whatsapp_link": wa_link,
                "created_at": c.created_at.isoformat() if c.created_at else ""
            })
            
        return results

analytics_service = AnalyticsService()
