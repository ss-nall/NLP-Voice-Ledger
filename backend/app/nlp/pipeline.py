"""
Master Modular NLP Pipeline Orchestrator.
Wraps the enterprise BlackboardNLPPipeline engine with full backwards compatibility,
supporting single and multi-event financial propositions.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.nlp.event_extraction import FinancialEvent
from backend.app.nlp.pipeline_core import blackboard_pipeline, PipelineContext

class NLPPipelineResult:
    def __init__(
        self,
        raw_input: str,
        speech_data: Optional[Dict[str, Any]],
        language_info: Dict[str, Any],
        code_switch_info: Dict[str, Any],
        normalized_info: Dict[str, Any],
        entities: Dict[str, Any],
        temporal_info: List[Dict[str, Any]],
        relation_info: Dict[str, Any],
        event: FinancialEvent,
        entity_resolution: Dict[str, Any],
        coreference_info: Dict[str, Any],
        consistency_info: Dict[str, Any],
        is_query: bool = False,
        query_plan: Optional[Dict[str, Any]] = None,
        telemetry: Optional[List[Dict[str, Any]]] = None,
        all_events: Optional[List[FinancialEvent]] = None
    ):
        self.raw_input = raw_input
        self.speech_data = speech_data
        self.language_info = language_info
        self.code_switch_info = code_switch_info
        self.normalized_info = normalized_info
        self.entities = entities
        self.temporal_info = temporal_info
        self.relation_info = relation_info
        self.event = event
        self.entity_resolution = entity_resolution
        self.coreference_info = coreference_info
        self.consistency_info = consistency_info
        self.is_query = is_query
        self.query_plan = query_plan
        self.telemetry = telemetry or []
        self.all_events = all_events or [event]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_input": self.raw_input,
            "speech_data": self.speech_data,
            "language_info": self.language_info,
            "code_switch_info": self.code_switch_info,
            "normalized_info": self.normalized_info,
            "entities": self.entities,
            "temporal_info": self.temporal_info,
            "relation_info": self.relation_info,
            "event": self.event.model_dump() if self.event else {},
            "all_events": [e.model_dump() for e in self.all_events],
            "entity_resolution": self.entity_resolution,
            "coreference_info": self.coreference_info,
            "consistency_info": self.consistency_info,
            "is_query": self.is_query,
            "query_plan": self.query_plan,
            "telemetry": self.telemetry
        }


class NLPPipeline:
    """
    Modular execution engine for bilingual Telugu-English bookkeeping NLP.
    """
    
    def process_text(
        self,
        text: str,
        session_id: str = "default_session",
        known_entities: Optional[List[Dict[str, Any]]] = None,
        current_balance: float = 0.0,
        recent_transactions: Optional[List[Dict[str, Any]]] = None,
        is_spoken: bool = False
    ) -> NLPPipelineResult:
        ctx: PipelineContext = blackboard_pipeline.process(
            text=text,
            session_id=session_id,
            known_entities=known_entities or [],
            current_balance=current_balance,
            recent_transactions=recent_transactions or [],
            is_spoken=is_spoken
        )

        primary_event = ctx.events[0] if ctx.events else FinancialEvent(
            event_type="TRANSACTION",
            actor="Unspecified",
            amount=0.0,
            direction="receivable",
            event_date=datetime.now().strftime("%Y-%m-%d"),
            source_text=ctx.raw_input,
            confidence=0.5,
            explanation="Processed utterance"
        )

        return NLPPipelineResult(
            raw_input=ctx.raw_input,
            speech_data=ctx.speech_data,
            language_info=ctx.language_info,
            code_switch_info=ctx.code_switch_info,
            normalized_info=ctx.normalized_info,
            entities=ctx.entities,
            temporal_info=ctx.temporal_info,
            relation_info=ctx.relation_info,
            event=primary_event,
            entity_resolution=ctx.entity_resolution,
            coreference_info=ctx.coreference_info,
            consistency_info=ctx.consistency_info,
            is_query=ctx.is_query,
            query_plan=ctx.query_plan,
            telemetry=[{"component": t.component, "duration_ms": round(t.duration_ms, 2)} for t in ctx.telemetry],
            all_events=ctx.events
        )

# Global singleton
nlp_pipeline = NLPPipeline()
