"""
Enterprise Pluggable Blackboard NLP Pipeline Core.
Manages blackboard execution context, component lifecycle hooks, latency telemetry,
and atomic multi-clause processing.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
import re

from backend.app.nlp.telugu_lexicon import TELUGU_NUMERALS
from backend.app.nlp.speech_processor import speech_processor
from backend.app.nlp.language_detection import language_identifier
from backend.app.nlp.code_switching import code_switch_detector
from backend.app.nlp.transliteration import phonetic_normalizer, split_telugu_sandhi
from backend.app.nlp.temporal_extraction import temporal_extractor
from backend.app.nlp.entity_extraction import entity_extractor
from backend.app.nlp.relation_extraction import relation_extractor
from backend.app.nlp.event_extraction import event_builder, FinancialEvent
from backend.app.nlp.entity_resolution import entity_resolver
from backend.app.nlp.dialogue_tracker import dialogue_tracker
from backend.app.nlp.clause_splitter import clause_splitter
from backend.app.nlp.indic_phonetics import indic_phonetic_matcher
from backend.app.nlp.consistency_engine import consistency_engine
from backend.app.nlp.query_engine import query_engine

@dataclass
class TelemetrySpan:
    component: str
    duration_ms: float
    status: str = "SUCCESS"

@dataclass
class PipelineContext:
    raw_input: str
    session_id: str
    is_spoken: bool = False
    known_entities: List[Dict[str, Any]] = field(default_factory=list)
    current_balance: float = 0.0
    recent_transactions: List[Dict[str, Any]] = field(default_factory=list)
    working_text: str = ""
    clauses: List[Dict[str, Any]] = field(default_factory=list)
    speech_data: Optional[Dict[str, Any]] = None
    language_info: Dict[str, Any] = field(default_factory=dict)
    code_switch_info: Dict[str, Any] = field(default_factory=dict)
    normalized_info: Dict[str, Any] = field(default_factory=dict)
    entities: Dict[str, Any] = field(default_factory=dict)
    temporal_info: List[Dict[str, Any]] = field(default_factory=list)
    relation_info: Dict[str, Any] = field(default_factory=dict)
    events: List[FinancialEvent] = field(default_factory=list)
    entity_resolution: Dict[str, Any] = field(default_factory=dict)
    coreference_info: Dict[str, Any] = field(default_factory=dict)
    consistency_info: Dict[str, Any] = field(default_factory=dict)
    is_query: bool = False
    query_plan: Optional[Dict[str, Any]] = None
    telemetry: List[TelemetrySpan] = field(default_factory=list)

class BlackboardNLPPipeline:
    """
    Enterprise modular blackboard orchestrator for bilingual Telugu-English bookkeeping.
    """

    def process(
        self,
        text: str,
        session_id: str = "default_session",
        known_entities: Optional[List[Dict[str, Any]]] = None,
        current_balance: float = 0.0,
        recent_transactions: Optional[List[Dict[str, Any]]] = None,
        is_spoken: bool = False
    ) -> PipelineContext:
        ctx = PipelineContext(
            raw_input=text,
            session_id=session_id,
            is_spoken=is_spoken,
            known_entities=known_entities or [],
            current_balance=current_balance,
            recent_transactions=recent_transactions or [],
            working_text=text
        )

        # 1. Check for Natural Language Analytical Query
        t0 = time.perf_counter()
        q_plan = query_engine.parse_query(text)
        if q_plan.get("is_query"):
            ctx.is_query = True
            ctx.query_plan = q_plan
            ctx.telemetry.append(TelemetrySpan("SemanticQueryEngine", (time.perf_counter() - t0) * 1000))
            return ctx

        # 2. Sandhi Normalization & Spoken Number Processing
        t0 = time.perf_counter()
        sandhi_split = split_telugu_sandhi(text)
        tokens = re.findall(r'[a-zA-Z0-9\u0C00-\u0C7F]+', sandhi_split.lower())
        has_spoken_numerals = any(t in TELUGU_NUMERALS or bool(re.match(r'^\d+(?:\.\d+)?k$', t)) for t in tokens)

        if is_spoken or has_spoken_numerals:
            speech_res = speech_processor.process_spoken_transcript(sandhi_split)
            ctx.speech_data = speech_res
            ctx.working_text = speech_res["normalized_transcript"]
        else:
            ctx.working_text = sandhi_split
        ctx.telemetry.append(TelemetrySpan("SpokenNumberNormalizer", (time.perf_counter() - t0) * 1000))

        # 3. Compound Clause Splitter
        t0 = time.perf_counter()
        clauses = clause_splitter.split_clauses(ctx.working_text)
        ctx.clauses = clauses
        ctx.telemetry.append(TelemetrySpan("CompoundClauseSplitter", (time.perf_counter() - t0) * 1000))

        # 4. Language & Code-Switching Detection
        t0 = time.perf_counter()
        ctx.language_info = language_identifier.identify(ctx.working_text)
        ctx.code_switch_info = code_switch_detector.analyze(ctx.working_text)
        ctx.telemetry.append(TelemetrySpan("LanguageAndCodeSwitchDetector", (time.perf_counter() - t0) * 1000))

        # Process Each Clause into Financial Events
        for clause_item in clauses:
            clause_text = clause_item["clause_text"]
            
            # Normalization
            norm_res = phonetic_normalizer.normalize(clause_text)
            norm_text = norm_res["normalized_text"]
            ctx.normalized_info = norm_res

            # Temporal Extraction
            temporal_res = temporal_extractor.extract_dates(norm_text)
            ctx.temporal_info = temporal_res

            # Entity Extraction
            entities_res = entity_extractor.extract_entities(norm_text)
            ctx.entities = entities_res

            # Dialogue State & Anaphora Coreference Resolution
            dst_res = dialogue_tracker.resolve_anaphora_and_implicit_slots(
                session_id=ctx.session_id,
                text=norm_text,
                extracted_entities=entities_res,
                current_entity_balance=ctx.current_balance
            )
            ctx.coreference_info = dst_res

            if not entities_res.get("actors") and dst_res.get("resolved_actor"):
                entities_res["actors"].append({
                    "name": dst_res["resolved_actor"],
                    "raw_span": dst_res["resolved_actor"],
                    "type": "PERSON",
                    "confidence": 0.88,
                    "resolved_via_context": True
                })

            if not entities_res.get("amounts") and dst_res.get("inferred_amount"):
                entities_res["amounts"].append({
                    "value": dst_res["inferred_amount"],
                    "currency": "INR",
                    "raw_span": "remaining balance",
                    "confidence": 0.90,
                    "inferred_from_ledger": True
                })

            # Relation Extraction
            relation_res = relation_extractor.extract_relation(norm_text, entities_res)
            ctx.relation_info = relation_res

            # Financial Event Construction
            event = event_builder.build_event(clause_text, entities_res, relation_res, temporal_res, ctx.language_info)

            # Indic Phonetic Canonical Entity Resolution
            resolved_entity = entity_resolver.resolve_entity(
                event.actor,
                ctx.known_entities,
                role_hint="supplier" if event.direction == "payable" else "customer"
            )
            if resolved_entity.get("matched"):
                event.actor = resolved_entity["canonical_name"]
            ctx.entity_resolution = resolved_entity

            # Consistency & Contradiction Checking
            consistency_res = consistency_engine.validate_event_against_ledger(
                event.model_dump(),
                current_entity_balance=ctx.current_balance,
                recent_transactions=ctx.recent_transactions
            )
            ctx.consistency_info = consistency_res

            # Record Event into Dialogue Tracker
            dialogue_tracker.record_turn(
                session_id=ctx.session_id,
                text=clause_text,
                event_data=event.model_dump(),
                metadata={"consistency": consistency_res, "resolved_entity": resolved_entity}
            )

            ctx.events.append(event)

        return ctx

blackboard_pipeline = BlackboardNLPPipeline()
