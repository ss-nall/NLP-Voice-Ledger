"""
Multi-Lingual Financial Event Extraction & Representation Module.
Assembles raw NLP features into an auditable, standardized FinancialEvent schema.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class FinancialEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    event_type: str
    actor: str
    counterparty: str = "Business"
    amount: float
    currency: str = "INR"
    direction: str  # 'receivable' or 'payable'
    payment_method: Optional[str] = "cash"
    event_date: str
    due_date: Optional[str] = None
    source_text: str
    confidence: float
    explanation: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FinancialEventBuilder:
    """
    Constructs a valid FinancialEvent from extracted linguistic components.
    """
    
    @staticmethod
    def build_event(
        raw_text: str,
        entities: Dict[str, Any],
        relation: Dict[str, Any],
        temporal_info: List[Dict[str, Any]],
        lang_info: Dict[str, Any]
    ) -> FinancialEvent:
        # Determine actor
        actors = entities.get("actors", [])
        actor_name = relation.get("actor", "Unspecified")
        if actor_name == "Unspecified" and actors:
            actor_name = actors[0]["name"]
            
        # Determine amount
        amounts = entities.get("amounts", [])
        amount_val = amounts[0]["value"] if amounts else 0.0
        currency = amounts[0]["currency"] if amounts else "INR"
        
        # Determine payment method
        payment_methods = entities.get("payment_methods", [])
        payment_method = payment_methods[0]["method"] if payment_methods else "cash"
        
        # Determine dates
        now_str = datetime.now().strftime("%Y-%m-%d")
        event_date = now_str
        due_date = None
        
        for t in temporal_info:
            if t.get("temporal_role") == "DUE_DATE":
                due_date = t["normalized_date"]
            elif t.get("temporal_role") == "EVENT_DATE":
                event_date = t["normalized_date"]
                
        # Determine event type
        rel_type = relation.get("relation_type", "GENERAL_TRANSACTION")
        direction = relation.get("direction", "receivable")
        
        if rel_type == "PROMISED_TO_PAY":
            event_type = "payment_commitment"
            if not due_date:
                due_date = (datetime.now()).strftime("%Y-%m-%d")
        elif rel_type in ["PAYMENT_RECEIVED", "PAID"]:
            if direction == "payable":
                event_type = "payment_made"
            else:
                event_type = "partial_payment"
        elif rel_type == "PAYMENT_MADE":
            event_type = "payment_made"
        elif rel_type == "SETTLED":
            event_type = "full_settlement"
        elif rel_type in ["ADVANCE", "ADVANCE_PAID_BY_BUSINESS", "ADVANCE_RECEIVED"]:
            event_type = "advance_payment"
        elif rel_type == "CREDIT_SALE":
            event_type = "credit_sale"
        elif rel_type == "PURCHASE":
            event_type = "purchase"
        elif rel_type in ["PAYABLE", "OWES"] and direction == "payable":
            event_type = "payable_obligation"
        elif rel_type in ["RECEIVABLE", "OWES"] and direction == "receivable":
            event_type = "receivable_invoice"
        else:
            event_type = "general_entry"
            
        # Overall confidence calculation
        ent_conf = amounts[0]["confidence"] if amounts else 0.8
        rel_conf = relation.get("confidence", 0.85)
        lang_conf = lang_info.get("confidence", 0.9)
        overall_confidence = round((ent_conf * 0.4 + rel_conf * 0.4 + lang_conf * 0.2), 2)
        
        # Collect temporal spans & invoice metadata
        temp_spans = [t["raw_span"] for t in temporal_info]
        inv_list = [i["invoice_number"] for i in entities.get("invoices", [])]
        
        primary_lang = lang_info.get("primary_language", "english")
        is_mixed = lang_info.get("is_code_mixed", False)
        
        explanation = relation.get("explanation", f"Recorded financial event for {actor_name}.")
        
        return FinancialEvent(
            event_type=event_type,
            actor=actor_name,
            counterparty="Business",
            amount=float(amount_val),
            currency=currency,
            direction=direction,
            payment_method=payment_method,
            event_date=event_date,
            due_date=due_date,
            source_text=raw_text,
            confidence=overall_confidence,
            explanation=explanation,
            metadata={
                "language": primary_lang,
                "is_code_mixed": is_mixed,
                "temporal_spans": temp_spans,
                "invoices": inv_list
            }
        )

# Global singleton
event_builder = FinancialEventBuilder()
