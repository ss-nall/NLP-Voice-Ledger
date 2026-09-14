"""
Transliteration & Phonetic Normalization Engine.
Normalizes informal Romanized Telugu spelling variants while retaining verbatim raw spans.
Implements Indic phonetic soundex for entity matching.
"""

import re
from typing import Dict, Any, List, Tuple

# Phonetic normalization lookup dictionary
PHONETIC_CANONICAL_MAP: Dict[str, str] = {
    # Payable variants
    "ivvaali": "ivvali", "ivvalI": "ivvali", "ivvalira": "ivvali", "ivvalsi": "ivvali",
    "ivaali": "ivvali", "ivali": "ivvali", "ivaalira": "ivvali",
    "ivvalsindi": "ivvali", "evvali": "ivvali", "evali": "ivvali", "eeyali": "ivvali", "eeyyali": "ivvali", "kattali": "kattali",
    "kattalsindi": "kattali", "kattaali": "kattali", "kattalira": "kattali",
    
    # Receivable variants
    "raavali": "ravali", "ravalsi": "ravali", "ravalsindi": "ravali", "teesukovali": "teesukovali",
    "teeskovali": "teesukovali", "theeskovali": "teesukovali", "ravanundi": "ravali", "ravalee": "ravali",
    
    # Paid variants
    "ichadu": "ichadu", "ichesthadu": "ichadu", "ichesadu": "ichesadu", "icheysadu": "ichesadu", "ichindhi": "ichindi",
    "ichaanu": "ichanu", "icheysa": "ichesa", "ichesanu": "ichesa", "ichestha": "ichesa", "ichharu": "icharu",
    "pampaadu": "pampadu", "pampa": "pampanu", "pampinchadu": "pampadu",
    "kattadu": "kattadu", "katta": "kattanu", "kattesa": "kattanu", "kattesanu": "kattanu",
    
    # Promise variants
    "istanu": "istanu", "istha": "istanu", "isthanu": "istanu", "isthanannadu": "istanu annadu",
    "isthannadu": "istanu annadu", "isthadu": "istanu annadu",
    
    # Numeral phonetic variants (for Indian accents)
    "thouzad": "thousand", "thouzand": "thousand", "thoujand": "thousand", "thoujan": "thousand",
    "towjand": "thousand", "taujand": "thousand", "tauzand": "thousand", "tauzan": "thousand",
    "tozand": "thousand", "towzand": "thousand", "thousend": "thousand", "thousan": "thousand",
    "hunderd": "hundred", "hondred": "hundred", "handred": "hundred", "hundered": "hundred",
    "lakha": "lakh", "laakh": "lakh", "krore": "crore", "krores": "crores",
    "wandalu": "vandalu", "wandhalu": "vandhalu", "wanda": "vanda",
    
    # Temporal variants
    "ninna": "ninna", "ninnaa": "ninna", "ninne": "ninna",
    "monna": "monna", "monne": "monna",
    "repu": "repu", "repuu": "repu",
    "ellundi": "ellundi", "yelundi": "ellundi",
    "vache": "vache", "vacche": "vache", "vachey": "vache", "vachee": "vache",
    "vaaram": "vaaram", "varam": "vaaram", "vaaramu": "vaaram",
    "nela": "nela", "nelalo": "nela",
    
    # Currency / Money variants
    "dabbulu": "rupayalu", "rupailu": "rupayalu", "roopayalu": "rupayalu", "rupees": "rupayalu",
    "chillara": "chillara",
    
    # Trade / Settlement
    "completega": "complete ga", "motham": "motham", "mottham": "motham",
    "saraku": "saraku", "samanu": "saman", "maal": "saraku"
}

def indic_phonetic_fingerprint(name: str) -> str:
    """
    Computes a phonetic fingerprint adapted for South Asian / Indic names.
    Groups phonetically interchangeable letters (s/sh, b/v, th/t, d/dh, ee/i, oo/u)
    and harmonizes Telugu noun vowel additions (-u, -a).
    """
    s = name.lower().strip()
    s = re.sub(r'[^a-z]', '', s)
    if not s:
        return ""
        
    # Replacements
    s = s.replace("sh", "s").replace("sch", "s").replace("ch", "c")
    s = s.replace("ee", "i").replace("ea", "i").replace("y", "i")
    s = s.replace("oo", "u").replace("ou", "u")
    s = s.replace("ph", "f").replace("bh", "b").replace("v", "w")
    s = s.replace("th", "t").replace("dh", "d").replace("kh", "k").replace("gh", "g")
    
    # Strip trailing noun case vowel addition in Telugu transliterations (e.g. 'rameshu' -> 'ramesh')
    if len(s) > 4 and s.endswith('u'):
        s = s[:-1]
        
    # Collapse consecutive duplicate letters
    s = re.sub(r'(.)\1+', r'\1', s)
    return s


class PhoneticNormalizer:
    """
    Normalizes Romanized Telugu text into standard canonical forms
    while tracking modifications.
    """
    
    @staticmethod
    def normalize(text: str) -> Dict[str, Any]:
        raw_words = text.split()
        normalized_words = []
        changes = []
        
        for idx, word in enumerate(raw_words):
            # Strip punctuation for lookup
            clean = re.sub(r'[^\w\u0C00-\u0C7F]', '', word).lower()
            
            if clean in PHONETIC_CANONICAL_MAP:
                norm = PHONETIC_CANONICAL_MAP[clean]
                normalized_words.append(norm)
                if norm != clean:
                    changes.append({
                        "original": word,
                        "normalized": norm,
                        "position": idx
                    })
            else:
                normalized_words.append(word)
                
        normalized_text = " ".join(normalized_words)
        return {
            "original_text": text,
            "normalized_text": normalized_text,
            "has_changes": len(changes) > 0,
            "changes": changes
        }

def split_telugu_sandhi(text: str) -> str:
    """
    Normalizes Telugu verb-numeral and postposition agglutinated sandhi tokens
    into distinct grammatical components.
    Examples:
      - 'పదివేలిచ్చాడు' -> 'పదివేలు ఇచ్చాడు'
      - '50,000ఇచ్చేశాను' -> '50,000 ఇచ్చేశాను'
      - 'నాకిచ్చాడు' -> 'నాకు ఇచ్చాడు'
      - 'దీపక్కిచ్చాను' -> 'దీపక్ కి ఇచ్చాను'
      - 'ప్రేమ్కిచ్చాను' -> 'ప్రేమ్ కి ఇచ్చాను'
      - 'padivelichadu' -> 'padi velu ichadu'
    """
    if not text:
        return ""
        
    s = text
    # 0. Digits / formatted numbers directly attached to verbs (e.g. 50,000ఇచ్చేశాను, 500ఇచ్చాడు)
    s = re.sub(r'(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+)ఇచ్చా(డు|రు|ను|ము|ం|యి|సింది)?\b', r'\1 ఇచ్చా\2', s)
    s = re.sub(r'(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+)ఇచ్చే(సాడు|శాడు|సారు|శారు|సాను|శాను|సింది|శాం|సాం)?\b', r'\1 ఇచ్చే\2', s)
    s = re.sub(r'(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+)ఇవ్వాలి\b', r'\1 ఇవ్వాలి', s)
    s = re.sub(r'(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+)రావాలి\b', r'\1 రావాలి', s)

    # 1. Numeral + Verb Sandhi (Telugu script)
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)వేలిచ్చా(డు|రు|ను|ము|ం|యి|సింది|రంట|నంట)?\b', r'\1వేలు ఇచ్చా\2', s)
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)వేలిచ్చే(సాడు|శాడు|సారు|శారు|సాను|శాను|సింది|శాం|సాం)?\b', r'\1వేలు ఇచ్చే\2', s)
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)వందలిచ్చా(డు|రు|ను|ము|ం|యి|సింది)?\b', r'\1వందలు ఇచ్చా\2', s)
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)వందలిచ్చే(సాడు|శాడు|సారు|శారు|సాను|శాను|సింది|శాం|సాం)?\b', r'\1వందలు ఇచ్చే\2', s)
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)లక్షలిచ్చా(డు|రు|ను|ము|ం|యి|సింది)?\b', r'\1లక్షలు ఇచ్చా\2', s)
    
    # 2. Romanized equivalents
    s = re.sub(r'\b([a-zA-Z]+)velicha(du|ru|nu|mu|m|y|sindi)?\b', r'\1 velu icha\2', s, flags=re.IGNORECASE)
    s = re.sub(r'\b([a-zA-Z]+)veliches(adu|aru|anu|am|indi)?\b', r'\1 velu iches\2', s, flags=re.IGNORECASE)
    s = re.sub(r'\b([a-zA-Z]+)vandalicha(du|ru|nu|mu|m|y|sindi)?\b', r'\1 vandalu icha\2', s, flags=re.IGNORECASE)
    s = re.sub(r'\b([a-zA-Z]+)lakshalicha(du|ru|nu|mu|m|y|sindi)?\b', r'\1 lakshalu icha\2', s, flags=re.IGNORECASE)

    # 3. Pronoun + Verb Sandhis (నాకు + ఇచ్చాడు -> నాకిచ్చాడు, etc.)
    s = re.sub(r'\bనాకిచ్చా(డు|రు|ను|ము|ం|సింది)?\b', r'నాకు ఇచ్చా\1', s)
    s = re.sub(r'\bనాకిచ్చే(సాడు|శాడు|సారు|శారు|సాను|శాను|సింది|శాం|సాం)?\b', r'నాకు ఇచ్చే\1', s)
    s = re.sub(r'\bనాకొచ్చిం(ది|దిరా)?\b', r'నాకు వచ్చింది', s)
    s = re.sub(r'\bనాకివ్వాలి\b', r'నాకు ఇవ్వాలి', s)
    s = re.sub(r'\bనాకురావాలి\b', r'నాకు రావాలి', s)

    # 4. Postposition + Verb Sandhis & Entity + Postposition Sandhis
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)కిచ్చా(డు|ను|రు|ము|ం|సింది)?\b', r'\1 కి ఇచ్చా\2', s)
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)కిచ్చే(సాడు|శాడు|సారు|శారు|సాను|శాను|సింది|శాం|సాం)?\b', r'\1 కి ఇచ్చే\2', s)
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)కివ్వాలి\b', r'\1 కి ఇవ్వాలి', s)
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)కియ్యాలి\b', r'\1 కి ఇవ్వాలి', s)
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)నుండిరావాలి\b', r'\1 నుండి రావాలి', s)
    
    return s


# Curated Name Lexicon for High-Accuracy South Asian / Telugu Transliteration
NAME_TRANSLITERATION_MAP: Dict[str, Dict[str, str]] = {
    "prem": {"en": "Prem", "te": "ప్రేమ్"},
    "ప్రేమ్": {"en": "Prem", "te": "ప్రేమ్"},
    "deepak": {"en": "Deepak", "te": "దీపక్"},
    "దీపక్": {"en": "Deepak", "te": "దీపక్"},
    "sathvik": {"en": "Sathvik", "te": "సాత్విక్"},
    "satwik": {"en": "Sathvik", "te": "సాత్విక్"},
    "సాత్విక్": {"en": "Sathvik", "te": "సాత్విక్"},
    "pavan": {"en": "Pavan", "te": "పవన్"},
    "పవన్": {"en": "Pavan", "te": "పవన్"},
    "రమేష్": {"en": "Ramesh", "te": "రమేష్"},
    "ramesh": {"en": "Ramesh", "te": "రమేష్"},
    "సురేష్": {"en": "Suresh", "te": "సురేష్"},
    "suresh": {"en": "Suresh", "te": "సురేష్"},
    "కిరణ్": {"en": "Kiran", "te": "కిరణ్"},
    "kiran": {"en": "Kiran", "te": "కిరణ్"},
    "మహేష్": {"en": "Mahesh", "te": "మహేష్"},
    "mahesh": {"en": "Mahesh", "te": "మహేష్"},
    "నరేష్": {"en": "Naresh", "te": "నరేష్"},
    "naresh": {"en": "Naresh", "te": "నరేష్"},
    "రాజేష్": {"en": "Rajesh", "te": "రాజేష్"},
    "rajesh": {"en": "Rajesh", "te": "రాజేష్"},
    "వెంకటేష్": {"en": "Venkatesh", "te": "వెంకటేష్"},
    "venkatesh": {"en": "Venkatesh", "te": "వెంకటేష్"},
    "సంతోష్": {"en": "Santosh", "te": "సంతోష్"},
    "santosh": {"en": "Santosh", "te": "సంతోష్"},
    "లక్ష్మి": {"en": "Lakshmi", "te": "లక్ష్మి"},
    "lakshmi": {"en": "Lakshmi", "te": "లక్ష్మి"},
    "బాలాజీ": {"en": "Balaji", "te": "బాలాజీ"},
    "balaji": {"en": "Balaji", "te": "బాలాజీ"},
    "గోపాల్": {"en": "Gopal", "te": "గోపాల్"},
    "gopal": {"en": "Gopal", "te": "గోపాల్"},
    "రవి": {"en": "Ravi", "te": "రవి"},
    "ravi": {"en": "Ravi", "te": "రవి"},
    "సతీష్": {"en": "Satish", "te": "సతీష్"},
    "satish": {"en": "Satish", "te": "సతీష్"},
    "శ్రీనివాస్": {"en": "Srinivas", "te": "శ్రీనివాస్"},
    "srinivas": {"en": "Srinivas", "te": "శ్రీనివాస్"},
    "ప్రసాద్": {"en": "Prasad", "te": "ప్రసాద్"},
    "prasad": {"en": "Prasad", "te": "ప్రసాద్"},
    "ప్రవీణ్": {"en": "Praveen", "te": "ప్రవీణ్"},
    "praveen": {"en": "Praveen", "te": "ప్రవీణ్"},
    "కార్తీక్": {"en": "Karthik", "te": "కార్తీక్"},
    "karthik": {"en": "Karthik", "te": "కార్తీక్"},
    "అజయ్": {"en": "Ajay", "te": "అజయ్"},
    "ajay": {"en": "Ajay", "te": "అజయ్"},
    "విజయ్": {"en": "Vijay", "te": "విజయ్"},
    "vijay": {"en": "Vijay", "te": "విజయ్"},
    "ఆనంద్": {"en": "Anand", "te": "ఆనంద్"},
    "anand": {"en": "Anand", "te": "ఆనంద్"},
    "సునీల్": {"en": "Sunil", "te": "సునీల్"},
    "sunil": {"en": "Sunil", "te": "సునీల్"},
    "అనిల్": {"en": "Anil", "te": "అనిల్"},
    "anil": {"en": "Anil", "te": "అనిల్"},
    "మోహన్": {"en": "Mohan", "te": "మోహన్"},
    "mohan": {"en": "Mohan", "te": "మోహన్"},
    "గణేష్": {"en": "Ganesh", "te": "గణేష్"},
    "ganesh": {"en": "Ganesh", "te": "గణేష్"},
    "కృష్ణ": {"en": "Krishna", "te": "కృష్ణ"},
    "krishna": {"en": "Krishna", "te": "కృష్ణ"},
    "సాయి": {"en": "Sai", "te": "సాయి"},
    "sai": {"en": "Sai", "te": "సాయి"},
    "సీత": {"en": "Sita", "te": "సీత"},
    "sita": {"en": "Sita", "te": "సీత"},
    "రాధ": {"en": "Radha", "te": "రాధ"},
    "radha": {"en": "Radha", "te": "రాధ"},
    "సప్లయర్": {"en": "Supplier", "te": "సప్లయర్"},
    "supplier": {"en": "Supplier", "te": "సప్లయర్"},
    "కస్టమర్": {"en": "Customer", "te": "కస్టమర్"},
    "customer": {"en": "Customer", "te": "కస్టమర్"},
    "శ్రీ లక్ష్మి ట్రేడర్స్": {"en": "Sri Lakshmi Traders", "te": "శ్రీ లక్ష్మి ట్రేడర్స్"},
    "sri lakshmi traders": {"en": "Sri Lakshmi Traders", "te": "శ్రీ లక్ష్మి ట్రేడర్స్"},
    "బాలాజీ కిరాణా": {"en": "Balaji Kirana", "te": "బాలాజీ కిరాణా"},
    "balaji kirana": {"en": "Balaji Kirana", "te": "బాలాజీ కిరాణా"},
}

TELUGU_VOWELS = {
    '\u0C05': 'a', '\u0C06': 'aa', '\u0C07': 'i', '\u0C08': 'ee', '\u0C09': 'u', '\u0C0A': 'oo', '\u0C0B': 'ru',
    '\u0C0E': 'e', '\u0C0F': 'e', '\u0C10': 'ai', '\u0C12': 'o', '\u0C13': 'o', '\u0C14': 'au'
}
TELUGU_CONSONANTS = {
    '\u0C15': 'k', '\u0C16': 'kh', '\u0C17': 'g', '\u0C18': 'gh', '\u0C19': 'ng',
    '\u0C1A': 'ch', '\u0C1B': 'chh', '\u0C1C': 'j', '\u0C1D': 'jh', '\u0C1E': 'ny',
    '\u0C1F': 't', '\u0C20': 'th', '\u0C21': 'd', '\u0C22': 'dh', '\u0C23': 'n',
    '\u0C24': 'th', '\u0C25': 'th', '\u0C26': 'd', '\u0C27': 'dh', '\u0C28': 'n',
    '\u0C2A': 'p', '\u0C2B': 'ph', '\u0C2C': 'b', '\u0C2D': 'bh', '\u0C2E': 'm',
    '\u0C2F': 'y', '\u0C30': 'r', '\u0C31': 'r', '\u0C32': 'l', '\u0C33': 'l', '\u0C35': 'v',
    '\u0C36': 'sh', '\u0C37': 'sh', '\u0C38': 's', '\u0C39': 'h'
}
TELUGU_MATRAS = {
    '\u0C3E': 'aa', '\u0C3F': 'i', '\u0C40': 'ee', '\u0C41': 'u', '\u0C42': 'oo', '\u0C43': 'ru',
    '\u0C46': 'e', '\u0C47': 'e', '\u0C48': 'ai', '\u0C4A': 'o', '\u0C4B': 'o', '\u0C4C': 'au',
    '\u0C02': 'm', '\u0C03': 'h'
}
VIRAMA = '\u0C4D'

def telugu_to_english_phonetic(text: str) -> str:
    """
    Converts any Telugu Unicode script text into readable, natural Romanized English.
    """
    words = text.split()
    converted_words = []
    
    for word in words:
        w_lower = word.lower()
        if w_lower in NAME_TRANSLITERATION_MAP:
            converted_words.append(NAME_TRANSLITERATION_MAP[w_lower]["en"])
            continue
            
        out = []
        chars = list(word)
        n = len(chars)
        idx = 0
        
        while idx < n:
            ch = chars[idx]
            
            if ch in TELUGU_VOWELS:
                out.append(TELUGU_VOWELS[ch])
                idx += 1
            elif ch in TELUGU_CONSONANTS:
                cons = TELUGU_CONSONANTS[ch]
                # Check next character
                if idx + 1 < n:
                    next_ch = chars[idx + 1]
                    if next_ch == VIRAMA:
                        out.append(cons)
                        idx += 2
                    elif next_ch in TELUGU_MATRAS:
                        out.append(cons + TELUGU_MATRAS[next_ch])
                        idx += 2
                    else:
                        out.append(cons + 'a')
                        idx += 1
                else:
                    out.append(cons)
                    idx += 1
            elif ch in TELUGU_MATRAS:
                out.append(TELUGU_MATRAS[ch])
                idx += 1
            else:
                out.append(ch)
                idx += 1
                
        res = "".join(out)
        res = re.sub(r'aa+', 'a', res)
        res = re.sub(r'ee+', 'ee', res)
        res = re.sub(r'oo+', 'oo', res)
        converted_words.append(res.title() if not res.isupper() else res)
        
    return " ".join(converted_words)


def english_to_telugu_phonetic(text: str) -> str:
    """
    Converts Romanized English names to Telugu script.
    """
    clean_lower = text.strip().lower()
    if clean_lower in NAME_TRANSLITERATION_MAP:
        return NAME_TRANSLITERATION_MAP[clean_lower]["te"]
        
    te_syllables = {
        "dee": "దీ", "pa": "ప", "k": "క్", "sa": "సా", "thvi": "త్వి", "twi": "త్వి",
        "va": "వ", "n": "న్", "ra": "ర", "me": "మే", "sh": "ష్",
        "su": "సు", "re": "రే", "ki": "కి", "ran": "రణ్", "ma": "మ", "he": "హే",
        "na": "న", "ga": "గ", "ne": "నే", "la": "ల", "kshi": "క్షి", "ba": "బా",
        "ji": "జీ", "go": "గో", "pal": "పాల్", "ti": "తీ", "ka": "కా", "rthi": "ర్తీ"
    }
    te_cand = text.title()
    for k, v in te_syllables.items():
        te_cand = re.sub(k, v, te_cand, flags=re.IGNORECASE)
    return te_cand if any('\u0C00' <= c <= '\u0C7F' for c in te_cand) else text


def get_bilingual_names(name: str) -> Dict[str, str]:
    """
    Returns high-quality English, Telugu, and combined display name
    for any actor / counterparty.
    - If given Telugu script (e.g. 'దీపక్'): returns display 'దీపక్ (Deepak)'
    - If given English (e.g. 'Deepak'): returns display 'Deepak (దీపక్)'
    """
    if not name or name.strip() in ["", "Unspecified", "Unknown"]:
        return {"english": "Unspecified", "telugu": "పేరు పేర్కొనబడలేదు", "display": "Unspecified"}
        
    clean = name.strip()
    clean_lower = clean.lower()
    
    # 1. Direct dictionary match
    if clean_lower in NAME_TRANSLITERATION_MAP:
        info = NAME_TRANSLITERATION_MAP[clean_lower]
        is_telugu_input = any('\u0C00' <= char <= '\u0C7F' for char in clean)
        display = f"{info['te']} ({info['en']})" if is_telugu_input else f"{info['en']} ({info['te']})"
        return {
            "english": info["en"],
            "telugu": info["te"],
            "display": display
        }
        
    # 2. Check if Telugu script input
    is_telugu_script = any('\u0C00' <= char <= '\u0C7F' for char in clean)
    if is_telugu_script:
        en_cand = telugu_to_english_phonetic(clean)
        return {
            "english": en_cand,
            "telugu": clean,
            "display": f"{clean} ({en_cand})"
        }
    else:
        en_name = clean.title()
        te_cand = english_to_telugu_phonetic(en_name)
        return {
            "english": en_name,
            "telugu": te_cand,
            "display": f"{en_name} ({te_cand})" if any('\u0C00' <= c <= '\u0C7F' for c in te_cand) else en_name
        }


# Global singleton
phonetic_normalizer = PhoneticNormalizer()

