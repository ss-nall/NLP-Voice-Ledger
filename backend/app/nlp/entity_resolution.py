"""
Entity Resolution & Alias Linking Engine.
Matches mentioned actors against canonical customer and supplier records
using exact alias tables, Indic phonetic soundex, and fuzzy Levenshtein/Jaro-Winkler similarity.
Supports interactive multi-match disambiguation prompts.
"""

import re
import difflib
from typing import Dict, Any, List, Optional, Tuple
from backend.app.nlp.transliteration import indic_phonetic_fingerprint, get_bilingual_names
from backend.app.nlp.telugu_lexicon import TELUGU_HONORIFICS
from backend.app.nlp.indic_phonetics import indic_phonetic_matcher, strip_indic_honorifics

class EntityResolver:
    """
    Resolves conversational entity mentions to database records.
    Provides phonetic scoring and suggested match candidates for ambiguous pronunciations.
    """
    
    @staticmethod
    def clean_name(raw_name: str) -> str:
        if not raw_name:
            return ""
        s = raw_name.lower().strip()
        # Remove bracketed content like (రమేష్) or (Ramesh)
        s = re.sub(r'\(.*?\)', ' ', s)
        # Remove honorifics and postpositions
        for h in TELUGU_HONORIFICS + [
            "gariki", "annaki", "bhaiki", "sethki", "ki", "ku", "nundi", "nunchi", "daggara",
            "garu", "gaaru", "anna", "bhai", "ji", "seth", "saab", "reddy", "rao", "babu",
            "గారికి", "అన్నకి", "కి", "కు", "నుండి", "నుంచి", "గారు", "అన్న"
        ]:
            s = re.sub(r'\b' + re.escape(h) + r'\b', '', s)
            if s.endswith(h) and len(s) > len(h) + 2:
                s = s[:-len(h)]
        s = re.sub(r'[^\w\s\u0C00-\u0C7F]', ' ', s)
        return re.sub(r'\s+', ' ', s).strip()

    @classmethod
    def calculate_similarity(cls, s1: str, s2: str) -> float:
        """Computes hybrid Levenshtein ratio + prefix weighting."""
        c1 = cls.clean_name(s1)
        c2 = cls.clean_name(s2)
        if not c1 or not c2:
            return 0.0
        if c1 == c2:
            return 1.0
            
        seq_ratio = difflib.SequenceMatcher(None, c1, c2).ratio()
        
        # Jaro-Winkler style prefix bonus
        prefix_len = 0
        for ch1, ch2 in zip(c1, c2):
            if ch1 == ch2:
                prefix_len += 1
            else:
                break
        prefix_bonus = min(prefix_len, 4) * 0.03
        
        # Phonetic bonus
        f1 = indic_phonetic_fingerprint(c1)
        f2 = indic_phonetic_fingerprint(c2)
        phonetic_bonus = 0.15 if (f1 and f2 and f1 == f2) else 0.0
        
        return min(1.0, round(seq_ratio + prefix_bonus + phonetic_bonus, 2))

    @classmethod
    def resolve_entity(
        cls,
        mention: str,
        known_entities: List[Dict[str, Any]],
        role_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Matches mention against known entities.
        known_entities structure: [{"id": 1, "name": "Sathwik", "type": "customer", "aliases": ["Satvik"], "balance": 1500.0}, ...]
        """
        if not mention or mention.lower() in ["unspecified", "someone", "customer", "supplier", "dealer", "కస్టమర్", "సప్లయర్"]:
            return {
                "matched": False,
                "entity_id": None,
                "canonical_name": mention if mention else "Unspecified",
                "confidence": 0.0,
                "requires_disambiguation": False,
                "requires_confirmation": False,
                "suggested_matches": []
            }
            
        clean_mention = cls.clean_name(mention)
        if not clean_mention:
            return {
                "matched": False,
                "entity_id": None,
                "canonical_name": mention,
                "confidence": 0.0,
                "requires_disambiguation": False,
                "requires_confirmation": False,
                "suggested_matches": []
            }

        target_bilingual = get_bilingual_names(clean_mention)
        target_en = cls.clean_name(target_bilingual.get("english", "")).lower()
        target_te = cls.clean_name(target_bilingual.get("telugu", "")).lower()
        mention_fingerprint = indic_phonetic_fingerprint(clean_mention)
        
        best_exact_match = None
        suggested_matches = []
        
        for ent in known_entities:
            ent_name = ent.get("name", "")
            ent_en = ent.get("name_english", "")
            ent_te = ent.get("name_telugu", "")
            aliases = ent.get("aliases", [])
            all_variants = [ent_name, ent_en, ent_te] + (aliases if isinstance(aliases, list) else [])
            cleaned_variants = [cls.clean_name(v).lower() for v in all_variants if v and cls.clean_name(v)]
            
            # 1. Exact string / bilingual match
            if clean_mention in cleaned_variants or (target_en and target_en in cleaned_variants) or (target_te and target_te in cleaned_variants):
                best_exact_match = ent
                break
                
            # 2. Phonetic soundex fingerprint match (e.g. Pavan vs Pawan, Satvik vs Sathwik)
            if mention_fingerprint:
                matched_fp = False
                for cv in cleaned_variants:
                    cv_fp = indic_phonetic_fingerprint(cv)
                    if cv_fp and cv_fp == mention_fingerprint:
                        best_exact_match = ent
                        matched_fp = True
                        break
                if matched_fp:
                    break
                    
            # 3. Compute best similarity score across all variants using IndicPhoneticMatcher
            max_ent_sim = 0.0
            for name_variant in all_variants:
                if name_variant:
                    sim = cls.calculate_similarity(clean_mention, name_variant)
                    phonetic_sim = indic_phonetic_matcher.match_score(clean_mention, name_variant)
                    best_sim = max(sim, phonetic_sim)
                    if best_sim > max_ent_sim:
                        max_ent_sim = best_sim
                        
            if max_ent_sim >= 0.65:
                suggested_matches.append({
                    "id": ent.get("id"),
                    "name": ent.get("name"),
                    "type": ent.get("type", "customer"),
                    "outstanding_balance": ent.get("balance", 0.0),
                    "similarity": max_ent_sim
                })
                
        # 1. Deterministic Exact or Phonetic Fingerprint Match found
        if best_exact_match:
            return {
                "matched": True,
                "entity_id": best_exact_match.get("id"),
                "canonical_name": best_exact_match.get("name"),
                "entity_type": best_exact_match.get("type", "customer"),
                "confidence": 1.0,
                "requires_disambiguation": False,
                "requires_confirmation": False,
                "suggested_matches": []
            }
            
        # 2. Ambiguous or Moderately Close match exists (Needs Disambiguation / User Confirmation)
        if suggested_matches:
            suggested_matches.sort(key=lambda x: x["similarity"], reverse=True)
            top_match = suggested_matches[0]
            return {
                "matched": False,
                "entity_id": top_match["id"],
                "canonical_name": mention.title() if not mention.isupper() else mention,
                "entity_type": top_match["type"],
                "confidence": top_match["similarity"],
                "requires_disambiguation": True,
                "requires_confirmation": True,
                "suggested_matches": suggested_matches[:3],
                "confirmation_prompt": f"మీరు చెప్పిన '{mention}' ఇప్పటికే ఉన్న '{top_match['name']}' కి సంబంధించినదా?"
            }
            
        # 3. Completely new entity
        return {
            "matched": False,
            "entity_id": None,
            "canonical_name": mention.title() if not mention.isupper() else mention,
            "entity_type": "customer" if role_hint != "supplier" else "supplier",
            "confidence": 0.50,
            "requires_disambiguation": False,
            "requires_confirmation": False,
            "suggested_matches": []
        }

# Global singleton
entity_resolver = EntityResolver()
