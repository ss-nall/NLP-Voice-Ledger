"""
Deterministic Natural Language Financial Query Parser.
Maps code-mixed and Telugu/English queries into structured query plans for deterministic SQL execution.
Zero LLM arithmetic hallucination.
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class NLQueryParser:
    """
    Parses conversational questions into deterministic database query plans.
    """
    
    @staticmethod
    def parse_query(query_text: str) -> Dict[str, Any]:
        text_lower = query_text.lower().strip()
        
        # 1. Intent: Top Debtors (Who owes me the most / Evaru ekkuva ivvali / ఎవరు ఎక్కువ ఇవ్వాలి)
        if any(p in text_lower for p in [
            "ekkuva money ivvali", "ekkuva ivvali", "who owes me the most", "top debtors",
            "highest balance", "who owes most", "evaru naaku", "evaru baki unnaru",
            "ఎవరు ఎక్కువ ఇవ్వాలి", "ఎక్కువ బాకీ ఎవరు", "ఎవరు ఎక్కువ బాకీ"
        ]):
            return {
                "intent": "TOP_DEBTORS",
                "target": "customers",
                "filter": {"min_balance": 1.0},
                "order_by": "outstanding_balance DESC",
                "limit": 5,
                "response_template": "Top customers with highest outstanding receivables"
            }
            
        # 2. Intent: Upcoming / Pending Payments for a specific day or week
        if any(p in text_lower for p in [
            "ee week payments", "this week payments", "payments due", "due this friday",
            "upcoming payments", "repu payments", "friday payments", "commitments",
            "రాబోయే చెల్లింపులు", "వచ్చే వారం చెల్లింపులు"
        ]):
            timeframe = "this_week"
            day_target = None
            if "friday" in text_lower or "sukravaram" in text_lower or "శుక్రవారం" in text_lower:
                day_target = "Friday"
            elif "repu" in text_lower or "tomorrow" in text_lower or "రేపు" in text_lower:
                day_target = "Tomorrow"
                
            return {
                "intent": "UPCOMING_PAYMENTS",
                "target": "payment_commitments",
                "filter": {"status": "PENDING", "day_target": day_target, "timeframe": timeframe},
                "order_by": "due_date ASC",
                "limit": 10,
                "response_template": f"Upcoming payment commitments ({day_target if day_target else 'this week'})"
            }
            
        # 3. Intent: Total Payables (Suppliers ki entha ivvali / ఎంత ఇవ్వాలి)
        if any(p in text_lower for p in [
            "suppliers ki entha ivvali", "total payables", "nenu entha ivvali", "how much do i owe",
            "how much to pay", "payable total", "suppliers balance",
            "ఎంత ఇవ్వాలి", "మొత్తం ఎంత ఇవ్వాలి", "ఇవ్వాల్సిన మొత్తం", "సప్లయర్ల బాకీ"
        ]):
            return {
                "intent": "TOTAL_PAYABLES",
                "target": "suppliers",
                "aggregate": "SUM(outstanding_balance)",
                "response_template": "Total amount payable to suppliers"
            }
            
        # 4. Intent: Total Receivables (Customers nundi entha ravali / ఎంత రావాలి)
        if any(p in text_lower for p in [
            "total receivables", "entha ravali", "total pending", "how much is receivable",
            "customers nundi", "total baki", "customers balance",
            "ఎంత రావాలి", "మొత్తం ఎంత రావాలి", "రావాల్సిన మొత్తం", "కస్టమర్ల బాకీ", "బాకీ ఎంత"
        ]):
            return {
                "intent": "TOTAL_RECEIVABLES",
                "target": "customers",
                "aggregate": "SUM(outstanding_balance)",
                "response_template": "Total amount receivable from customers"
            }
            
        # 5. Intent: Overdue Customers
        if any(p in text_lower for p in [
            "overdue", "late payers", "time aipoindi", "defaulters", "overdue payments", "date daatipoindi",
            "గడువు దాటినవి", "ఆలస్యమైన చెల్లింపులు"
        ]):
            return {
                "intent": "OVERDUE_CUSTOMERS",
                "target": "customers",
                "filter": {"is_overdue": True},
                "order_by": "days_overdue DESC",
                "limit": 10,
                "response_template": "Customers with overdue payment commitments"
            }
            
        # 6. Intent: Entity Payment History (e.g. Ramesh entha ichadu)
        actor_match = re.search(r'\b(ramesh|suresh|mahesh|venkat|lakshmi|priya|rajesh|krishna|ravi|anand|రమేష్|సురేష్|మహేష్|వెంకట్|లక్ష్మి|ప్రియ|రాజేష్|కృష్ణ|రవి|ఆనంద్)\b', text_lower)
        if actor_match and any(p in text_lower for p in ["entha ichadu", "how much paid", "payments", "history", "ichadu", "ఎంత ఇచ్చాడు", "చెల్లింపులు"]):
            actor = actor_match.group(1).title()
            return {
                "intent": "ENTITY_PAYMENT_HISTORY",
                "target": "transactions",
                "filter": {"actor": actor, "type": "PAYMENT_RECEIVED"},
                "aggregate": "SUM(amount)",
                "timeframe": "last_90_days" if "3 months" in text_lower or "last 3 months" in text_lower else "all_time",
                "response_template": f"Total payments received from {actor}"
            }
            
        # 7. Intent: Cash Flow Summary
        if any(p in text_lower for p in [
            "cash flow", "cashflow", "inflow", "outflow", "jama kharchu", "summary",
            "నగదు ప్రవాహం", "లెక్కల సారాంశం", "జమా ఖర్చు"
        ]):
            return {
                "intent": "CASH_FLOW_SUMMARY",
                "target": "analytics",
                "timeframe": "last_30_days",
                "response_template": "30-day cash flow summary and projection"
            }
            
        # Default General Search
        return {
            "intent": "GENERAL_SEARCH",
            "target": "ledger",
            "query_text": query_text,
            "response_template": f"Search results for '{query_text}'"
        }

# Global singleton
nl_query_parser = NLQueryParser()
