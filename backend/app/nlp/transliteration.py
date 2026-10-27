"""
Multi-Lingual Transliteration, Name Resolution & Phonetic Normalization Engine.
Supports Romanized Indic, Telugu, Tamil, and Hindi canonical mappings,
bilingual display formatting (e.g. 'Pavan (పవన్)', 'முருகன் (Murugan)', 'राहुल (Rahul)'),
and Sandhi decomposition across scripts.
"""

import re
from typing import Dict, Any, List, Tuple, Optional

# Name transliteration cross-reference table across English, Telugu, Tamil, and Hindi
INDIC_NAME_TABLE: Dict[str, Dict[str, str]] = {
    "pavan": {"english": "Pavan", "telugu": "పవన్", "tamil": "பவன்", "hindi": "पवन"},
    "deepak": {"english": "Deepak", "telugu": "దీపక్", "tamil": "தீபக்", "hindi": "दीपक"},
    "sathvik": {"english": "Sathvik", "telugu": "సాత్విక్", "tamil": "சாத்விக்", "hindi": "सात्विक"},
    "sathwik": {"english": "Sathwik", "telugu": "సాత్విక్", "tamil": "சாத்விக்", "hindi": "सात्विक"},
    "prem": {"english": "Prem", "telugu": "ప్రేమ్", "tamil": "பிரேம்", "hindi": "प्रेम"},
    "ramesh": {"english": "Ramesh", "telugu": "రమేష్", "tamil": "ரமேஷ்", "hindi": "रमेश"},
    "suresh": {"english": "Suresh", "telugu": "సురేష్", "tamil": "சுரேஷ்", "hindi": "सुरेश"},
    "mahesh": {"english": "Mahesh", "telugu": "మహేష్", "tamil": "மகேஷ்", "hindi": "महेश"},
    "venkat": {"english": "Venkat", "telugu": "వెంకట్", "tamil": "வெங்கட்", "hindi": "वेंकट"},
    "lakshmi": {"english": "Lakshmi", "telugu": "లక్ష్మి", "tamil": "லட்சுமி", "hindi": "लक्ष्मी"},
    "priya": {"english": "Priya", "telugu": "ప్రియ", "tamil": "பிரியா", "hindi": "प्रिया"},
    "rajesh": {"english": "Rajesh", "telugu": "రాజేష్", "tamil": "ராஜேஷ்", "hindi": "राजेश"},
    "krishna": {"english": "Krishna", "telugu": "కృష్ణ", "tamil": "கிருஷ்ணா", "hindi": "कृष्णा"},
    "ravi": {"english": "Ravi", "telugu": "రవి", "tamil": "ரவி", "hindi": "रवि"},
    "anand": {"english": "Anand", "telugu": "ఆనంద్", "tamil": "ஆனந்த்", "hindi": "आनंद"},
    "naresh": {"english": "Naresh", "telugu": "నరేష్", "tamil": "நரேஷ்", "hindi": "नरेश"},
    "kiran": {"english": "Kiran", "telugu": "కిరణ్", "tamil": "கிரண்", "hindi": "किरण"},
    "murugan": {"english": "Murugan", "telugu": "మురుగన్", "tamil": "முருகன்", "hindi": "मुरुगन"},
    "selvam": {"english": "Selvam", "telugu": "సెల్వం", "tamil": "செல்வம்", "hindi": "सेलवम"},
    "kavitha": {"english": "Kavitha", "telugu": "కవిత", "tamil": "கவிதா", "hindi": "कविता"},
    "senthil": {"english": "Senthil", "telugu": "సెంథిల్", "tamil": "செந்தில்", "hindi": "सेंथिल"},
    "karthik": {"english": "Karthik", "telugu": "కార్తీక్", "tamil": "கார்த்திக்", "hindi": "कार्तिक"},
    "praveen": {"english": "Praveen", "telugu": "ప్రవీణ్", "tamil": "பிரவீன்", "hindi": "प्रवीण"},
    "rahul": {"english": "Rahul", "telugu": "రాహుల్", "tamil": "ராகுல்", "hindi": "राहुल"},
    "amit": {"english": "Amit", "telugu": "అమిత్", "tamil": "அமித்", "hindi": "अमित"},
    "vikram": {"english": "Vikram", "telugu": "విక్రమ్", "tamil": "விக்ரம்", "hindi": "विक्रम"},
    "rohit": {"english": "Rohit", "telugu": "రోహిత్", "tamil": "ரோஹித்", "hindi": "रोहित"},
    "sunil": {"english": "Sunil", "telugu": "సునీల్", "tamil": "சுனில்", "hindi": "सुनील"},
    "manoj": {"english": "Manoj", "telugu": "మనోజ్", "tamil": "மனோஜ்", "hindi": "मनोज"}
}

# Inverted Script Lookup Table
SCRIPT_TO_NAME_KEY: Dict[str, str] = {}
for key, mapping in INDIC_NAME_TABLE.items():
    if key.lower() not in SCRIPT_TO_NAME_KEY:
        SCRIPT_TO_NAME_KEY[key.lower()] = key
    for lang, val in mapping.items():
        val_clean = val.strip().lower()
        if val_clean not in SCRIPT_TO_NAME_KEY:
            SCRIPT_TO_NAME_KEY[val_clean] = key

def get_bilingual_names(name: str) -> Dict[str, str]:
    """
    Returns normalized cross-script and bilingual name representations with formatted display string.
    e.g.
      'Pavan' -> {'english': 'Pavan', 'telugu': 'పవన్', 'tamil': 'பவன்', 'hindi': 'पवन', 'display': 'Pavan (పవన్)'}
      'పవన్' -> {'english': 'Pavan', 'telugu': 'పవన్', 'display': 'పవన్ (Pavan)'}
      'முருகன்' -> {'english': 'Murugan', 'tamil': 'முருகன்', 'display': 'முருகன் (Murugan)'}
      'राहुल' -> {'english': 'Rahul', 'hindi': 'राहुल', 'display': 'राहुल (Rahul)'}
    """
    clean = name.strip()
    clean_lower = clean.lower()
    
    # Strip existing bracketed names
    clean_no_brackets = re.sub(r'\(.*?\)', '', clean).strip()
    clean_key = clean_no_brackets.lower()
    
    matched_key = SCRIPT_TO_NAME_KEY.get(clean_key)
    
    # Check if input is in Telugu, Tamil, Hindi, or Latin script
    is_telugu = any(0x0C00 <= ord(c) <= 0x0C7F for c in clean)
    is_tamil = any(0x0B80 <= ord(c) <= 0x0BFF for c in clean)
    is_hindi = any(0x0900 <= ord(c) <= 0x097F for c in clean)
    
    if matched_key and matched_key in INDIC_NAME_TABLE:
        entry = INDIC_NAME_TABLE[matched_key]
        en_name = entry["english"]
        te_name = entry["telugu"]
        ta_name = entry["tamil"]
        hi_name = entry["hindi"]
        
        if is_telugu:
            display = f"{clean_no_brackets} ({en_name})"
        elif is_tamil:
            display = f"{clean_no_brackets} ({en_name})"
        elif is_hindi:
            display = f"{clean_no_brackets} ({en_name})"
        else:
            display = f"{en_name} ({te_name})"
            
        return {
            "english": en_name,
            "telugu": te_name,
            "tamil": ta_name,
            "hindi": hi_name,
            "display": display
        }
    else:
        # Fallback for dynamic/unregistered names
        if is_telugu or is_tamil or is_hindi:
            display = clean_no_brackets
            return {
                "english": clean_no_brackets,
                "telugu": clean_no_brackets if is_telugu else "",
                "tamil": clean_no_brackets if is_tamil else "",
                "hindi": clean_no_brackets if is_hindi else "",
                "display": display
            }
        else:
            title_name = clean_no_brackets.title()
            return {
                "english": title_name,
                "telugu": title_name,
                "tamil": title_name,
                "hindi": title_name,
                "display": title_name
            }

# Phonetic canonical lookup dictionary
PHONETIC_CANONICAL_MAP: Dict[str, str] = {
    # Telugu
    "ivvaali": "ivvali", "ivvalI": "ivvali", "ivvalira": "ivvali", "ivvalsi": "ivvali",
    "ivaali": "ivvali", "ivali": "ivvali", "ivaalira": "ivvali", "ivvalsindi": "ivvali",
    "evvali": "ivvali", "evali": "ivvali", "eeyali": "ivvali", "eeyyali": "ivvali",
    "kattali": "kattali", "kattalsindi": "kattali", "kattaali": "kattali",
    "raavali": "ravali", "ravalsi": "ravali", "ravalsindi": "ravali", "teesukovali": "teesukovali",
    "teeskovali": "teesukovali", "theeskovali": "teesukovali", "ravanundi": "ravali",
    "ichadu": "ichadu", "ichesthadu": "ichadu", "ichesadu": "ichesadu", "icheysadu": "ichesadu", "ichindhi": "ichindi",
    "ichaanu": "ichanu", "icheysa": "ichesa", "ichesanu": "ichesa", "ichestha": "ichesa", "ichharu": "icharu",
    "pampaadu": "pampadu", "pampa": "pampanu", "pampinchadu": "pampadu",
    "kattadu": "kattadu", "katta": "kattanu", "kattesa": "kattanu",
    "istanu": "istanu", "istha": "istanu", "isthanu": "istanu", "isthanannadu": "istanu annadu",
    
    # Tamil
    "tharanum": "tharanum", "thara vendum": "tharanum", "kodukanum": "kodukkanum", "kodukka vendum": "kodukkanum",
    "kattanum": "kattanum", "kattanam": "kattanum",
    "varanum": "varanum", "vara vendum": "varanum", "vaanganum": "vaanganum",
    "koduthaar": "koduthaar", "koduthaaru": "koduthaar", "koduthutaar": "koduthaar", "koduthutaaru": "koduthaar",
    "koduthen": "koduthen", "koduthuten": "koduthen", "thandhaar": "thandhaar", "thandhen": "thandhen",
    "kattinaar": "kattinaar", "kattinen": "kattinen",
    
    # Hindi
    "dena": "dena hai", "denahai": "dena hai", "deni hai": "dena hai", "dene hai": "dena hai",
    "lena": "lena hai", "lenahai": "lena hai", "leni hai": "lena hai", "lene hai": "lena hai",
    "diya": "diya", "diye": "diya", "de diya": "diya", "bheja": "bheja", "bhej diya": "bheja",
    "dega bola": "dene ko bola", "dunga bola": "dene ko bola",
    
    # Spoken Numerals
    "thouzad": "thousand", "thouzand": "thousand", "thoujand": "thousand", "thoujan": "thousand",
    "towjand": "thousand", "taujand": "thousand", "tauzand": "thousand", "hunderd": "hundred",
    "hondred": "hundred", "handred": "hundred", "lakha": "lakh", "laakh": "lakh", "latcham": "lakh",
    "krore": "crore", "krores": "crores", "wandalu": "vandalu", "aayiram": "aayiram", "hazaar": "hazaar",
    
    # Temporal & Currency
    "ninna": "ninna", "netru": "netru", "repu": "repu", "naalai": "naalai", "kal": "kal", "aaj": "aaj",
    "dabbulu": "rupayalu", "rupailu": "rupayalu", "paise": "rupaye", "rupaye": "rupaye", "panam": "panam", "kaasu": "panam"
}

def split_indic_sandhi(text: str) -> str:
    """
    Decomposes fused Sandhi agglutinations, numeral prefixes, and attached postpositions across
    Telugu, Tamil, and Hindi.
    """
    if not text:
        return ""
        
    s = text
    
    # Specific Telugu Sandhi Fusions
    s = re.sub(r'నాకిచ్చాడు', 'నాకు ఇచ్చాడు', s)
    s = re.sub(r'నాకొచ్చింది', 'నాకు వచ్చింది', s)
    s = re.sub(r'పదివేలిచ్చాడు', 'పదివేలు ఇచ్చాడు', s)
    s = re.sub(r'(\d+)\s*ఇచ్చేశాను', r'\1 ఇచ్చేశాను', s)
    s = re.sub(r'(\d+)ఇచ్చేశాను', r'\1 ఇచ్చేశాను', s)
    s = re.sub(r'([a-zA-Z\u0C00-\u0C7F]+)కిచ్చాను', r'\1 కి ఇచ్చాను', s)
    
    # Split digit + attached postposition: '2000ki' -> '2000 ki', '500kku' -> '500 kku', '1000ko' -> '1000 ko'
    s = re.sub(r'(\d+)(ki|ku|kku|ukku|ko|se|nundi|nunchi|irundhu|kitta|కి|కు|க்கு|உக்கு|को|से)\b', r'\1 \2', s, flags=re.IGNORECASE)
    
    # Split letter + digit / digit + letter: '50,000ఇచ్చేశాను' -> '50,000 ఇచ్చేశాను'
    s = re.sub(r'(\d{1,3}(?:,\d{2,3})*|\d+)([\u0C00-\u0C7F\u0B80-\u0BFF\u0900-\u097F]+)', r'\1 \2', s)
    s = re.sub(r'([\u0C00-\u0C7F\u0B80-\u0BFF\u0900-\u097F]+)(\d+)', r'\1 \2', s)
    
    return s

# Backward compatibility alias
split_telugu_sandhi = split_indic_sandhi

def indic_phonetic_fingerprint(name: str) -> str:
    """
    Computes a phonetic fingerprint adapted for South Asian / Indic names.
    Groups phonetically interchangeable letters and harmonizes noun vowel additions.
    """
    s = name.lower().strip()
    s = re.sub(r'[^a-z]', '', s)
    if not s:
        return ""
        
    s = s.replace("sh", "s").replace("sch", "s").replace("ch", "c").replace("zh", "l")
    s = s.replace("ee", "i").replace("ea", "i").replace("y", "i").replace("aa", "a")
    s = s.replace("oo", "u").replace("ou", "u")
    s = s.replace("ph", "f").replace("bh", "b").replace("v", "w")
    s = s.replace("th", "t").replace("dh", "d").replace("kh", "k").replace("gh", "g")
    
    if len(s) > 4 and s.endswith(('u', 'an', 'am')):
        if s.endswith('an') or s.endswith('am'):
            s = s[:-2]
        elif s.endswith('u'):
            s = s[:-1]
        
    s = re.sub(r'(.)\1+', r'\1', s)
    return s


class PhoneticNormalizer:
    """
    Normalizes Romanized Indic text into standard canonical forms.
    """
    
    @staticmethod
    def normalize(text: str) -> Dict[str, Any]:
        text_sandhi = split_indic_sandhi(text)
        raw_words = text_sandhi.split()
        normalized_words = []
        changes = []
        
        for idx, word in enumerate(raw_words):
            clean = re.sub(r'[^\w\u0C00-\u0C7F\u0B80-\u0BFF\u0900-\u097F]', '', word).lower()
            if clean in PHONETIC_CANONICAL_MAP:
                canon = PHONETIC_CANONICAL_MAP[clean]
                normalized_words.append(canon)
                changes.append({
                    "original": word,
                    "canonical": canon,
                    "position": idx
                })
            else:
                normalized_words.append(word)
                
        return {
            "original_text": text,
            "normalized_text": " ".join(normalized_words),
            "changes_count": len(changes),
            "changes": changes
        }

# Global singleton
phonetic_normalizer = PhoneticNormalizer()
