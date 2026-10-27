"""
Deterministic Natural Language Financial Query Parser.
Maps multi-lingual queries across Telugu, Tamil, Hindi, and English into structured SQL query plans.
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
        
        # 1. Intent: Top Debtors (Who owes me the most)
        if any(p in text_lower for p in [
            "ekkuva money ivvali", "ekkuva ivvali", "who owes me the most", "top debtors",
            "highest balance", "who owes most", "evaru naaku", "evaru baki unnaru",
            "ఎవరు ఎక్కువ ఇవ్వాలి", "ఎక్కువ బాకీ ఎవరు", "ఎవరు ఎక్కువ బాకీ",
            "yaar athigam tharanum", "yaarukku athiga baki", "yaar athiga panam tharanum", "athigam tharanum",
            "யார் அதிகம் தர வேண்டும்", "யாருக்கு அதிக பாக்கி",
            "sabse zyada kisse lena hai", "kisse sabse zyada baaki", "sabse jyada paise", "kisse lena hai sabse zyada",
            "सबसे ज्यादा किससे लेना है", "किसकी सबसे ज्यादा बाकी है", "सबसे बड़ा बकायेदार"
        ]):
            return {
                "intent": "TOP_DEBTORS",
                "target": "customers",
                "filter": {"min_balance": 1.0},
                "order_by": "outstanding_balance DESC",
                "limit": 5,
                "response_template": "Top customers with highest outstanding receivables"
            }
            
        # 2. Intent: Upcoming / Pending Payments
        if any(p in text_lower for p in [
            "ee week payments", "this week payments", "payments due", "due this friday",
            "upcoming payments", "repu payments", "friday payments", "commitments",
            "adutha vaaram payments", "naalai payments", "velli payments", "indha vaaram payments",
            "agle hafte ke payments", "aaj ke payments", "kal ke payments", "shukrawar ke payments",
            "రాబోయే చెల్లింపులు", "వచ్చే వారం చెల్లింపులు",
            "அடுத்த வாரம் பணம்", "நாளை கொடுப்பனவுகள்",
            "अगले हफ्ते के भुगतान", "कल के भुगतान", "आने वाले भुगतान"
        ]):
            timeframe = "this_week"
            day_target = None
            if any(k in text_lower for k in ["friday", "sukravaram", "శుక్రవారం", "velli", "வெள்ளி", "shukrawar", "शुक्रवार"]):
                day_target = "Friday"
            elif any(k in text_lower for k in ["repu", "tomorrow", "రేపు", "naalai", "நாளை", "kal", "कल"]):
                day_target = "Tomorrow"
                
            return {
                "intent": "UPCOMING_PAYMENTS",
                "target": "payment_commitments",
                "filter": {"status": "PENDING", "day_target": day_target, "timeframe": timeframe},
                "order_by": "due_date ASC",
                "limit": 10,
                "response_template": f"Upcoming payment commitments ({day_target if day_target else 'this week'})"
            }
            
        # 3. Intent: Total Payables (Suppliers ki entha ivvali / suppliers ko kitna dena hai)
        if any(p in text_lower for p in [
            "suppliers ki entha ivvali", "total payables", "nenu entha ivvali", "how much do i owe",
            "how much to pay", "payable total", "suppliers balance",
            "suppliers ku evalo tharanum", "mothama evalo kodukanum", "thara vendiya motham",
            "suppliers ko kitna dena hai", "kul kitna dena hai", "total kitna dena hai", "dena kitna hai",
            "ఎంత ఇవ్వాలి", "మొత్తం ఎంత ఇవ్వాలి", "ఇవ్వాల్సిన మొత్తం", "సప్లయర్ల బాకీ",
            "சப்ளையர்களுக்கு எவ்வளவு தர வேண்டும்", "மொத்தம் எவ்வளவு கொடுக்க வேண்டும்",
            "सप्लायर्स को कितना देना है", "कुल कितना देना है", "कितना चुकाना है"
        ]):
            return {
                "intent": "TOTAL_PAYABLES",
                "target": "suppliers",
                "aggregate": "SUM(outstanding_balance)",
                "response_template": "Total amount payable to suppliers"
            }
            
        # 4. Intent: Total Receivables (Customers nundi entha ravali / customers se kitna lena hai)
        if any(p in text_lower for p in [
            "total receivables", "entha ravali", "total pending", "how much is receivable",
            "customers nundi", "total baki", "customers balance",
            "customers kitterundhu evalo varanum", "mothama evalo varanum", "moththa baki",
            "customers se kitna lena hai", "kul kitna aana hai", "total kitna lena hai", "lena kitna hai",
            "ఎంత రావాలి", "మొత్తం ఎంత రావాలి", "రావాల్సిన మొత్తం", "కస్టమర్ల బాకీ", "బాకీ ఎంత",
            "கஸ்டமர்களிடம் எவ்வளவு வர வேண்டும்", "மொத்த பாக்கி எவ்வளவு",
            "कस्टमर्स से कितना लेना है", "कुल कितना बाकी है", "कितना लेना है"
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
            "kaalam kadandhadhu", "neram mudinjadhu", "late payment", "time nikal gaya",
            "గడువు దాటినవి", "ఆలస్యమైన చెల్లింపులు", "தாமதமான வாடிக்கையாளர்கள்", "अतिदेय ग्राहक", "डिफाल्टर"
        ]):
            return {
                "intent": "OVERDUE_CUSTOMERS",
                "target": "customers",
                "filter": {"is_overdue": True},
                "order_by": "days_overdue DESC",
                "limit": 10,
                "response_template": "Customers with overdue payment commitments"
            }
            
        # 6. Intent: Entity Payment History
        actor_match = re.search(r'\b(ramesh|suresh|mahesh|venkat|lakshmi|priya|rajesh|krishna|ravi|anand|kumar|kavitha|murugan|selvam|rahul|amit|vikram|రమేష్|సురేష్|ரமேஷ்|சுரேஷ்|ரமேஷ்|सुरेश|रमेश)\b', text_lower)
        if actor_match and any(p in text_lower for p in ["entha ichadu", "evalo koduthaar", "kitna diya", "how much paid", "payments", "history", "ichadu", "koduthaar", "diya"]):
            actor = actor_match.group(1).title()
            return {
                "intent": "ENTITY_HISTORY",
                "target": "transactions",
                "filter": {"actor_name": actor},
                "order_by": "transaction_date DESC",
                "limit": 10,
                "response_template": f"Payment and transaction history for {actor}"
            }
            
        # Default fallback
        return {
            "intent": "UNKNOWN",
            "target": None,
            "response_template": "Could not determine structured analytical query."
        }

# Global singleton
nl_query_parser = NLQueryParser()
