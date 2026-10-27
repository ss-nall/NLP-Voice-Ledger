"""
Multi-Lingual Indic Language Identification Module.
Identifies sentence-level and token-level language across 8 languages:
- 'telugu_script' (Unicode Telugu: 0x0C00 - 0x0C7F)
- 'tamil_script' (Unicode Tamil: 0x0B80 - 0x0BFF)
- 'hindi_script' (Unicode Devanagari: 0x0900 - 0x097F)
- 'kannada_script' (Unicode Kannada: 0x0C80 - 0x0CFF)
- 'malayalam_script' (Unicode Malayalam: 0x0D00 - 0x0D7F)
- 'urdu_script' (Unicode Arabic/Urdu: 0x0600 - 0x06FF)
- 'gujarati_script' (Unicode Gujarati: 0x0A80 - 0x0AFF)
- 'romanized_telugu', 'romanized_tamil', 'romanized_hindi', 'romanized_kannada',
  'romanized_malayalam', 'romanized_urdu', 'romanized_gujarati'
- 'english'
- 'code_mixed_script' & 'code_mixed_romanized'
"""

import re
from typing import Dict, Any, List
from backend.app.nlp.telugu_lexicon import (
    TELUGU_NUMERALS, DIRECTION_MARKERS as TELUGU_DIRECTION_MARKERS,
    TEMPORAL_LEXICON as TELUGU_TEMPORAL_LEXICON, DAYS_OF_WEEK as TELUGU_DAYS_OF_WEEK,
    TELUGU_HONORIFICS, BUSINESS_TERMS as TELUGU_BUSINESS_TERMS
)
from backend.app.nlp.tamil_lexicon import (
    TAMIL_NUMERALS, TAMIL_DIRECTION_MARKERS, TAMIL_TEMPORAL_LEXICON,
    TAMIL_DAYS_OF_WEEK, TAMIL_HONORIFICS, TAMIL_BUSINESS_TERMS
)
from backend.app.nlp.hindi_lexicon import (
    HINDI_NUMERALS, HINDI_DIRECTION_MARKERS, HINDI_TEMPORAL_LEXICON,
    HINDI_DAYS_OF_WEEK, HINDI_HONORIFICS, HINDI_BUSINESS_TERMS
)
from backend.app.nlp.kannada_lexicon import (
    KANNADA_NUMERALS, KANNADA_DIRECTION_MARKERS, KANNADA_TEMPORAL_LEXICON,
    KANNADA_HONORIFICS, KANNADA_BUSINESS_TERMS
)
from backend.app.nlp.malayalam_lexicon import (
    MALAYALAM_NUMERALS, MALAYALAM_DIRECTION_MARKERS, MALAYALAM_TEMPORAL_LEXICON,
    MALAYALAM_HONORIFICS, MALAYALAM_BUSINESS_TERMS
)
from backend.app.nlp.urdu_lexicon import (
    URDU_NUMERALS, URDU_DIRECTION_MARKERS, URDU_TEMPORAL_LEXICON,
    URDU_HONORIFICS, URDU_BUSINESS_TERMS
)
from backend.app.nlp.gujarati_lexicon import (
    GUJARATI_NUMERALS, GUJARATI_DIRECTION_MARKERS, GUJARATI_TEMPORAL_LEXICON,
    GUJARATI_HONORIFICS, GUJARATI_BUSINESS_TERMS
)

# Romanized Vocabularies
ROMANIZED_TELUGU_VOCAB = set(
    list(TELUGU_NUMERALS.keys()) +
    list(TELUGU_TEMPORAL_LEXICON.keys()) +
    list(TELUGU_DAYS_OF_WEEK.keys()) +
    TELUGU_HONORIFICS +
    list(TELUGU_BUSINESS_TERMS.keys()) +
    TELUGU_DIRECTION_MARKERS.get("PAYABLE_POSTPOSITIONS", []) +
    TELUGU_DIRECTION_MARKERS.get("RECEIVABLE_POSTPOSITIONS", []) +
    TELUGU_DIRECTION_MARKERS.get("PAYABLE_VERBS", []) +
    TELUGU_DIRECTION_MARKERS.get("RECEIVABLE_VERBS", []) +
    TELUGU_DIRECTION_MARKERS.get("PAID_BY_CUSTOMER_VERBS", []) +
    TELUGU_DIRECTION_MARKERS.get("PAID_BY_BUSINESS_VERBS", []) +
    [
        "undi", "unna", "unnayi", "kavali", "cheppu", "enti", "entha", "evaru", "naaku", "nenu",
        "chesa", "chesam", "chesanu", "chesadu", "chesindi", "chesaru", "cheyyaledu", "kaledu",
        "lekapothe", "mottam", "annadu", "annanu", "cheppadu", "cheppanu", "pettadu", "teesuko",
        "dabbulu", "rupailu", "rupayalu", "chillara", "baki", "udhari", "saraku", "konna"
    ]
)

ROMANIZED_TAMIL_VOCAB = set(
    list(TAMIL_NUMERALS.keys()) +
    list(TAMIL_TEMPORAL_LEXICON.keys()) +
    list(TAMIL_DAYS_OF_WEEK.keys()) +
    TAMIL_HONORIFICS +
    list(TAMIL_BUSINESS_TERMS.keys()) +
    TAMIL_DIRECTION_MARKERS.get("PAYABLE_POSTPOSITIONS", []) +
    TAMIL_DIRECTION_MARKERS.get("RECEIVABLE_POSTPOSITIONS", []) +
    TAMIL_DIRECTION_MARKERS.get("PAYABLE_VERBS", []) +
    TAMIL_DIRECTION_MARKERS.get("RECEIVABLE_VERBS", []) +
    TAMIL_DIRECTION_MARKERS.get("PAID_BY_CUSTOMER_VERBS", []) +
    TAMIL_DIRECTION_MARKERS.get("PAID_BY_BUSINESS_VERBS", []) +
    [
        "irukku", "irukanga", "venum", "solleru", "enna", "evalo", "yaaru", "enakku", "naan",
        "pannen", "pannom", "pannaan", "panninaar", "panren", "aachu", "aayiduchu",
        "mudichu", "sonnaan", "sonnaaru", "tharuvaaru", "vaangiko",
        "panam", "kaasu", "rubai", "kadhan", "porul", "vaanginen"
    ]
)

ROMANIZED_HINDI_VOCAB = set(
    list(HINDI_NUMERALS.keys()) +
    list(HINDI_TEMPORAL_LEXICON.keys()) +
    list(HINDI_DAYS_OF_WEEK.keys()) +
    HINDI_HONORIFICS +
    list(HINDI_BUSINESS_TERMS.keys()) +
    HINDI_DIRECTION_MARKERS.get("PAYABLE_POSTPOSITIONS", []) +
    HINDI_DIRECTION_MARKERS.get("RECEIVABLE_POSTPOSITIONS", []) +
    HINDI_DIRECTION_MARKERS.get("PAYABLE_VERBS", []) +
    HINDI_DIRECTION_MARKERS.get("RECEIVABLE_VERBS", []) +
    HINDI_DIRECTION_MARKERS.get("PAID_BY_CUSTOMER_VERBS", []) +
    HINDI_DIRECTION_MARKERS.get("PAID_BY_BUSINESS_VERBS", []) +
    [
        "hai", "hain", "tha", "the", "chahiye", "batao", "kya", "kitna", "kaun", "kisko", "kisse",
        "mujhe", "humko", "maine", "humne", "usne", "unhone", "kiya", "karega", "karenge",
        "diya", "dena", "lena", "aana", "milna", "bheja", "paise", "rupaye", "rokda", "khata", "hisaab"
    ]
)

ROMANIZED_KANNADA_VOCAB = set(
    list(KANNADA_NUMERALS.keys()) +
    list(KANNADA_TEMPORAL_LEXICON.keys()) +
    KANNADA_HONORIFICS +
    list(KANNADA_BUSINESS_TERMS.keys()) +
    KANNADA_DIRECTION_MARKERS.get("DATIVE_POSTPOSITIONS", []) +
    KANNADA_DIRECTION_MARKERS.get("ABLATIVE_POSTPOSITIONS", []) +
    KANNADA_DIRECTION_MARKERS.get("PAID_BY_BUSINESS_VERBS", []) +
    KANNADA_DIRECTION_MARKERS.get("PAID_BY_CUSTOMER_VERBS", []) +
    KANNADA_DIRECTION_MARKERS.get("PAYABLE_VERBS", []) +
    KANNADA_DIRECTION_MARKERS.get("RECEIVABLE_VERBS", []) +
    ["ide", "illa", "beku", "beda", "heli", "yaru", "enu", "nanage", "nanu", "duddu", "rupayi"]
)

ROMANIZED_MALAYALAM_VOCAB = set(
    list(MALAYALAM_NUMERALS.keys()) +
    list(MALAYALAM_TEMPORAL_LEXICON.keys()) +
    MALAYALAM_HONORIFICS +
    list(MALAYALAM_BUSINESS_TERMS.keys()) +
    MALAYALAM_DIRECTION_MARKERS.get("DATIVE_POSTPOSITIONS", []) +
    MALAYALAM_DIRECTION_MARKERS.get("ABLATIVE_POSTPOSITIONS", []) +
    MALAYALAM_DIRECTION_MARKERS.get("PAID_BY_BUSINESS_VERBS", []) +
    MALAYALAM_DIRECTION_MARKERS.get("PAID_BY_CUSTOMER_VERBS", []) +
    MALAYALAM_DIRECTION_MARKERS.get("PAYABLE_VERBS", []) +
    MALAYALAM_DIRECTION_MARKERS.get("RECEIVABLE_VERBS", []) +
    ["und", "illa", "venam", "parayu", "aaranu", "enthanu", "enikku", "njan", "panam", "roopa"]
)

ROMANIZED_URDU_VOCAB = set(
    list(URDU_NUMERALS.keys()) +
    list(URDU_TEMPORAL_LEXICON.keys()) +
    URDU_HONORIFICS +
    list(URDU_BUSINESS_TERMS.keys()) +
    URDU_DIRECTION_MARKERS.get("DATIVE_POSTPOSITIONS", []) +
    URDU_DIRECTION_MARKERS.get("ABLATIVE_POSTPOSITIONS", []) +
    URDU_DIRECTION_MARKERS.get("PAID_BY_BUSINESS_VERBS", []) +
    URDU_DIRECTION_MARKERS.get("PAID_BY_CUSTOMER_VERBS", []) +
    URDU_DIRECTION_MARKERS.get("PAYABLE_VERBS", []) +
    URDU_DIRECTION_MARKERS.get("RECEIVABLE_VERBS", []) +
    ["hai", "hain", "karo", "batao", "kaun", "kitna", "mujhe", "maine", "wasool", "ada"]
)

ROMANIZED_GUJARATI_VOCAB = set(
    list(GUJARATI_NUMERALS.keys()) +
    list(GUJARATI_TEMPORAL_LEXICON.keys()) +
    GUJARATI_HONORIFICS +
    list(GUJARATI_BUSINESS_TERMS.keys()) +
    GUJARATI_DIRECTION_MARKERS.get("DATIVE_POSTPOSITIONS", []) +
    GUJARATI_DIRECTION_MARKERS.get("ABLATIVE_POSTPOSITIONS", []) +
    GUJARATI_DIRECTION_MARKERS.get("PAID_BY_BUSINESS_VERBS", []) +
    GUJARATI_DIRECTION_MARKERS.get("PAID_BY_CUSTOMER_VERBS", []) +
    GUJARATI_DIRECTION_MARKERS.get("PAYABLE_VERBS", []) +
    GUJARATI_DIRECTION_MARKERS.get("RECEIVABLE_VERBS", []) +
    ["che", "nathi", "joie", "kaho", "kon", "ketla", "mane", "hve", "rupya", "roka"]
)

ENGLISH_FINANCE_VOCAB = {
    "pending", "cash", "credit", "debit", "online", "transfer", "bill", "invoice",
    "customer", "supplier", "account", "due", "paid", "received", "balance",
    "advance", "refund", "cheque", "check", "settled", "goods", "items", "discount",
    "payment", "order", "delivery", "store", "shop", "remaining", "already", "today",
    "yesterday", "tomorrow", "month", "week", "friday", "monday", "total", "clear", "record"
}

def is_telugu_char(ch: str) -> bool:
    return 0x0C00 <= ord(ch) <= 0x0C7F

def is_tamil_char(ch: str) -> bool:
    return 0x0B80 <= ord(ch) <= 0x0BFF

def is_hindi_char(ch: str) -> bool:
    return 0x0900 <= ord(ch) <= 0x097F

def is_kannada_char(ch: str) -> bool:
    return 0x0C80 <= ord(ch) <= 0x0CFF

def is_malayalam_char(ch: str) -> bool:
    return 0x0D00 <= ord(ch) <= 0x0D7F

def is_urdu_char(ch: str) -> bool:
    return 0x0600 <= ord(ch) <= 0x06FF

def is_gujarati_char(ch: str) -> bool:
    return 0x0A80 <= ord(ch) <= 0x0AFF

def classify_token(token: str) -> str:
    token_clean = token.lower().strip(",.!?\"'")
    if not token_clean:
        return "punctuation"
    if token_clean.isdigit():
        return "numeric"
        
    # Check Unicode Scripts
    if any(is_telugu_char(c) for c in token_clean):
        return "telugu_script"
    if any(is_tamil_char(c) for c in token_clean):
        return "tamil_script"
    if any(is_hindi_char(c) for c in token_clean):
        return "hindi_script"
    if any(is_kannada_char(c) for c in token_clean):
        return "kannada_script"
    if any(is_malayalam_char(c) for c in token_clean):
        return "malayalam_script"
    if any(is_urdu_char(c) for c in token_clean):
        return "urdu_script"
    if any(is_gujarati_char(c) for c in token_clean):
        return "gujarati_script"
        
    # Check Romanized Dictionaries
    if token_clean in ROMANIZED_TELUGU_VOCAB:
        return "romanized_telugu"
    if token_clean in ROMANIZED_TAMIL_VOCAB:
        return "romanized_tamil"
    if token_clean in ROMANIZED_HINDI_VOCAB:
        return "romanized_hindi"
    if token_clean in ROMANIZED_KANNADA_VOCAB:
        return "romanized_kannada"
    if token_clean in ROMANIZED_MALAYALAM_VOCAB:
        return "romanized_malayalam"
    if token_clean in ROMANIZED_URDU_VOCAB:
        return "romanized_urdu"
    if token_clean in ROMANIZED_GUJARATI_VOCAB:
        return "romanized_gujarati"
        
    # Morphology Suffixes
    for suffix in ["gariki", "nundi", "nunchi", "andi", "ichadu"]:
        if len(token_clean) > len(suffix) + 2 and token_clean.endswith(suffix):
            return "romanized_telugu"
    for suffix in ["ukku", "kku", "idam", "irundhu", "kitta", "koduthaar"]:
        if len(token_clean) > len(suffix) + 2 and token_clean.endswith(suffix):
            return "romanized_tamil"
    for suffix in ["bhaiya", "sethji", "waale", "waali", "denge", "bheja"]:
        if len(token_clean) > len(suffix) + 2 and token_clean.endswith(suffix):
            return "romanized_hindi"
    for suffix in ["avaru", "inda", "ige", "kotte", "kodabeku", "tagondidini"]:
        if len(token_clean) > len(suffix) + 2 and token_clean.endswith(suffix):
            return "romanized_kannada"
    for suffix in ["chetan", "kk", "innu", "koduthu", "tharanund"]:
        if len(token_clean) > len(suffix) + 2 and token_clean.endswith(suffix):
            return "romanized_malayalam"
    for suffix in ["sahab", "keliye", "diya", "kiya"]:
        if len(token_clean) > len(suffix) + 2 and token_clean.endswith(suffix):
            return "romanized_urdu"
    for suffix in ["bhai", "aapya", "aapvana", "levana"]:
        if len(token_clean) > len(suffix) + 2 and token_clean.endswith(suffix):
            return "romanized_gujarati"
            
    if token_clean in ENGLISH_FINANCE_VOCAB:
        return "english"
        
    return "english"


class LanguageIdentifier:
    """
    Identifies language distribution and primary language across 8 languages.
    """
    
    @staticmethod
    def identify(text: str) -> Dict[str, Any]:
        tokens = re.findall(r'[\w\u0C00-\u0C7F\u0B80-\u0BFF\u0900-\u097F\u0C80-\u0CFF\u0D00-\u0D7F\u0600-\u06FF\u0A80-\u0AFF]+', text)
        if not tokens:
            return {
                "primary_language": "unknown",
                "is_code_mixed": False,
                "token_distribution": {},
                "token_tags": [],
                "confidence": 0.0
            }
            
        token_tags = []
        counts = {
            "telugu_script": 0, "tamil_script": 0, "hindi_script": 0,
            "kannada_script": 0, "malayalam_script": 0, "urdu_script": 0, "gujarati_script": 0,
            "romanized_telugu": 0, "romanized_tamil": 0, "romanized_hindi": 0,
            "romanized_kannada": 0, "romanized_malayalam": 0, "romanized_urdu": 0, "romanized_gujarati": 0,
            "english": 0, "numeric": 0
        }
        
        for t in tokens:
            tag = classify_token(t)
            token_tags.append({"token": t, "language": tag})
            if tag in counts:
                counts[tag] += 1
                
        script_keys = [
            "telugu_script", "tamil_script", "hindi_script",
            "kannada_script", "malayalam_script", "urdu_script", "gujarati_script"
        ]
        romanized_keys = [
            "romanized_telugu", "romanized_tamil", "romanized_hindi",
            "romanized_kannada", "romanized_malayalam", "romanized_urdu", "romanized_gujarati"
        ]
        
        total_word_tokens = sum(counts[k] for k in script_keys + romanized_keys + ["english"])
        
        if total_word_tokens == 0:
            primary_lang = "numeric"
            is_mixed = False
        else:
            # Check script matches first
            script_counts = {k: counts[k] for k in script_keys}
            top_script = max(script_counts, key=script_counts.get)
            
            if script_counts[top_script] > 0 and counts["english"] > 0:
                primary_lang = f"code_mixed_{top_script.replace('_script', '')}"
                is_mixed = True
            elif script_counts[top_script] >= total_word_tokens * 0.4:
                primary_lang = top_script
                is_mixed = counts["english"] > 0
            else:
                romanized_counts = {k: counts[k] for k in romanized_keys}
                top_romanized = max(romanized_counts, key=romanized_counts.get)
                
                if romanized_counts[top_romanized] > 0 and counts["english"] > 0:
                    primary_lang = f"code_mixed_{top_romanized.replace('romanized_', '')}"
                    is_mixed = True
                elif romanized_counts[top_romanized] >= total_word_tokens * 0.35:
                    primary_lang = top_romanized
                    is_mixed = counts["english"] > 0
                else:
                    primary_lang = "english"
                    is_mixed = any(counts[k] > 0 for k in script_keys + romanized_keys)
                
        confidence = 0.94 if is_mixed else 0.98
        
        return {
            "primary_language": primary_lang,
            "is_code_mixed": is_mixed,
            "token_counts": counts,
            "token_tags": token_tags,
            "confidence": confidence
        }

language_identifier = LanguageIdentifier()
