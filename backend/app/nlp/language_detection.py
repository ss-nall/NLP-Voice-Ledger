"""
Language Identification Module.
Identifies sentence-level and token-level language:
- 'telugu_script' (Unicode Telugu: 0x0C00 - 0x0C7F)
- 'romanized_telugu' (Telugu words written in Latin script: e.g., 'ivvali', 'ninna', 'ichadu')
- 'english' (English words: e.g., 'pending', 'transfer', 'supplier', 'cash', 'bill')
- 'code_mixed' (Sentences combining Telugu and English)
"""

import re
from typing import Dict, Any, List
from backend.app.nlp.telugu_lexicon import (
    TELUGU_NUMERALS, DIRECTION_MARKERS, TEMPORAL_LEXICON, DAYS_OF_WEEK,
    TELUGU_HONORIFICS, BUSINESS_TERMS
)

# Set of common Romanized Telugu keywords
ROMANIZED_TELUGU_VOCAB = set(
    list(TELUGU_NUMERALS.keys()) +
    list(TEMPORAL_LEXICON.keys()) +
    list(DAYS_OF_WEEK.keys()) +
    TELUGU_HONORIFICS +
    list(BUSINESS_TERMS.keys()) +
    DIRECTION_MARKERS["PAYABLE_POSTPOSITIONS"] +
    DIRECTION_MARKERS["RECEIVABLE_POSTPOSITIONS"] +
    DIRECTION_MARKERS["PAYABLE_VERBS"] +
    DIRECTION_MARKERS["RECEIVABLE_VERBS"] +
    DIRECTION_MARKERS["PAID_BY_CUSTOMER_VERBS"] +
    DIRECTION_MARKERS["PAID_BY_BUSINESS_VERBS"] +
    DIRECTION_MARKERS["PROMISE_VERBS"] +
    [
        "undi", "unna", "unnayi", "kavali", "cheppu", "enti", "entha", "evaru", "naaku", "nenu",
        "chesa", "chesam", "chesanu", "chesadu", "chesindi", "chesaru", "cheyyaledu", "kaledu",
        "lekapothe", "mottam", "annadu", "annanu", "cheppadu", "cheppanu", "pettadu", "teesuko",
        "dabbulu", "rupailu", "rupayalu", "chillara", "baki", "udhari", "saraku", "konna"
    ]
)

# Common English finance words
ENGLISH_FINANCE_VOCAB = {
    "pending", "cash", "credit", "debit", "online", "transfer", "bill", "invoice",
    "customer", "supplier", "account", "due", "paid", "received", "balance",
    "advance", "refund", "cheque", "check", "settled", "goods", "items", "discount",
    "payment", "order", "delivery", "store", "shop", "remaining", "already", "today",
    "yesterday", "tomorrow", "month", "week", "friday", "monday", "total", "clear"
}

def is_telugu_char(ch: str) -> bool:
    """Checks if a character falls within the Unicode Telugu block."""
    code = ord(ch)
    return 0x0C00 <= code <= 0x0C7F

def classify_token(token: str) -> str:
    """Classifies a single token into its language category."""
    token_clean = token.lower().strip(",.!?\"'")
    if not token_clean:
        return "punctuation"
        
    if token_clean.isdigit():
        return "numeric"
        
    # Check if character has Telugu script
    if any(is_telugu_char(c) for c in token_clean):
        return "telugu_script"
        
    # Check Romanized Telugu vocabulary
    if token_clean in ROMANIZED_TELUGU_VOCAB:
        return "romanized_telugu"
        
    # Common Telugu morphology suffixes
    for suffix in ["ki", "ku", "nundi", "nunchi", "tho", "lo", "ga", "adu", "anu", "aru", "aaru", "andi", "adu", "edi"]:
        if len(token_clean) > len(suffix) + 2 and token_clean.endswith(suffix):
            return "romanized_telugu"
            
    # Check English vocabulary
    if token_clean in ENGLISH_FINANCE_VOCAB:
        return "english"
        
    return "english"  # Default latin token fallback


class LanguageIdentifier:
    """
    Identifies language distribution, primary matrix language, and code-mixed classification.
    """
    
    @staticmethod
    def identify(text: str) -> Dict[str, Any]:
        tokens = re.findall(r'[\w\u0C00-\u0C7F]+', text)
        if not tokens:
            return {
                "primary_language": "unknown",
                "is_code_mixed": False,
                "token_distribution": {},
                "token_tags": [],
                "confidence": 0.0
            }
            
        token_tags = []
        counts = {"telugu_script": 0, "romanized_telugu": 0, "english": 0, "numeric": 0}
        
        for t in tokens:
            tag = classify_token(t)
            token_tags.append({"token": t, "language": tag})
            if tag in counts:
                counts[tag] += 1
                
        total_word_tokens = sum(counts[k] for k in ["telugu_script", "romanized_telugu", "english"])
        if total_word_tokens == 0:
            primary_lang = "numeric"
            is_mixed = False
        else:
            # Check script first
            if counts["telugu_script"] > 0 and counts["english"] > 0:
                primary_lang = "code_mixed_script"
                is_mixed = True
            elif counts["telugu_script"] >= total_word_tokens * 0.7:
                primary_lang = "telugu_script"
                is_mixed = counts["english"] > 0
            elif counts["romanized_telugu"] > 0 and counts["english"] > 0:
                primary_lang = "code_mixed_romanized"
                is_mixed = True
            elif counts["romanized_telugu"] >= total_word_tokens * 0.5:
                primary_lang = "romanized_telugu"
                is_mixed = counts["english"] > 0
            else:
                primary_lang = "english"
                is_mixed = counts["romanized_telugu"] > 0 or counts["telugu_script"] > 0
                
        confidence = 0.92 if is_mixed else 0.97
        
        return {
            "primary_language": primary_lang,
            "is_code_mixed": is_mixed,
            "token_counts": counts,
            "token_tags": token_tags,
            "confidence": confidence
        }

# Global singleton
language_identifier = LanguageIdentifier()
