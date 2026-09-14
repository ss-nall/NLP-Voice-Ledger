"""
Conversational Voice & Text Interaction Coordinator.
Bridges user messages with the NLP pipeline, consistency engine,
ledger state transitions, RAG retrieval, and speech feedback.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.database.models import (
    Customer, Supplier, Transaction, ConversationMessage, AuditLog
)
from backend.app.nlp.pipeline import nlp_pipeline
from backend.app.nlp.event_extraction import FinancialEvent
from backend.app.services.ledger_service import ledger_service
from backend.app.services.analytics_service import analytics_service
from backend.app.rag.document_service import document_service

# Idempotency sliding-window cache to block rapid double-submissions
_IDEMPOTENCY_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}

class ConversationService:
    @staticmethod
    def _fetch_known_entities(db: Session) -> List[Dict[str, Any]]:
        customers = db.query(Customer).all()
        suppliers = db.query(Supplier).all()
        entities = []
        for c in customers:
            entities.append({
                "id": c.id,
                "name": c.name,
                "type": "customer",
                "aliases": c.aliases,
                "balance": c.outstanding_balance
            })
        for s in suppliers:
            entities.append({
                "id": s.id,
                "name": s.name,
                "type": "supplier",
                "aliases": s.aliases,
                "balance": s.outstanding_balance
            })
        return entities

    @classmethod
    def process_message(
        cls,
        db: Session,
        message_text: str,
        session_id: str = "default_session",
        is_voice: bool = False,
        audio_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Check idempotency to prevent rapid double-registration (e.g. speech onend + Enter race)
        cache_key = f"{session_id}:{message_text.strip().lower()}"
        now_ts = time.time()
        
        # Purge stale cache entries (> 30 seconds)
        stale_keys = [k for k, (t, _) in _IDEMPOTENCY_CACHE.items() if now_ts - t > 30.0]
        for k in stale_keys:
            _IDEMPOTENCY_CACHE.pop(k, None)
            
        if cache_key in _IDEMPOTENCY_CACHE:
            prev_time, cached_res = _IDEMPOTENCY_CACHE[cache_key]
            if now_ts - prev_time < 2.5:
                return cached_res

        known_entities = cls._fetch_known_entities(db)
        
        # Determine active entity from recent transactions for balance lookups
        recent_txs = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(10).all()
        recent_tx_dicts = [
            {
                "counterparty_name": t.counterparty_name,
                "amount": t.amount,
                "type": t.transaction_type,
                "date": t.date
            }
            for t in recent_txs
        ]
        
        # Run NLP Pipeline
        nlp_result = nlp_pipeline.process_text(
            text=message_text,
            session_id=session_id,
            known_entities=known_entities,
            recent_transactions=recent_tx_dicts,
            is_spoken=is_voice
        )
        
        # Check if query vs transaction event
        if nlp_result.is_query and nlp_result.query_plan:
            return cls._handle_query(db, message_text, nlp_result, session_id, is_voice)
            
        # If document query (e.g. policy or invoice query)
        if any(w in message_text.lower() for w in ["policy", "terms", "contract", "rules", "agreement", "invoice inv"]):
            rag_res = document_service.query_documents(db, message_text)
            return {
                "message_type": "DOCUMENT_RAG",
                "text_response": rag_res["answer"],
                "rag_sources": rag_res["sources"],
                "nlp_diagnostics": nlp_result.to_dict()
            }
            
        # Process Financial Event
        event: FinancialEvent = nlp_result.event
        actor = event.actor
        
        # Check if phonetic entity disambiguation required
        ent_res = nlp_result.entity_resolution
        if ent_res.get("requires_disambiguation") and ent_res.get("suggested_matches"):
            return {
                "success": False,
                "message_type": "ENTITY_DISAMBIGUATION_REQUIRED",
                "requires_disambiguation": True,
                "extracted_actor": actor,
                "suggested_matches": ent_res.get("suggested_matches", []),
                "confirmation_prompt": ent_res.get("confirmation_prompt"),
                "proposed_event": event.model_dump(),
                "nlp_diagnostics": nlp_result.to_dict(),
                "text_response": ent_res.get("confirmation_prompt") or f"Did you mean existing account for '{actor}'?",
                "speech_data": nlp_result.speech_data
            }
        
        # Look up current balance for actor
        current_balance = 0.0
        cust = ledger_service.get_customer_by_name(db, actor)
        supp = ledger_service.get_supplier_by_name(db, actor)
        if cust:
            current_balance = cust.outstanding_balance
        elif supp:
            current_balance = supp.outstanding_balance
            
        # Re-evaluate consistency with accurate live balance
        consistency_info = nlp_result.consistency_info
        if current_balance > 0:
            from backend.app.nlp.consistency_engine import consistency_engine
            consistency_info = consistency_engine.validate_event_against_ledger(
                event.model_dump(),
                current_entity_balance=current_balance,
                recent_transactions=recent_tx_dicts
            )
            
        # Check if contradiction / confirmation required
        if consistency_info.get("requires_confirmation"):
            return {
                "success": False,
                "message_type": "CONTRADICTION_CONFIRMATION_REQUIRED",
                "requires_confirmation": True,
                "confirmation_prompt": consistency_info.get("confirmation_prompt"),
                "severity": consistency_info.get("severity"),
                "discrepancy_type": consistency_info.get("discrepancy_type"),
                "excess_amount": consistency_info.get("excess_amount", 0.0),
                "proposed_event": event.model_dump(),
                "current_balance": current_balance,
                "alerts": consistency_info.get("alerts", []),
                "nlp_diagnostics": nlp_result.to_dict(),
                "text_response": consistency_info.get("confirmation_prompt"),
                "speech_data": nlp_result.speech_data
            }
            
        # Automatically apply event to ledger if consistent
        ledger_result = ledger_service.apply_financial_event(db, event)
        
        # Build natural language response explanation
        response_text = cls._build_success_response(event, ledger_result)
        
        # Save message to conversation history
        conv_msg = ConversationMessage(
            session_id=session_id,
            sender="user",
            message_text=message_text,
            is_voice=is_voice,
            pipeline_dump_json=json.dumps(nlp_result.to_dict())
        )
        db.add(conv_msg)
        db.commit()
        
        final_result = {
            "message_type": "TRANSACTION_EXECUTED",
            "success": True,
            "text_response": response_text,
            "ledger_update": ledger_result,
            "nlp_diagnostics": nlp_result.to_dict(),
            "speech_data": nlp_result.speech_data
        }
        _IDEMPOTENCY_CACHE[cache_key] = (now_ts, final_result)
        return final_result

    @classmethod
    def confirm_and_apply_event(
        cls,
        db: Session,
        event_dict: Dict[str, Any],
        override_amount: Optional[float] = None,
        force_settle: bool = False,
        selected_entity_id: Optional[int] = None,
        override_actor: Optional[str] = None,
        link_as_alias: bool = True
    ) -> Dict[str, Any]:
        """User explicitly confirmed an ambiguous, disambiguated, or contradictory event."""
        event = FinancialEvent(**event_dict)
        original_actor = event.actor

        if override_actor:
            event.actor = override_actor
        elif selected_entity_id:
            cust = db.query(Customer).filter(Customer.id == selected_entity_id).first()
            supp = db.query(Supplier).filter(Supplier.id == selected_entity_id).first()
            target_ent = cust if (cust and event.direction != "payable") else (supp or cust)
            if target_ent:
                event.actor = target_ent.name
                if link_as_alias and original_actor and original_actor.lower() != target_ent.name.lower():
                    cur_aliases = target_ent.aliases or []
                    if original_actor not in cur_aliases:
                        cur_aliases.append(original_actor)
                        target_ent.aliases_json = json.dumps(cur_aliases)
                        db.flush()

        if override_amount is not None:
            event.amount = override_amount
        if force_settle:
            event.event_type = "full_settlement"
            
        ledger_result = ledger_service.apply_financial_event(db, event, force_override=True)
        response_text = f"Confirmed! Updated ledger for {event.actor}. Current outstanding balance: ₹{ledger_result['current_balance']:,.2f}."
        
        return {
            "success": True,
            "message_type": "TRANSACTION_EXECUTED",
            "text_response": response_text,
            "ledger_update": ledger_result
        }

    @classmethod
    def _handle_query(
        cls,
        db: Session,
        raw_query: str,
        nlp_result: Any,
        session_id: str,
        is_voice: bool
    ) -> Dict[str, Any]:
        plan = nlp_result.query_plan
        intent = plan.get("intent")
        
        if intent == "TOP_DEBTORS":
            debtors = analytics_service.get_top_debtors(db, limit=plan.get("limit", 5))
            if not debtors:
                resp = "No customers currently have pending dues."
            else:
                top = debtors[0]
                lines = [f"{i+1}. {d['name']}: ₹{d['outstanding_balance']:,.2f} (Risk: {d['risk_tier']})" for i, d in enumerate(debtors)]
                resp = f"**{top['name']} owes you the most (₹{top['outstanding_balance']:,.2f})**.\n\nTop Debtors:\n" + "\n".join(lines)
            data = debtors
        elif intent == "TOTAL_RECEIVABLES":
            tot = analytics_service.get_total_receivables(db)
            resp = f"**Total outstanding customer receivables: ₹{tot:,.2f}**"
            data = {"total_receivables": tot}
        elif intent == "TOTAL_PAYABLES":
            tot = analytics_service.get_total_payables(db)
            resp = f"**Total outstanding supplier payables: ₹{tot:,.2f}**"
            data = {"total_payables": tot}
        elif intent == "CASH_FLOW_SUMMARY":
            summary = analytics_service.get_cash_flow_summary(db)
            resp = f"**Cash Flow Summary**\n- Cash Inflow: ₹{summary['total_inflow']:,.2f}\n- Cash Outflow: ₹{summary['total_outflow']:,.2f}\n- Net Position: ₹{summary['net_cash_position']:,.2f}"
            data = summary
        elif intent == "PAYMENT_REMINDERS_DUE":
            reminders = analytics_service.get_due_reminders(db)
            if not reminders:
                resp = "No upcoming payment reminders due."
            else:
                lines = [f"- {r['customer_name']}: ₹{r['amount']:,.2f} (Due: {r['due_date']})" for r in reminders]
                resp = f"**Upcoming Payment Reminders ({len(reminders)}):**\n" + "\n".join(lines)
            data = reminders
        else:
            resp = "Understood your query, but could not find matching financial summary."
            data = {}

        return {
            "message_type": "ANALYTICAL_QUERY_ANSWER",
            "success": True,
            "text_response": resp,
            "query_data": data,
            "nlp_diagnostics": nlp_result.to_dict()
        }

    @classmethod
    def _build_success_response(cls, event: FinancialEvent, ledger_result: Dict[str, Any]) -> str:
        actor = ledger_result.get("entity_name", event.actor)
        amount = event.amount
        balance = ledger_result.get("current_balance", 0.0)
        status = ledger_result.get("status", "SUCCESS")
        
        if event.direction == "receivable":
            if event.event_type in ["partial_payment", "full_payment", "payment_received", "full_settlement"]:
                if balance == 0:
                    return f"✅ **{actor}** నుండి **₹{amount:,.2f}** అందింది. బాకీ పూర్తిగా క్లియర్ అయింది! *(Received ₹{amount:,.2f} from {actor}. Account fully settled ₹0.00)*"
                else:
                    return f"✅ **{actor}** నుండి **₹{amount:,.2f}** అందింది. మిగిలిన బాకీ: **₹{balance:,.2f}** *(Received ₹{amount:,.2f} from {actor}. Remaining balance: ₹{balance:,.2f})*"
            else:
                return f"📝 **{actor}** ఖాతాలో **₹{amount:,.2f}** అప్పు/సేల్ నమోదయింది. మొత్తం బాకీ: **₹{balance:,.2f}** *(Recorded credit sale of ₹{amount:,.2f} for {actor}. Total balance: ₹{balance:,.2f})*"
        else:
            if event.event_type in ["payment_made", "partial_payment", "full_settlement"]:
                if balance == 0:
                    return f"✅ **{actor}** కి **₹{amount:,.2f}** చెల్లించాము. సప్లయర్ బాకీ పూర్తిగా తీరింది! *(Paid ₹{amount:,.2f} to {actor}. Supplier balance fully cleared ₹0.00)*"
                else:
                    return f"✅ **{actor}** కి **₹{amount:,.2f}** చెల్లించాము. మిగిలిన బాకీ: **₹{balance:,.2f}** *(Paid ₹{amount:,.2f} to {actor}. Remaining payable: ₹{balance:,.2f})*"
            else:
                return f"📦 **{actor}** వద్ద కొనుగోలు **₹{amount:,.2f}** నమోదయింది. సప్లయర్ కి ఇవ్వాల్సిన బాకీ: **₹{balance:,.2f}** *(Recorded purchase of ₹{amount:,.2f} from {actor}. Total payable: ₹{balance:,.2f})*"

# Global singleton
conversation_service = ConversationService()
