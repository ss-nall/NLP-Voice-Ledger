"""
Semantic Text-to-Ledger Query Engine.
Parses complex, time-bounded, entity-specific, and aggregate financial inquiries
in both Telugu Script and Romanized Telugu / English.
"""

import re
from typing import Dict, Any, List, Optional

class SemanticQueryEngine:
    """
    Parses analytical questions into structured query execution plans.
    Guarantees transactions with explicit amounts/actors are never misclassified as queries.
    """

    def parse_query(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        
        # 1. Transaction guards: If sentence has booking verbs without question markers, it's not a query
        booking_keywords = ["ichadu", "ichanu", "ivvali", "ravali", "konna", "ammanu", "transfer", "paid", "received", "ఇచ్చాను", "ఇచ్చాడు", "ఇవ్వాలి", "రావాలి"]
        question_markers = ["evaru", "entha", "how much", "who", "show", "chupinchu", "summary", "list", "which", "ఎవరు", "ఎంత", "చూపించు", "జాబితా", "సారాంశం", "?"]
        
        has_question_marker = any(qm in text_lower for qm in question_markers)
        has_amount_digit = bool(re.search(r'\d+', text))
        
        # If it has an amount and a booking verb without an explicit question word, it's a booking transaction
        if has_amount_digit and any(bk in text_lower for bk in booking_keywords) and not has_question_marker:
            return {"is_query": False, "intent": "GENERAL_SEARCH", "filters": {}, "raw_query": text}

        # If it doesn't have question markers or inquiry words, it's not an analytical query
        if not has_question_marker and not any(kw in text_lower for kw in ["top debtor", "overdue", "highest due", "total receivable", "total payable", "motham raavali", "motham ivvali"]):
            return {"is_query": False, "intent": "GENERAL_SEARCH", "filters": {}, "raw_query": text}

        intent = "GENERAL_SEARCH"
        filters: Dict[str, Any] = {}
        target_entity: Optional[str] = None
        time_range: Optional[str] = None

        # Time range filters
        if "ఈ రోజు" in text or "today" in text_lower or "eroju" in text_lower:
            time_range = "TODAY"
        elif "నిన్న" in text or "yesterday" in text_lower or "ninna" in text_lower:
            time_range = "YESTERDAY"
        elif "ఈ వారం" in text or "this week" in text_lower or "ee varam" in text_lower:
            time_range = "THIS_WEEK"
        elif "ఈ నెల" in text or "this month" in text_lower or "ee nela" in text_lower:
            time_range = "THIS_MONTH"
        elif "గత నెల" in text or "last month" in text_lower or "gatha nela" in text_lower:
            time_range = "LAST_MONTH"

        # Intent classification
        if any(w in text_lower for w in ["who owes", "evaru ivvali", "evaru naaku", "ekkuva baaki", "top debtor", "highest due", "ఎవరు ఎక్కువ", "ఎవరు బాకీ", "ఎక్కువ బాకీ", "ఎవరు ఇవ్వాలి"]):
            intent = "TOP_DEBTORS"
        elif any(w in text_lower for w in ["total receivable", "raavalasina", "motham raavali", "total due to me", "మొత్తం రావాల్సిన", "రావాల్సిన బాకీలు", "రావలసిన"]):
            intent = "TOTAL_RECEIVABLES"
        elif any(w in text_lower for w in ["total payable", "ivvalasina", "motham ivvali", "total due to suppliers", "మొత్తం ఇవ్వాల్సిన", "ఇవ్వాల్సిన బాకీలు"]):
            intent = "TOTAL_PAYABLES"
        elif any(w in text_lower for w in ["overdue", "gaduvu datina", "pending", "late", "గడువు దాటిన"]):
            intent = "OVERDUE_BALANCES"
        elif any(w in text_lower for w in ["statement", "history", "khata", "vivaralu", "transactions", "chupinchu", "show me", "వివరాలు", "స్టేట్‌మెంట్"]):
            intent = "ENTITY_STATEMENT"
            words = text.split()
            if len(words) >= 2:
                cand = words[0]
                if cand.lower() not in ["show", "chupinchu", "evaru", "naaku", "what", "how", "చూపించు", "ఎవరు"]:
                    target_entity = cand

        if time_range:
            filters["time_range"] = time_range
        if target_entity:
            filters["target_entity"] = target_entity

        return {
            "is_query": intent != "GENERAL_SEARCH",
            "intent": intent,
            "filters": filters,
            "target_entity": target_entity,
            "time_range": time_range,
            "raw_query": text
        }

query_engine = SemanticQueryEngine()
