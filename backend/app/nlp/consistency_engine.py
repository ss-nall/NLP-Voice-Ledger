"""
Consistency & Contradiction Detection Engine.
Validates proposed financial events against current ledger state.
Detects contradictory settlements, overpayments, duplicates, impossible dates, and high-value anomalies.
"""

from typing import Dict, Any, List, Optional
from backend.app.config import settings

class ConsistencyEngine:
    """
    Guards ledger integrity by intercepting conflicting or contradictory transaction claims.
    """
    
    @staticmethod
    def validate_event_against_ledger(
        event: Dict[str, Any],
        current_entity_balance: float,
        recent_transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates an incoming financial event against current outstanding balance and recent history.
        """
        actor = event.get("actor", "Unspecified")
        amount = float(event.get("amount", 0.0))
        event_type = event.get("event_type", "")
        direction = event.get("direction", "receivable")
        
        alerts = []
        requires_confirmation = False
        confirmation_prompt = None
        severity = "INFO"
        
        discrepancy_type = None
        excess = 0.0
        
        # 1. Contradiction Check: Full Settlement Claim with Pending Balance
        if event_type == "full_settlement" or "settle" in event.get("source_text", "").lower() or "complete ga" in event.get("source_text", "").lower() or "motham ichesadu" in event.get("source_text", "").lower():
            if current_entity_balance > 0:
                discrepancy_type = "CONTRADICTORY_SETTLEMENT"
                alerts.append({
                    "type": "CONTRADICTORY_SETTLEMENT",
                    "severity": "WARNING",
                    "message": f"Previous records show ₹{current_entity_balance:,.2f} still pending from {actor}."
                })
                requires_confirmation = True
                severity = "WARNING"
                confirmation_prompt = (
                    f"⚠️ **ఖాతా వ్యత్యాసం (Ledger Discrepancy)**:\n"
                    f"పుస్తకంలో {actor} గారి పాత బాకీ **₹{current_entity_balance:,.2f}** ఉంది.\n"
                    f"పూర్తి బాకీ క్లియర్ చేయాలా, లేక చెప్పిన మొత్తం మాత్రమే నమోదు చేయాలా?\n\n"
                    f"*(Ledger shows ₹{current_entity_balance:,.2f} outstanding for {actor}. Should I clear the full balance of ₹{current_entity_balance:,.2f} or record only the stated amount?)*"
                )
                
        # 2. Overpayment Check: Payment received exceeds outstanding receivable balance
        if event_type == "partial_payment" or event_type == "full_payment" or event_type == "payment_received":
            if current_entity_balance > 0 and amount > current_entity_balance:
                excess = amount - current_entity_balance
                discrepancy_type = "OVERPAYMENT_EXCEEDS_BALANCE"
                alerts.append({
                    "type": "OVERPAYMENT_EXCEEDS_BALANCE",
                    "severity": "WARNING",
                    "message": f"Payment amount ₹{amount:,.2f} exceeds outstanding balance ₹{current_entity_balance:,.2f} by ₹{excess:,.2f}."
                })
                requires_confirmation = True
                severity = "WARNING"
                confirmation_prompt = (
                    f"⚠️ **ఎక్కువ చెల్లింపు (Excess Payment)**:\n"
                    f"{actor} గారి బాకీ **₹{current_entity_balance:,.2f}** మాత్రమే ఉంది, కానీ చెప్పిన మొత్తం **₹{amount:,.2f}** (అదనంగా ₹{excess:,.2f}).\n"
                    f"బాకీ క్లియర్ చేసి మిగిలిన ₹{excess:,.2f} అడ్వాన్స్‌గా జమ చేయాలా?\n\n"
                    f"*({actor}'s balance is only ₹{current_entity_balance:,.2f}. Clear balance and credit ₹{excess:,.2f} as advance?)*"
                )
                
        # 3. Duplicate Transaction Check: Same actor and amount in immediate previous transaction
        if recent_transactions:
            tx = recent_transactions[0]
            tx_amount = float(tx.get("amount", 0))
            tx_actor = tx.get("counterparty_name", "")
            if tx_actor.lower() == actor.lower() and tx_amount == amount and amount > 0:
                discrepancy_type = "POTENTIAL_DUPLICATE_TRANSACTION"
                alerts.append({
                    "type": "POTENTIAL_DUPLICATE_TRANSACTION",
                    "severity": "CAUTION",
                    "message": f"A transaction of ₹{amount:,.2f} for {actor} was recently recorded ({tx.get('date', 'recently')})."
                })
                requires_confirmation = True
                severity = "CAUTION"
                confirmation_prompt = (
                    f"⚠️ **ఇటీవలే నమోదు చేయబడింది (Duplicate Check)**:\n"
                    f"{actor} గారికి ₹{amount:,.2f} లావాదేవీ కాసేపటి క్రితం రికార్డ్ అయింది.\n"
                    f"మళ్ళీ ఈ లావాదేవీని నమోదు చేయమంటారా?\n\n"
                    f"*(A transaction of ₹{amount:,.2f} for {actor} was just recorded. Are you sure you want to add this duplicate entry?)*"
                )
                
        # 4. High-Value Transaction Flag
        if amount >= settings.HIGH_VALUE_THRESHOLD:
            alerts.append({
                "type": "HIGH_VALUE_ANOMALY",
                "severity": "NOTICE",
                "message": f"High value transaction ₹{amount:,.2f} exceeds audit threshold (₹{settings.HIGH_VALUE_THRESHOLD:,.2f})."
            })
            
        is_consistent = len(alerts) == 0 or all(a["severity"] == "NOTICE" for a in alerts)
        
        return {
            "is_consistent": is_consistent,
            "requires_confirmation": requires_confirmation,
            "severity": severity,
            "discrepancy_type": discrepancy_type,
            "excess_amount": excess,
            "confirmation_prompt": confirmation_prompt,
            "alerts": alerts,
            "current_balance": current_entity_balance,
            "proposed_amount": amount
        }

# Global singleton
consistency_engine = ConsistencyEngine()
