"""
Multi-Lingual Financial Relation & Direction Extraction Module.
Resolves transaction direction (PAYABLE vs RECEIVABLE), semantic participant roles,
and financial action relations (OWES, PAID, PROMISED_TO_PAY, ADVANCE, CREDIT_SALE, SETTLED)
across 8 Indian Languages: Telugu, Tamil, Hindi, Kannada, Malayalam, Urdu, Gujarati, and English.
"""

import re
from typing import Dict, Any, List, Optional
from backend.app.nlp.indic_lexicon import ALL_DIRECTION_MARKERS

INDIC_SCRIPTS_CHAR_CLASS = r'a-zA-Z\u0C00-\u0C7F\u0B80-\u0BFF\u0900-\u097F\u0C80-\u0CFF\u0D00-\u0D7F\u0600-\u06FF\u0A80-\u0AFF'

class FinancialRelationExtractor:
    """
    Determines financial relationship, flow direction, and semantic roles
    from multi-lingual Indic and English grammatical cues.
    """
    
    @staticmethod
    def extract_relation(text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        text_lower = text.lower()
        actors = entities.get("actors", [])
        actor_name = actors[0]["name"] if actors else "Unspecified"
        actor_type = actors[0]["type"] if actors else "PERSON"
        
        def matches_any(keywords: List[str]) -> bool:
            for kw in keywords:
                if re.search(r'(?:^|\s+)' + re.escape(kw) + r'(?:\s+|$|[.,!?])', text_lower):
                    return True
            return False

        # Business Recipient Pronouns across 8 languages: "to me", "to us", "naaku", "enakku", "mujhe", "nanage", "enikku", "mane", etc.
        has_business_recipient = bool(
            re.search(r'(?:^|\s+)(?:naaku|naku|maaku|maku|enakku|engalukku|mujhe|humko|humare|nanage|namage|enikku|njangalkku|mane|amne|to me|to us|for me|for us|నాకు|మాకు|எனக்கு|எங்களுக்கு|मुझे|हमको|നನಗೆ|നമുക്ക്|મને|ہمیں)(?:\s+|$|[.,!?])', text_lower)
        )

        # Counterparty Dative marker (Payable to Counterparty)
        temporal_dative_words = {
            "week", "vaaram", "varam", "month", "nela", "year", "maadham", "masam", "hafte", "saptah", "mahine", "vaara", "tingalu", "aazhcha", "athwade",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "somavaram", "mangalavaram", "budhavaram", "guruvaram", "sukravaram", "sanivaram", "aadivaram",
            "thingal", "sevvaai", "budhan", "viyazhan", "velli", "sani", "njaayiru",
            "somwar", "mangalwar", "budhwar", "guruwar", "shukrawar", "shaniwar", "raviwar",
            "somavaara", "mangalavaara", "budhavaara", "guruvaara", "shukravaara", "shanivaara", "bhanuvaara",
            "repu", "ninna", "ellundi", "eroju", "today", "tomorrow", "naalai", "netru", "kal", "aaj", "parson", "naale", "ivathu", "innu", "aaje",
            "sayantram", "udayam", "madyanam"
        }
        
        # Detect Gujarati context for postposition disambiguation ('ne' is dative in Gujarati, agentive in Hindi/Urdu)
        is_gujarati_context = bool(
            re.search(r'[\u0A80-\u0AFF]', text)
            or any(re.search(rf'\b{re.escape(w)}\b', text_lower) for w in [
                "aapya", "aapiya", "aapvana", "aapvanu", "levana", "levanu", "chukavya", "chukavvana",
                "moklya", "malya", "aavya", "aavvana", "baki che", "chhe", "pasethi", "kale", "aaje",
                "hajar", "beso", "paanchso", "pachas", "vis", "tris", "ame", "mane", "temne",
                "આપ્યા", "ચૂકવ્યા", "મોકલ્યા", "લેવાના", "આપવાના", "પાસેથી"
            ])
        )

        # Dative regex matching across 8 languages (Recipient marker "TO" - separated or attached)
        if is_gujarati_context:
            dative_pattern = rf'(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+)\s+(?:ne|mate|પાસે|ને|માટે)(?:\s+|$|[.,!?])|(?<=[^\u0aa8\s])(ને)\b|(નને|ન્ને)\b|(?<=[a-zA-Z])(ne)\b'
        else:
            dative_pattern = rf'(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+)\s*(?:gariki|annaki|bhaiki|sethki|ki|ku|kku|ukku|ko|ige|ge|kke|inu|lekku|nu|mate|గారికి|అన్నకి|కి|కు|க்கு|உக்கு|को|गे|ಗೆ|ಇಗೆ|ಕ್ಕೆ|ക്ക്|ഇന്|ലേക്ക്|ന്|നു|کو|ને|માટે)(?:\s+|$|[.,!?])|(?<=[{INDIC_SCRIPTS_CHAR_CLASS}])(కి|కు|க்கு|உக்கு|को|गे|ಗೆ|ಇಗೆ|ಕ್ಕೆ|ന്|നു|کو)\b'

        dative_match = re.search(dative_pattern, text_lower)
        dative_word = ""
        if dative_match:
            for g in dative_match.groups():
                if g:
                    dative_word = g.lower()
                    break
        has_counterparty_dative = bool(dative_match and dative_word not in temporal_dative_words and not has_business_recipient and dative_word not in {"maine", "humne", "me", "ame", "میں نے", "ہم نے", "મેં", "અમે"})
        has_dative_cue = (
            has_counterparty_dative
            or "paid to " in text_lower or "pay to " in text_lower or "due to " in text_lower or "payable to " in text_lower
            or bool(re.search(rf'\bto\s+[{INDIC_SCRIPTS_CHAR_CLASS}]+', text_lower))
        )
        
        # Agentive / Subject marker across languages (e.g. Hindi/Urdu "ne", Gujarati "e / temne")
        if is_gujarati_context:
            agent_pattern = rf'(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+)\s*(?:e|temne|teoe|એ|તેમણે|તેણે)(?:\s+|$|[.,!?])|(?<=[{INDIC_SCRIPTS_CHAR_CLASS}])(એ)\b|(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+[\u0ac7])(?:\s+|$|[.,!?])'
        else:
            agent_pattern = rf'(?:^|\s+)([{INDIC_SCRIPTS_CHAR_CLASS}]+)\s*(?:ne|usne|unhone|ने|उसने|उन्होंने|نے)(?:\s+|$|[.,!?])'

        agent_match = re.search(agent_pattern, text_lower)
        agent_word = ""
        if agent_match:
            for g in agent_match.groups():
                if g:
                    agent_word = g.lower()
                    break
        gujarati_agent_exclusions = {
            "અને", "છે", "બધાને", "મને", "અમને", "તમને", "તેમને", "તેને", "પાસે", "સાથે", "માટે", "કાલે", "આજે", "કે", "જે", "તે", "રોજે", "વખતે", "me", "ame", "મેં", "અમે", "આપ્યા", "ચૂકવ્યા", "મોકલ્યા", "લીધા", "દીધા"
        }
        has_counterparty_agent = bool(
            agent_match and agent_word not in temporal_dative_words
            and agent_word not in gujarati_agent_exclusions
            and agent_word not in {"maine", "humne", "मैंने", "हमने", "me", "ame", "મેં", "અમે", "nenu", "memu", "naan", "naanu", "njan", "i", "we", "میں نے", "ہم نے"}
        )

        # Ablative marker (From Customer / Source)
        has_ablative_cue = (
            any(re.search(r'(?:^|\s+)' + re.escape(p) + r'(?:\s+|$|[.,!?])', text_lower) for p in ALL_DIRECTION_MARKERS["RECEIVABLE_POSTPOSITIONS"])
            or "from " in text_lower or text_lower.startswith("from ") or "due from " in text_lower or "received from " in text_lower or "collected from " in text_lower or "got from " in text_lower
            or any(k in text_lower for k in ["నుంచి", "నుండి", "இருந்து", "ಇಂದ", "നിന്ന്", "પાસેથી", "સે", "کی طرف سے"])
        )

        # First person subject check (Business owner speaking)
        is_first_person = bool(re.search(r'(?:\b|^|\s)(maine|humne|nenu|memu|naan|naanga|main|hum|naanu|naavu|njan|njangal|me|ame|hu|i|we|నేను|మేము|நான்|நாங்கள்|मैंने|हमने|ನಾನು|ഞാൻ|ہم نے|میں نے|મેં|અમે|હું)(?:\b|\s|$|[.,!?])', text_lower))

        # Verb Tense & Direction Classifications
        # 1. Hindi / Urdu
        is_hindi_biz_paid = (
            (is_first_person and matches_any(["diya", "diye", "de diya", "bheja", "bhej diya", "pay kiya", "transfer kiya", "jama kiya", "ada kiya", "दिया", "दिए", "भेजा", "دیا", "ادا کیا", "بھیجا"]))
            or (has_counterparty_dative and not has_counterparty_agent and matches_any(["diya", "diye", "de diya", "bheja", "bhej diya", "pay kiya", "transfer kiya", "ada kiya", "ada kardiya", "दिया", "दिए", "भेजा", "دیا", "ادا کیا", "بھیجا"]))
            or matches_any(["maine diya", "humne diya", "मैंने दिया", "हमने दिया", "maine bhej diya", "humne bheja", "pay kar diya", "transfer kar diya", "chukta kiya", "میں نے دیا", "ہم نے دیا"])
        )
        is_hindi_cust_paid = (
            not is_hindi_biz_paid and not is_first_person and (
                (has_counterparty_agent and matches_any(["diya", "diye", "de diya", "bheja", "bhej diya", "pay kiya", "transfer kiya", "jama kiya", "ada kiya", "ada kardiya", "दिया", "दिए", "भेजा", "دیا", "ادا کیا", "بھیجا"]))
                or (has_ablative_cue and matches_any(["mila", "aaya", "prapt hua", "wasool hua", "mil gaya", "मिला", "आया", "وصول ہوا", "ملا"]))
                or (has_business_recipient and matches_any(["diya", "diye", "bheja", "दिया", "भेजा", "دیا"]))
            )
        )

        # 2. Tamil
        is_tamil_biz_paid = (
            matches_any(["koduthen", "koduthom", "koduthuten", "thandhen", "thandhom", "kattinen", "kattinom", "anuppinen", "செலுத்தினேன்", "கொடுத்தேன்", "தந்தேன்", "கட்டினேன்"])
            or (has_counterparty_dative and not has_business_recipient and matches_any(["koduthen", "koduthom", "koduthu", "thanthen", "anuppinen", "கொடுத்தேன்", "கொடுத்தோம்"]))
        )
        is_tamil_cust_paid = (
            not is_tamil_biz_paid and not is_first_person and (
                matches_any(["koduthaar", "koduthan", "thandhaar", "thandhan", "kattinaar", "anuppinaar", "செலுத்தினார்", "கொடுத்தார்", "தந்தார்", "அனுப்பினார்", "கட்டினார்"])
                or (has_ablative_cue and matches_any(["vandhadhu", "vandhuchu", "kidaithathu", "வந்தது"]))
                or (has_business_recipient and matches_any(["koduthaar", "thandhaar", "கொடுத்தார்"]))
            )
        )

        # 3. Kannada
        is_kannada_biz_paid = (
            (is_first_person and matches_any(["kotte", "kottidini", "kottidivi", "paavathiside", "paavathi madide", "ಕೊಟ್ಟೆ", "ಪಾವತಿಸಿದೆ"]))
            or (has_counterparty_dative and not has_business_recipient and matches_any(["kotte", "kottidini", "kottidivi", "paavathiside", "paavathi madide", "ಕೊಟ್ಟೆ", "ಪಾವತಿಸಿದೆ"]))
        )
        is_kannada_cust_paid = (
            not is_kannada_biz_paid and not is_first_person and (
                matches_any(["kottiddane", "kottaru", "kaluhisiddane", "kottanu", "paavathisiddane", "ಕೊಟ್ಟಿದ್ದಾನೆ", "ಕೊಟ್ಟರು", "ಕಳುಹಿಸಿದ್ದಾನೆ", "ಕೊಟ್ಟನು"])
                or (has_ablative_cue and matches_any(["bantu", "banthu", "sikkitu", "ಬಂತು"]))
                or (has_business_recipient and matches_any(["kotte", "kottaru", "ಕೊಟ್ಟ", "ಕೊಟ್ಟಿದ್ದಾನೆ"]))
            )
        )

        # 4. Malayalam
        is_malayalam_biz_paid = (
            (is_first_person and matches_any(["koduthu", "nalki", "pay cheythu", "ayachu", "കൊടുത്തു", "നൽകി", "അയച്ചു"]))
            or (has_counterparty_dative and not has_business_recipient and matches_any(["koduthu", "pay cheythu", "ayachu", "കൊടുത്തു", "നൽകി"]))
            or ("കൊടുത്തു" in text_lower and not has_business_recipient and not has_ablative_cue)
        )
        is_malayalam_cust_paid = (
            not is_malayalam_biz_paid and not is_first_person and (
                matches_any(["thannu", "nalki", "ayachu", "തന്നു", "നൽകി", "അയച്ചു"])
                or (has_ablative_cue and matches_any(["kitti", "kittiyath", "കിട്ടി", "ലഭിച്ചു"]))
                or (has_business_recipient and matches_any(["thannu", "nalki", "തന്നു", "നൽകി"]))
            )
        )

        # 5. Gujarati
        is_gujarati_biz_paid = (
            (is_first_person and matches_any(["aapya", "chukavya", "moklya", "didha", "aapiya", "aapi didha", "આપ્યા", "ચૂકવ્યા", "મોકલ્યા", "આપી દીધા", "દીધા"]))
            or (has_counterparty_dative and not has_counterparty_agent and not has_business_recipient and matches_any(["aapya", "chukavya", "moklya", "aapiya", "aapi didha", "didha", "ચૂકવ્યા", "મોકલ્યા", "આપી દીધા", "આપ્યા"]))
        )
        is_gujarati_cust_paid = (
            not is_gujarati_biz_paid and not is_first_person and (
                (has_counterparty_agent and matches_any(["aapya", "moklya", "chukavya", "jama karya", "આપ્યા", "મોકલ્યા", "ચૂકવ્યા"]))
                or (is_gujarati_context and not has_counterparty_dative and matches_any(["aapya", "moklya", "chukavya", "jama karya", "આપ્યા", "મોકલ્યા"]))
                or (has_ablative_cue and matches_any(["malya", "aavya", "મળ્યા", "આવ્યા"]))
                or (has_business_recipient and matches_any(["aapya", "આપ્યા"]))
            )
        )

        # 6. Telugu
        is_telugu_biz_paid = (
            (is_first_person and matches_any(["ichanu", "icha", "ichesanu", "ichesa", "kattanu", "kattesa", "kattina", "chellinchanu", "chellincha", "pampanu", "pampa", "ఇచ్చాను", "ఇచ్చాం", "ఇచ్చేశాను", "ఇచ్చేసాను", "ఇచ్చేసా", "కట్టాను", "కట్టేసాను", "కట్టేసా", "చెల్లించాను", "చెల్లించా", "పంపాను", "పంపా"]))
            or (has_counterparty_dative and not has_business_recipient and matches_any(["ichanu", "icha", "ichesanu", "ichesa", "kattanu", "kattesa", "kattina", "chellinchanu", "chellincha", "pampanu", "pampa", "ఇచ్చాను", "ఇచ్చాం", "ఇచ్చేశాను", "ఇచ్చేసాను", "ఇచ్చేసా", "కట్టాను", "కట్టేసాను", "కట్టేసా", "చెల్లించాను", "చెల్లించా", "పంపాను", "పంపా"]))
            or matches_any(["nenu ichanu", "memu ichamu", "నేను ఇచ్చాను", "మేము ఇచ్చాం", "nenu kattanu", "nenu ichesa", "nenu chellincha"])
        )
        is_telugu_cust_paid = (
            not is_telugu_biz_paid and not is_first_person and (
                matches_any(["ichadu", "ichindi", "icharu", "ichesadu", "ichesaru", "kattadu", "kattaru", "kattesadu", "kattesaru", "chellinchadu", "chellincharu", "pampadu", "pamparu", "ఇచ్చాడు", "ఇచ్చింది", "ఇచ్చారు", "ఇచ్చేశారు", "ఇచ్చేసాడు", "కట్టాడు", "కట్టారు", "కట్టేసాడు", "కట్టేశారు", "చెల్లించాడు", "చెల్లించారు", "పంపాను", "పంపారు"])
                or (has_ablative_cue and matches_any(["vachindi", "vachayi", "andindi", "వచ్చింది", "చేరింది"]))
                or (has_business_recipient and matches_any(["ichadu", "ichindi", "icharu", "ichesaru", "ఇచ్చాడు", "చెల్లించాడు", "కట్టాడు"]))
            )
        )

        # 7. English
        is_english_biz_paid = (
            (is_first_person and matches_any(["paid", "gave", "transferred", "sent", "deposited"]))
            or (has_dative_cue and matches_any(["paid to", "transferred to", "sent to", "gave to"]))
            or text_lower.startswith("paid ") or text_lower.startswith("gave ") or text_lower.startswith("transferred ")
        )
        is_english_cust_paid = (
            not is_english_biz_paid and (
                (has_ablative_cue and matches_any(["received", "collected", "got", "received from", "collected from", "got from"]))
                or (bool(re.search(r'\b[a-zA-Z]+\s+(?:paid|gave|transferred|deposited|sent)\b', text_lower)) and not is_first_person and not has_counterparty_dative)
            )
        )

        is_biz_paid = (
            is_hindi_biz_paid or is_tamil_biz_paid or is_kannada_biz_paid or
            is_malayalam_biz_paid or is_gujarati_biz_paid or is_telugu_biz_paid or is_english_biz_paid
        )
        is_cust_paid = (
            not is_biz_paid and (
                is_hindi_cust_paid or is_tamil_cust_paid or is_kannada_cust_paid or
                is_malayalam_cust_paid or is_gujarati_cust_paid or is_telugu_cust_paid or is_english_cust_paid
                or (has_counterparty_agent and matches_any(ALL_DIRECTION_MARKERS["PAID_BY_CUSTOMER_VERBS"]))
                or (matches_any(ALL_DIRECTION_MARKERS["PAID_BY_CUSTOMER_VERBS"]) and not matches_any(ALL_DIRECTION_MARKERS["PAYABLE_VERBS"]) and not is_first_person and not has_counterparty_dative)
            )
        )
        has_payable_verb = matches_any(ALL_DIRECTION_MARKERS["PAYABLE_VERBS"]) or any(v in text_lower for v in ["ఆపవానా", "આપવાના", "આપવાના છે", "ચૂકવવાના છે", "കൊടുക്കാനുണ്ട്", "കൊടുക്കണം", "دینا ہے", "ادا کرنا ہے"])
        has_receivable_verb = matches_any(ALL_DIRECTION_MARKERS["RECEIVABLE_VERBS"]) or any(v in text_lower for v in ["લેવાના", "લેવાના છે", "കിട്ടാനുണ്ട്", "വാങ്ങാനുണ്ട്", "لینا ہے", "وصول کرنا ہے"])
        is_promise = any(v in text_lower for v in ALL_DIRECTION_MARKERS["PROMISE_VERBS"]) or \
                     ("annadu" in text_lower and ("istanu" in text_lower or "istha" in text_lower)) or \
                     ("sonnaar" in text_lower and "tharen" in text_lower) or \
                     ("bola" in text_lower and ("dega" in text_lower or "dunga" in text_lower)) or \
                     ("paranju" in text_lower and "tharaam" in text_lower) or \
                     ("helida" in text_lower and "kodtini" in text_lower) or \
                     ("bolya" in text_lower and "aapshe" in text_lower)
        is_settled = any(v in text_lower for v in ALL_DIRECTION_MARKERS["SETTLEMENT_VERBS"])
        is_advance = any(v in text_lower for v in ALL_DIRECTION_MARKERS["ADVANCE_VERBS"])
        
        # 1. Trade Items (Credit Sale vs Purchase)
        is_sale_trade = any(kw in text_lower for kw in [
            "goods icha", "goods ichamu", "saraku icha", "saraku ammanu", "saruku ammanu", "ammanu", "ammamu", "credit meeda", "udhari icha", "credit sale", "sold",
            "sarakku koduthen", "porul koduthen", "kadhanuku koduthen", "kadhanuku vitren", "vitren", "virpanai", "kadhanuku vaanginaar", "kadhanukku vaanginaar",
            "maal diya", "samaan diya", "udhar pe diya", "becha", "maal becha", "samaan becha", "udhar becha", "udhar liya",
            "saraku kotte", "maal aapiyo", "maal bechyu",
            "సరుకు ఇచ్చా", "సరుకు అమ్మాను", "అమ్మాను", "అమ్మాము", "சரக்கு கொடுத்தேன்", "பொருள் கொடுத்தேன்", "சரக்கு விற்றேன்", "விற்றேன்", "விற்பனை செய்தேன்", "சரக்கு கடனுக்கு வாங்கினார்", "கடனுக்கு வாங்கினார்", "माल दिया", "सामान दिया", "उधार पे दिया", "माल बेचा", "सामान बेचा", "बेचा", "उधार लिया"
        ])
        if is_sale_trade:
            return {
                "relation_type": "CREDIT_SALE",
                "direction": "receivable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.94,
                "explanation": f"Credit sale of goods provided to {actor_name}."
            }
            
        is_purchase_trade = any(kw in text_lower for kw in [
            "saraku konna", "saruku konna", "konnanu", "konnamu", "stock theppincham", "purchase", "maal konnam",
            "sarakku vaanginen", "sarakku vaanginom", "maal vaanginom", "porul vaanginom", "vaanginen",
            "maal kharida", "samaan kharida", "stock mangwaya", "kharida", "kharide",
            "stock thegondidini", "maal kharidyu",
            "సరుకు కొన్నా", "సరుకు కొన్నాను", "కొన్నాను", "కొన్నాము", "சரக்கு வாங்கினேன்", "வாங்கினேன்", "வாங்கினோம்", "माल खरीदा", "सामान खरीदा", "सामान मंगवाया", "खरीदा"
        ])
        if is_purchase_trade:
            return {
                "relation_type": "PURCHASE",
                "direction": "payable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.94,
                "explanation": f"Stock purchase from {actor_name}."
            }

        # 2. Promise to Pay
        if is_promise:
            direction = "payable" if (has_dative_cue and is_first_person) else "receivable"
            return {
                "relation_type": "PROMISED_TO_PAY",
                "direction": direction,
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.95,
                "explanation": f"{actor_name} committed to settle payment."
            }

        # 3. Full Settlement
        if is_settled:
            direction = "payable" if (is_biz_paid or (has_dative_cue and not has_business_recipient and not has_counterparty_agent)) else "receivable"
            return {
                "relation_type": "SETTLED",
                "direction": direction,
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.98,
                "explanation": f"Full ledger settlement completed with {actor_name}."
            }

        # 4. Advance Payment
        if is_advance:
            direction = "payable" if (is_biz_paid or (has_dative_cue and not has_counterparty_agent)) else "receivable"
            return {
                "relation_type": "ADVANCE",
                "direction": direction,
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.95,
                "explanation": f"Advance payment recorded for {actor_name}."
            }

        # 5. Business Paid Supplier (Outflow / Payable reduction)
        if is_biz_paid:
            return {
                "relation_type": "PAID",
                "direction": "payable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.96,
                "explanation": f"Business paid {actor_name} (cash outflow / payable reduction)."
            }

        # 6. Customer Paid Business (Inflow / Receivable reduction)
        if is_cust_paid:
            return {
                "relation_type": "PAID",
                "direction": "receivable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.96,
                "explanation": f"{actor_name} paid business (cash inflow / receivable reduction)."
            }

        # 7. Explicit Payable / Receivable Obligation via Modal Verbs
        if has_payable_verb:
            if has_business_recipient or has_ablative_cue:
                return {
                    "relation_type": "OWES",
                    "direction": "receivable",
                    "actor": actor_name,
                    "counterparty": "Business",
                    "confidence": 0.95,
                    "explanation": f"Customer {actor_name} owes payment to business."
                }
            return {
                "relation_type": "OWES",
                "direction": "payable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.95,
                "explanation": f"Business owes payment to supplier {actor_name}."
            }

        # 8. Explicit Receivable Obligation
        if has_receivable_verb or has_business_recipient:
            return {
                "relation_type": "OWES",
                "direction": "receivable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.95,
                "explanation": f"Customer {actor_name} owes payment to business."
            }

        # 9. Dative vs Ablative Postposition Fallback
        if has_dative_cue and not has_business_recipient and not has_counterparty_agent:
            return {
                "relation_type": "OWES",
                "direction": "payable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.90,
                "explanation": f"Dative marker indicates payable to {actor_name}."
            }

        if has_ablative_cue or has_counterparty_agent:
            return {
                "relation_type": "OWES",
                "direction": "receivable",
                "actor": actor_name,
                "counterparty": "Business",
                "confidence": 0.90,
                "explanation": f"Ablative / Agent marker indicates receivable from {actor_name}."
            }

        # Default fallback
        return {
            "relation_type": "OWES",
            "direction": "receivable",
            "actor": actor_name,
            "counterparty": "Business",
            "confidence": 0.85,
            "explanation": f"Defaulted to receivable obligation for {actor_name}."
        }

# Global singleton
relation_extractor = FinancialRelationExtractor()
