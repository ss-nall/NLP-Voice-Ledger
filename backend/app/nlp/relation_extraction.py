"""
Financial Relation & Direction Extraction Module.
Resolves transaction direction, semantic participant roles (PAYABLE vs RECEIVABLE),
and financial action relations (OWES, PAID, PROMISED_TO_PAY, ADVANCE, CREDIT_SALE, SETTLED).
"""

import re
from typing import Dict, Any, List, Optional
from backend.app.nlp.telugu_lexicon import DIRECTION_MARKERS

class FinancialRelationExtractor:
    """
    Determines the financial relationship, flow direction, and semantic roles
    from code-mixed and Telugu grammatical cues.
    """
    
    @staticmethod
    def extract_relation(text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        text_lower = text.lower()
        actors = entities.get("actors", [])
        actor_name = actors[0]["name"] if actors else "Unspecified"
        actor_type = actors[0]["type"] if actors else "PERSON"
        
        # Helper regex matcher
        def matches_any(keywords: List[str]) -> bool:
            for kw in keywords:
                if re.search(r'(?:^|\s+)' + re.escape(kw) + r'(?:\s+|$|[.,!?])', text_lower):
                    return True
            return False

        # Business Recipient Pronouns: "నాకు", "మాకు", "naaku", "naku", "maaku", "maku", "to me", "to us", "for me", "for us"
        has_business_recipient = bool(
            re.search(r'(?:^|\s+)(?:naaku|naku|maaku|maku|to me|to us|for me|for us|నాకు|మాకు)(?:\s+|$|[.,!?])', text_lower)
        )

        # Counterparty Dative marker (must not match temporal datives like 'next week ki', 'repu ki')
        temporal_ki_words = {
            "week", "vaaram", "varam", "month", "nela", "year",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "somavaram", "mangalavaram", "budhavaram", "guruvaram", "sukravaram", "sanivaram", "aadivaram",
            "repu", "ninna", "ellundi", "eroju", "today", "tomorrow", "sayantram", "udayam", "madyanam"
        }
        dative_match = re.search(r'(?:^|\s+)([a-zA-Z\u0C00-\u0C7F]+)\s*(?:gariki|annaki|bhaiki|sethki|ki|ku|గారికి|అన్నకి|కి|కు)(?:\s+|$|[.,!?])', text_lower)
        dative_word = dative_match.group(1).lower() if dative_match else ""
        has_counterparty_dative = bool(dative_match and dative_word not in temporal_ki_words and not has_business_recipient)
        has_dative_ki = (
            has_counterparty_dative
            or "paid to " in text_lower or "pay to " in text_lower or "due to " in text_lower or "payable to " in text_lower
        )
        
        # Ablative marker (From Customer): "nundi", "nunchi", "నుండి", "నుంచి", "from"
        has_ablative_nundi = (
            any(re.search(r'(?:^|\s+)' + re.escape(p) + r'(?:\s+|$|[.,!?])', text_lower) for p in DIRECTION_MARKERS["RECEIVABLE_POSTPOSITIONS"])
            or "from " in text_lower or text_lower.startswith("from ") or "due from " in text_lower or "received from " in text_lower or "collected from " in text_lower or "got from " in text_lower
        )

        # Verb Tense & Direction Classifications
        is_biz_paid = matches_any(DIRECTION_MARKERS["PAID_BY_BUSINESS_VERBS"])
        is_cust_paid = matches_any(DIRECTION_MARKERS["PAID_BY_CUSTOMER_VERBS"])
        has_payable_verb = matches_any(DIRECTION_MARKERS["PAYABLE_VERBS"])
        has_receivable_verb = matches_any(DIRECTION_MARKERS["RECEIVABLE_VERBS"])
        is_promise = any(v in text_lower for v in DIRECTION_MARKERS["PROMISE_VERBS"]) or ("annadu" in text_lower and ("istanu" in text_lower or "istha" in text_lower or "isthanu" in text_lower))
        is_settled = any(v in text_lower for v in DIRECTION_MARKERS["SETTLEMENT_VERBS"]) or ("mottham" in text_lower and "iches" in text_lower) or ("motham" in text_lower and "iches" in text_lower)
        is_advance = any(v in text_lower for v in DIRECTION_MARKERS["ADVANCE_VERBS"])
        
        # 1. Check Trade items (Credit sale vs Purchase)
        is_sale_trade = any(kw in text_lower for kw in [
            "goods icha", "goods ichamu", "saraku icha", "saraku ichamu", "saraku ammanu", "saraku ammamu",
            "ammanu", "ammamu", "ammadu", "credit meeda", "udhari icha", "credit sale", "sold",
            "సరుకు ఇచ్చా", "సరుకు అమ్మా", "అమ్మాను", "అమ్మాము", "అమ్మాడు", "అమ్మిన", "సేల్", "క్రెడిట్ సేల్"
        ])
        if is_sale_trade:
            return {
                "relation_type": "CREDIT_SALE",
                "direction": "receivable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.94,
                "explanation": f"Credit sale of goods provided to {actor_name}."
            }
            
        is_purchase_trade = any(kw in text_lower for kw in [
            "saraku konna", "konnanu", "konnamu", "konnadu", "stock theppincham", "purchase", "maal konnam",
            "సరుకు కొన్నా", "కొన్నాను", "కొన్నాము", "కొన్నాడు", "కొన్నాం", "కొన్న", "పర్చేస్"
        ])
        if is_purchase_trade:
            return {
                "relation_type": "PURCHASE",
                "direction": "payable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.94,
                "explanation": f"Stock purchase from {actor_name}."
            }

        # 2. Check Promise to Pay (e.g. 'Ramesh repu isthanu annadu', 'రమేష్ రేపు ఇస్తానన్నాడు')
        if is_promise:
            direction = "payable" if has_dative_ki and ("we" in text_lower or "nenu" in text_lower or "memu" in text_lower) else "receivable"
            return {
                "relation_type": "PROMISED_TO_PAY",
                "direction": direction,
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.96,
                "explanation": f"{actor_name} payment commitment recorded."
            }
            
        # 3. Check Full Settlement Claim (e.g. 'Ramesh mottham ichesadu', 'రమేష్ మొత్తం ఇచ్చేశాడు')
        if is_settled:
            direction = "payable" if has_dative_ki and (is_biz_paid or "nenu" in text_lower or "memu" in text_lower) else "receivable"
            return {
                "relation_type": "SETTLED",
                "direction": direction,
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.95,
                "explanation": f"Full settlement recorded for {actor_name}."
            }
            
        # 4. Check Advance Payment
        if is_advance:
            if is_biz_paid or (has_dative_ki and not is_cust_paid and not has_business_recipient):
                return {
                    "relation_type": "ADVANCE_PAID_BY_BUSINESS",
                    "direction": "payable",
                    "actor": actor_name,
                    "counterparty": "Business",
                    "confidence": 0.94,
                    "explanation": f"Business paid advance to {actor_name}."
                }
            else:
                return {
                    "relation_type": "ADVANCE_RECEIVED",
                    "direction": "receivable",
                    "actor": actor_name,
                    "counterparty": "Business",
                    "confidence": 0.94,
                    "explanation": f"Advance received from {actor_name}."
                }
                
        # 5. Check Payment Made by Business (1st person past / Outflow to Supplier / Outflow)
        # e.g. 'Ramesh ki 500 ichesanu', '500 ichesa', 'రమేష్ కి 500 ఇచ్చేశాను', 'రమేష్ కి 500 కట్టేసా', 'paid 500 to ramesh', 'transferred 500 to ramesh'
        if is_biz_paid or (has_dative_ki and not is_cust_paid and not has_business_recipient and not has_receivable_verb and not has_payable_verb):
            return {
                "relation_type": "PAYMENT_MADE",
                "direction": "payable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.96,
                "explanation": f"Business made payment to {actor_name} (reducing payable balance)."
            }

        # 6. Check Payment Received from Customer (3rd person past / Inflow from Customer)
        # e.g. 'Ramesh 500 ichadu', 'రమేష్ 500 ఇచ్చాడు', 'రమేష్ నాకు 500 ఇచ్చాడు', 'రమేష్ నుంచి 500 వచ్చింది', 'Ramesh nundi 500 vachindi', 'రమేష్ 500 కట్టాడు', 'received 1000 from kiran'
        if (is_cust_paid
            or (has_business_recipient and ("ichadu" in text_lower or "kattadu" in text_lower or "paid" in text_lower or "icheysadu" in text_lower or "ichindi" in text_lower))
            or (has_ablative_nundi and not has_receivable_verb and not has_payable_verb)
            or text_lower.startswith("received ") or text_lower.startswith("collected ") or text_lower.startswith("got ")):
            return {
                "relation_type": "PAYMENT_RECEIVED",
                "direction": "receivable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.96,
                "explanation": f"{actor_name} paid amount to Business (reducing receivable balance & cash inflow)."
            }

        # 7. Check Payable Obligation (Modal / Future obligation to pay Supplier)
        # e.g. 'Ramesh ki 1000 kattali', 'రమేష్ కి 1000 కట్టాలి', 'Supplier ki 5000 ivvali', 'need to pay 1000 to ramesh'
        has_supplier_keyword = any(k in text_lower for k in ["supplier", "dealer", "vendor", "distributor", "wholesaler", "mills", "hardware", "agency", "traders", "సప్లయర్", "డీలర్"])
        has_customer_keyword = any(k in text_lower for k in ["customer", "client", "buyer", "కస్టమర్", "క్లయింట్"])

        if ((has_dative_ki and has_payable_verb and not has_business_recipient)
            or (has_payable_verb and has_supplier_keyword)
            or "need to pay" in text_lower or "have to pay" in text_lower or "payable to" in text_lower or "owe to" in text_lower):
            return {
                "relation_type": "PAYABLE",
                "direction": "payable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.96,
                "explanation": f"Business owes amount to {actor_name} (Payable obligation)."
            }

        # 8. Check Receivable Asset / Invoice (Customer owes Business / Pending / Dues)
        # e.g. 'Ramesh nundi 1000 ravali', 'రమేష్ నుండి 1000 రావాలి', 'రమేష్ 2000 బాకీ ఉన్నాడు', 'kiran 2000 baki', 'pending from ramesh', 'రమేష్ 1000 ఇవ్వాలి నాకు', 'Customer aidhu vandalu ivvali'
        if (has_ablative_nundi
            or has_receivable_verb
            or "pending" in text_lower
            or "baki" in text_lower
            or "baaki" in text_lower
            or "due from" in text_lower
            or "receivable from" in text_lower
            or (has_business_recipient and has_payable_verb)
            or (has_customer_keyword and has_payable_verb)):
            return {
                "relation_type": "RECEIVABLE",
                "direction": "receivable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.95,
                "explanation": f"{actor_name} owes amount to Business (Receivable asset)."
            }

        # 9. Standalone Payable Verb without 'ki' (e.g. 'Supplier 1000 kattali', '5000 kattali')
        if has_payable_verb and not has_business_recipient:
            direction = "receivable" if has_customer_keyword else "payable"
            rel_type = "RECEIVABLE" if has_customer_keyword else "PAYABLE"
            return {
                "relation_type": rel_type,
                "direction": direction,
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.92,
                "explanation": f"Recorded {direction} transaction for {actor_name}."
            }

        # Default fallback
        return {
            "relation_type": "GENERAL_TRANSACTION",
            "direction": "receivable",
            "actor": actor_name,
            "counterparty": "Business",
            "confidence": 0.75,
            "explanation": f"Financial interaction involving {actor_name}."
        }

# Global singleton
relation_extractor = FinancialRelationExtractor()

