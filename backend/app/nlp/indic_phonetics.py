"""
Indic-Aware Phonetic Matching and Name Normalization Engine for Telugu, Tamil, Hindi,
Kannada, Malayalam, Urdu, Gujarati & Romanized Indic text.
Provides multi-lingual Indic phonetic hashing, case marker stripping, and hybrid Jaro-Winkler distance scoring.
"""

import re
from typing import Tuple, List, Optional
from backend.app.nlp.telugu_lexicon import TELUGU_HONORIFICS
from backend.app.nlp.tamil_lexicon import TAMIL_HONORIFICS
from backend.app.nlp.hindi_lexicon import HINDI_HONORIFICS
from backend.app.nlp.kannada_lexicon import KANNADA_HONORIFICS
from backend.app.nlp.malayalam_lexicon import MALAYALAM_HONORIFICS
from backend.app.nlp.urdu_lexicon import URDU_HONORIFICS
from backend.app.nlp.gujarati_lexicon import GUJARATI_HONORIFICS

# Postpositions & Honorifics
TELUGU_POSTPOSITIONS_TE = [
    'గారు', 'అన్న', 'అన్నా', 'రెడ్డి', 'రావు', 'భాయ్', 'సేఠ్', 'గారికి',
    'కి', 'కు', 'నుండి', 'నుంచి', 'తో', 'వద్ద', 'దగ్గర', 'లో', 'కింద'
]
TELUGU_POSTPOSITIONS_EN = [
    'garu', 'gaaru', 'anna', 'reddy', 'rao', 'bhai', 'seth', 'gariki',
    'ki', 'ku', 'nundi', 'nunchi', 'tho', 'vadda', 'daggara', 'lo', 'kinda'
]

TAMIL_POSTPOSITIONS_TA = [
    'அவர்கள்', 'அண்ணா', 'தம்பி', 'ஐயா', 'சேத்துக்கு', 'பாய்க்கு',
    'க்கு', 'உக்கு', 'கிட்ட', 'இடம்', 'இருந்து', 'இடமிருந்து'
]
TAMIL_POSTPOSITIONS_EN = [
    'avargal', 'anna', 'thambi', 'aiyya', 'bhaikku', 'sethkku',
    'ukku', 'kku', 'kitta', 'idam', 'irundhu', 'idamirundhu'
]

HINDI_POSTPOSITIONS_HI = [
    'जी', 'भैया', 'सेठजी', 'साहब', 'श्री', 'बाबूजी', 'को', 'से', 'के लिए', 'के पास'
]
HINDI_POSTPOSITIONS_EN = [
    'ji', 'bhaiya', 'bhai', 'sethji', 'saab', 'sir', 'babuji', 'shree',
    'ko', 'se', 'ke liye', 'ke paas'
]

KANNADA_POSTPOSITIONS_KN = [
    'ಅವರು', 'ಅಣ್ಣ', 'ಸಾಹುಕಾರ', 'ಶೆಟ್ರು', 'ಗೆ', 'ಇಗೆ', 'ಕ್ಕೆ', 'ಇಂದ', 'ಅಲ್ಲಿ'
]
KANNADA_POSTPOSITIONS_EN = [
    'avaru', 'anna', 'sahukara', 'sethru', 'ge', 'ige', 'kke', 'inda', 'alli'
]

MALAYALAM_POSTPOSITIONS_ML = [
    'ചേട്ടൻ', 'ചേച്ചി', 'ഇക്ക', 'സാഹിബ്', 'ക്ക്', 'ഇന്', 'ലേക്ക്', 'നിന്ന്', 'ൽ നിന്ന്'
]
MALAYALAM_POSTPOSITIONS_EN = [
    'chetan', 'chettan', 'chechi', 'ikka', 'sahib', 'kku', 'inu', 'lekku', 'ninnu'
]

URDU_POSTPOSITIONS_UR = [
    'صاحب', 'جناب', 'بھائی', 'کو', 'سے', 'کے لیے', 'کے پاس'
]
URDU_POSTPOSITIONS_EN = [
    'sahab', 'saheb', 'janab', 'bhai', 'ko', 'se', 'keliye', 'ke paas'
]

GUJARATI_POSTPOSITIONS_GU = [
    'ભાઈ', 'બહેન', 'શેઠ', 'કાકા', 'ને', 'થી', 'પાસે', 'માટે', 'પાસેથી'
]
GUJARATI_POSTPOSITIONS_EN = [
    'bhai', 'ben', 'sheth', 'kaka', 'ne', 'thi', 'pase', 'mate', 'pasethi'
]

ALL_INDIC_POSTPOSITIONS_SCRIPT = sorted(
    list(set(
        TELUGU_POSTPOSITIONS_TE + TAMIL_POSTPOSITIONS_TA + HINDI_POSTPOSITIONS_HI +
        KANNADA_POSTPOSITIONS_KN + MALAYALAM_POSTPOSITIONS_ML + URDU_POSTPOSITIONS_UR +
        GUJARATI_POSTPOSITIONS_GU
    )),
    key=len,
    reverse=True
)

ALL_INDIC_POSTPOSITIONS_ROMAN = sorted(
    list(set(
        TELUGU_POSTPOSITIONS_EN + TAMIL_POSTPOSITIONS_EN + HINDI_POSTPOSITIONS_EN +
        KANNADA_POSTPOSITIONS_EN + MALAYALAM_POSTPOSITIONS_EN + URDU_POSTPOSITIONS_EN +
        GUJARATI_POSTPOSITIONS_EN
    )),
    key=len,
    reverse=True
)

INDIC_PHONETIC_REPLACEMENTS = [
    # Strip Indic vowel matras and viramas across 8 scripts
    (r'[\u0C3E-\u0C4D\u0C55\u0C56\u0C62\u0C63]', ''), # Telugu
    (r'[\u0BBE-\u0BCD\u0BD7]', ''),                     # Tamil
    (r'[\u093E-\u094D\u0962\u0963]', ''),               # Devanagari (Hindi)
    (r'[\u0CBE-\u0CCD\u0CD5\u0CD6\u0CE2\u0CE3]', ''), # Kannada
    (r'[\u0D3E-\u0D4D\u0D57\u0D62\u0D63]', ''),         # Malayalam
    (r'[\u064B-\u065F\u0670]', ''),                     # Urdu/Arabic Harakat
    (r'[\u0ABE-\u0ACD\u0AE2\u0AE3]', ''),               # Gujarati
    (r'[\u0C01-\u0C03\u0B82\u0901-\u0903\u0C82\u0C83\u0D02\u0D03\u0A81-\u0A83]', ''), # Anusvara / Visarga
    
    # Romanized Indic consonant / vowel equivalence
    (r'th', 't'), (r'dh', 'd'), (r'bh', 'b'), (r'gh', 'g'), (r'jh', 'j'), (r'kh', 'k'), (r'ch', 'c'),
    (r'ph', 'f'), (r'sh', 's'), (r'zh', 'l'), (r'ee', 'i'), (r'oo', 'u'), (r'aa', 'a'), (r'w', 'v'),
    (r'y', 'i'), (r'z', 's'), (r'ck', 'k'), (r'c', 'k'),
    
    # Consonant unifications across scripts
    (r'[ఠటटठಟಠടഠٹطતટ]', 'त'),
    (r'[ఢడडढಡಢഡഢڈدદડ]', 'द'),
    (r'[భबभಬಭബഭبબભ]', 'ब'),
    (r'[ఘगघಗಘഗഘگગઘ]', 'ग'),
    (r'[శషసशषसಶಷಸശഷസسصثશષસ]', 'स'),
    (r'[ణనणनಣನണനنનણ]', 'न'),
    (r'[ళలळलಳಲളലلલળ]', 'ल'),
    (r'[ఝజजझಜಝജഝزجઝજ]', 'ज')
]

def strip_indic_honorifics(name: str) -> str:
    clean = name.strip()
    
    # 1. Remove Indic script postpositions
    for post in ALL_INDIC_POSTPOSITIONS_SCRIPT:
        if clean.endswith(post) and len(clean) > len(post) + 1:
            clean = clean[:-len(post)].strip()
            break
            
    # 2. Remove Romanized postpositions
    for post in ALL_INDIC_POSTPOSITIONS_ROMAN:
        pattern = rf'[\s_-]?{post}$'
        if re.search(pattern, clean, re.IGNORECASE) and len(clean) > len(post) + 2:
            clean = re.sub(pattern, '', clean, flags=re.IGNORECASE).strip()
            break
            
    return clean

def indic_phonetic_code(text: str) -> str:
    if not text:
        return ""
        
    s = text.lower().strip()
    s = strip_indic_honorifics(s)
    
    for pattern, replacement in INDIC_PHONETIC_REPLACEMENTS:
        s = re.sub(pattern, replacement, s)
        
    s = re.sub(r'(.)\1+', r'\1', s)
    return s.strip()

def jaro_winkler_distance(s1: str, s2: str, p: float = 0.1) -> float:
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    len1, len2 = len(s1), len(s2)
    max_dist = max(len1, len2) // 2 - 1
    if max_dist < 0:
        max_dist = 0

    s1_matches = [False] * len1
    s2_matches = [False] * len2

    matches = 0
    for i in range(len1):
        start = max(0, i - max_dist)
        end = min(i + max_dist + 1, len2)
        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] == s2[j]:
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

    if matches == 0:
        return 0.0

    k = 0
    transpositions = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    transpositions /= 2
    jaro = (matches / len1 + matches / len2 + (matches - transpositions) / matches) / 3.0
    prefix = 0
    for i in range(min(len1, len2, 4)):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break

    return jaro + (prefix * p * (1.0 - jaro))

class IndicPhoneticMatcher:
    def match_score(self, query_name: str, target_name: str) -> float:
        if not query_name or not target_name:
            return 0.0

        q_clean = strip_indic_honorifics(query_name).lower()
        t_clean = strip_indic_honorifics(target_name).lower()

        if q_clean == t_clean:
            return 1.0

        jw_score = jaro_winkler_distance(q_clean, t_clean)
        q_hash = indic_phonetic_code(q_clean)
        t_hash = indic_phonetic_code(t_clean)

        if q_hash and t_hash and q_hash == t_hash:
            return max(jw_score, 0.94)

        if q_hash and t_hash:
            hash_jw = jaro_winkler_distance(q_hash, t_hash)
            return max(jw_score, hash_jw * 0.92)

        return jw_score

indic_phonetic_matcher = IndicPhoneticMatcher()
