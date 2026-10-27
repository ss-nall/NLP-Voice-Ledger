"""
Finite State Dialogue State Tracker (DST) & Anaphora Coreference Engine.
Tracks active dialogue slots, conversation state machine, pronoun resolution,
and implicit ledger references.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import time

class DialogueState(str, Enum):
    IDLE = "IDLE"
    COLLECTING_SLOTS = "COLLECTING_SLOTS"
    CONFIRMING_DISAMBIGUATION = "CONFIRMING_DISAMBIGUATION"
    CONFIRMING_CONTRADICTION = "CONFIRMING_CONTRADICTION"
    COMMITTED = "COMMITTED"

# Multi-Lingual Pronoun Maps across 8 Indian Languages & English
PRONOUNS_MALE = [
    'అతను', 'అతనికి', 'అతడికి', 'ఆయన', 'ఆయనకి', 'వాడు', 'వాడికి',
    'athanu', 'athaniki', 'aayana', 'vaadu', 'vaadiki',
    'அவன்', 'அவனுக்கு', 'அவர்', 'அவருக்கு', 'avan', 'avanukku', 'avar', 'avarukku',
    'उसने', 'उसको', 'उसे', 'वह', 'वो', 'usne', 'usko', 'use', 'woh', 'wo',
    'ಅವನು', 'ಅವನಿಗೆ', 'ಅವರು', 'ಅವರಿಗೆ', 'avanu', 'avanige', 'avaru', 'avarige',
    'അവൻ', 'അവന്', 'അവർ', 'അവർക്ക്', 'avan', 'avanu', 'avar', 'avarkku',
    'اس نے', 'اس کو', 'اسے', 'وہ',
    'તેણે', 'તેને', 'તેઓ', 'તેમને', 'tene', 'temne', 'teo',
    'he', 'him'
]

PRONOUNS_FEMALE = [
    'ఆమె', 'ఆమెకి', 'ఆవిడ', 'ఆవిడకి', 'aame', 'aameki', 'aavida',
    'அவள்', 'அவளுக்கு', 'aval', 'avalukku',
    'ಅವಳು', 'ಅವಳಿಗೆ', 'avalu', 'avalige',
    'അവൾ', 'അവൾക്ക്', 'aval', 'avalkku',
    'તેણી', 'તેણીને', 'teni',
    'she', 'her'
]

PRONOUNS_PLURAL_OR_HONORIFIC = [
    'వారు', 'వారికి', 'వాళ్లు', 'వాళ్లకి', 'vaaru', 'vaariki', 'vaallu', 'vaallaki',
    'அவர்கள்', 'அவர்களுக்கு', 'avargal', 'avargalukku',
    'उन्होंने', 'उनको', 'उन्हें', 'unhone', 'unko', 'unhe',
    'ಅವರು', 'ಅವರಿಗೆ', 'avaru', 'avarige',
    'അവർ', 'അവർക്ക്', 'avar', 'avarkku',
    'انہوں نے', 'ان کو', 'انہیں',
    'તેઓ', 'તેમને', 'teo', 'temne',
    'they', 'them'
]

REMAINING_AMOUNT_KEYWORDS = [
    'మిగిలిన', 'మిగిలినది', 'మిగతా', 'బాకీ మొత్తం', 'పూర్తి బాకీ',
    'migilina', 'migatha', 'remaining', 'balance', 'full amount', 'cleared',
    'மீதமுள்ள', 'பாக்கி தொகை', 'बाकी', 'बचा हुआ', 'ಉಳಿದ', 'ബാക്കി', 'باقی', 'બાકી રહેલ'
]

class DialogueSessionState:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state: DialogueState = DialogueState.IDLE
        self.last_active_actor: Optional[str] = None
        self.last_actor_gender: str = "MALE"
        self.last_direction: Optional[str] = None
        self.last_amount: Optional[float] = None
        self.pending_event: Optional[Dict[str, Any]] = None
        self.history: List[Dict[str, Any]] = []
        self.last_updated_at: float = time.time()

    def update_with_event(self, event_data: Dict[str, Any]):
        if event_data.get("actor") and event_data["actor"] != "Unspecified":
            self.last_active_actor = event_data["actor"]
        if event_data.get("direction"):
            self.last_direction = event_data["direction"]
        if event_data.get("amount"):
            self.last_amount = event_data["amount"]
        self.last_updated_at = time.time()

class DialogueTracker:
    """
    Enterprise DST tracking dialogue turns and performing context-aware slot filling.
    """

    def __init__(self):
        self._sessions: Dict[str, DialogueSessionState] = {}

    def get_or_create_session(self, session_id: str) -> DialogueSessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = DialogueSessionState(session_id)
        return self._sessions[session_id]

    def resolve_anaphora_and_implicit_slots(
        self,
        session_id: str,
        text: str,
        extracted_entities: Dict[str, Any],
        current_entity_balance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Resolves pronouns to the last active entity and infers remaining balance when referenced.
        """
        session = self.get_or_create_session(session_id)
        text_lower = text.lower()
        resolved_actor = None
        is_pronoun_used = False
        is_remaining_referenced = False
        actor_resolved_from_context = False

        # 1. Pronoun Detection
        tokens = text_lower.split()
        for token in tokens:
            if token in PRONOUNS_MALE or token in PRONOUNS_FEMALE or token in PRONOUNS_PLURAL_OR_HONORIFIC:
                is_pronoun_used = True
                if session.last_active_actor:
                    resolved_actor = session.last_active_actor
                    actor_resolved_from_context = True
                break

        # 2. Omitted Actor Context Resolution
        if not extracted_entities.get("actors") and not resolved_actor and session.last_active_actor:
            resolved_actor = session.last_active_actor
            actor_resolved_from_context = True

        # 3. Implicit Remaining Balance Detection
        for kw in REMAINING_AMOUNT_KEYWORDS:
            if kw in text_lower:
                is_remaining_referenced = True
                break

        return {
            "is_pronoun_used": is_pronoun_used,
            "resolved_actor": resolved_actor or "Unspecified",
            "actor_resolved_from_context": actor_resolved_from_context,
            "is_remaining_referenced": is_remaining_referenced,
            "inferred_amount": current_entity_balance if is_remaining_referenced else None,
            "dialogue_state": session.state.value,
            "last_active_actor": session.last_active_actor
        }

    def record_turn(self, session_id: str, text: str, event_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        session = self.get_or_create_session(session_id)
        session.update_with_event(event_data)
        session.history.append({
            "timestamp": time.time(),
            "text": text,
            "event": event_data,
            "metadata": metadata or {}
        })

    def reset_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

    def clear_session(self, session_id: str):
        self.reset_session(session_id)

dialogue_tracker = DialogueTracker()
