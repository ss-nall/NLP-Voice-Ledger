"""
Indic-Aware Phonetic Matching and Name Normalization Engine for Telugu & Romanized Indic text.
Provides custom Telugu phonetic hashing, case marker stripping, and hybrid Jaro-Winkler distance scoring.
"""

import re
from typing import Tuple, List, Optional

# Common Telugu honorifics and postpositions / case markers
TELUGU_POSTPOSITIONS_TE = [
    'గారు', 'అన్న', 'అన్నా', 'రెడ్డి', 'రావు', 'భాయ్', 'సేఠ్', 'గారికి',
    'కి', 'కు', 'నుండి', 'నుంచి', 'తో', 'వద్ద', 'దగ్గర', 'లో', 'కింద'
]

TELUGU_POSTPOSITIONS_EN = [
    'garu', 'anna', 'reddy', 'rao', 'bhai', 'seth', 'gariki',
    'ki', 'ku', 'nundi', 'nunchi', 'tho', 'vadda', 'daggara', 'lo', 'kinda'
]

# Character mappings for Indic phonetic reduction
INDIC_PHONETIC_REPLACEMENTS = [
    (r'[ాిీుూృెేైొోౌ్]', ''),        # Strip Telugu vowel matras and virama for root consonant hash
    (r'[ంః]', ''),                  # Strip anusvara/visarga
    (r'th', 't'), (r'dh', 'd'), (r'bh', 'b'), (r'gh', 'g'), (r'jh', 'j'),
    (r'ph', 'f'), (r'sh', 's'), (r'ee', 'i'), (r'oo', 'u'), (r'w', 'v'),
    (r'y', 'i'), (r'z', 's'), (r'ck', 'k'), (r'c', 'k'),
    (r'[ఠట]', 'త'), (r'[ఢడ]', 'ద'), (r'[భబ]', 'బ'), (r'[ఘగ]', 'గ'),
    (r'[శషస]', 'స'), (r'[ణన]', 'న'), (r'[ళల]', 'ల'), (r'[ఝజ]', 'జ')
]

def strip_indic_honorifics(name: str) -> str:
    """
    Strips case markers, postpositions, and honorific suffixes from a person's name.
    e.g. 'రమేష్ గారికి' -> 'రమేష్', 'Pavan ki' -> 'Pavan', 'Ramesh anna' -> 'Ramesh'
    """
    clean = name.strip()
    
    # 1. Remove Telugu postpositions
    for post in sorted(TELUGU_POSTPOSITIONS_TE, key=len, reverse=True):
        if clean.endswith(post) and len(clean) > len(post) + 1:
            clean = clean[:-len(post)].strip()
            break
            
    # 2. Remove Romanized postpositions
    for post in sorted(TELUGU_POSTPOSITIONS_EN, key=len, reverse=True):
        pattern = rf'[\s_-]?{post}$'
        if re.search(pattern, clean, re.IGNORECASE) and len(clean) > len(post) + 2:
            clean = re.sub(pattern, '', clean, flags=re.IGNORECASE).strip()
            break
            
    return clean

def indic_phonetic_code(text: str) -> str:
    """
    Computes a simplified phonetic fingerprint for Telugu or Romanized Indic names.
    Maps aspirates, vowel variations, and retroflex consonants to canonical equivalents.
    """
    if not text:
        return ""
        
    s = text.lower().strip()
    s = strip_indic_honorifics(s)
    
    # Apply replacements
    for pattern, replacement in INDIC_PHONETIC_REPLACEMENTS:
        s = re.sub(pattern, replacement, s)
        
    # Collapse consecutive duplicate letters
    s = re.sub(r'(.)\1+', r'\1', s)
    return s.strip()

def jaro_winkler_distance(s1: str, s2: str, p: float = 0.1) -> float:
    """
    Computes Jaro-Winkler similarity between two strings (0.0 to 1.0).
    """
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

    # Count transpositions
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

    # Jaro calculation
    jaro = (matches / len1 + matches / len2 + (matches - transpositions) / matches) / 3.0

    # Winkler prefix calculation (max 4 chars)
    prefix = 0
    for i in range(min(len1, len2, 4)):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break

    return jaro + (prefix * p * (1.0 - jaro))

class IndicPhoneticMatcher:
    """
    Enterprise hybrid matcher combining token distance, Indic phonetic hashes,
    and transliteration equivalence for entity resolution.
    """

    def match_score(self, query_name: str, target_name: str) -> float:
        if not query_name or not target_name:
            return 0.0

        q_clean = strip_indic_honorifics(query_name).lower()
        t_clean = strip_indic_honorifics(target_name).lower()

        if q_clean == t_clean:
            return 1.0

        # String similarity
        jw_score = jaro_winkler_distance(q_clean, t_clean)

        # Phonetic code similarity
        q_code = indic_phonetic_code(q_clean)
        t_code = indic_phonetic_code(t_clean)
        phonetic_score = jaro_winkler_distance(q_code, t_code) if (q_code and t_code) else 0.0

        # Direct containment check
        containment_boost = 0.0
        if (len(q_clean) >= 3 and q_clean in t_clean) or (len(t_clean) >= 3 and t_clean in q_clean):
            containment_boost = 0.15

        final_score = max(jw_score, (jw_score * 0.5 + phonetic_score * 0.5) + containment_boost)
        return min(1.0, final_score)

indic_phonetic_matcher = IndicPhoneticMatcher()
