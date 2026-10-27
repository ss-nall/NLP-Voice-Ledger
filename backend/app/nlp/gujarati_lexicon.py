"""
Gujarati Financial & Numerals Lexicon.
Covers Gujarati script & Romanized Gujarati financial numerals, postpositions, and accounting verbs.
"""

from typing import Dict, List

GUJARATI_NUMERALS: Dict[str, float] = {
    # Digits (1-10)
    "ek": 1.0, "એક": 1.0, "૧": 1.0,
    "be": 2.0, "બે": 2.0, "do": 2.0, "૨": 2.0,
    "tran": 3.0, "ત્રણ": 3.0, "teen": 3.0, "૩": 3.0,
    "char": 4.0, "chaar": 4.0, "ચાર": 4.0, "૪": 4.0,
    "paanch": 5.0, "panch": 5.0, "પાંચ": 5.0, "૫": 5.0,
    "chha": 6.0, "chhe": 6.0, "છ": 6.0, "૬": 6.0,
    "saat": 7.0, "સાત": 7.0, "૭": 7.0,
    "aath": 8.0, "આઠ": 8.0, "૮": 8.0,
    "nav": 9.0, "nau": 9.0, "નવ": 9.0, "૯": 9.0,
    "das": 10.0, "દસ": 10.0, "૧૦": 10.0,

    # Teens (11-19)
    "agiyar": 11.0, "અગિયાર": 11.0,
    "bar": 12.0, "બાર": 12.0,
    "ter": 13.0, "તેર": 13.0,
    "chaud": 14.0, "ચૌદ": 14.0,
    "pandar": 15.0, "પંદર": 15.0,
    "sol": 16.0, "સોળ": 16.0,
    "sattar": 17.0, "સત્તર": 17.0,
    "adhaar": 18.0, "અઢાર": 18.0,
    "ogonis": 19.0, "ઓગણીસ": 19.0,

    # Tens (20-90)
    "vis": 20.0, "bees": 20.0, "વીસ": 20.0,
    "tris": 30.0, "tees": 30.0, "ત્રીસ": 30.0,
    "chalis": 40.0, "ચાલીસ": 40.0,
    "pachas": 50.0, "પચાસ": 50.0,
    "saath": 60.0, "સાઠ": 60.0,
    "sitter": 70.0, "સિત્તેર": 70.0,
    "ensi": 80.0, "એંસી": 80.0,
    "nevu": 90.0, "નેવું": 90.0,

    # Multipliers
    "so": 100.0, "sau": 100.0, "સો": 100.0,
    "beso": 200.0, "be so": 200.0, "બેસો": 200.0,
    "paanchso": 500.0, "paanch so": 500.0, "પાંચસો": 500.0,
    "hajar": 1000.0, "hajaar": 1000.0, "હજાર": 1000.0,
    "behajar": 2000.0, "be hajar": 2000.0, "બે હજાર": 2000.0,
    "paanchhajar": 5000.0, "paanch hajar": 5000.0, "પાંચ હજાર": 5000.0,
    "dashajar": 10000.0, "das hajar": 10000.0, "દસ હજાર": 10000.0,
    "laakh": 100000.0, "lakh": 100000.0, "લાખ": 100000.0,
    "crore": 10000000.0, "karor": 10000000.0, "કરોડ": 10000000.0,
}

GUJARATI_TEMPORAL_LEXICON: Dict[str, int] = {
    "kale": 1, "કાલે": 1,
    "aaje": 0, "આજે": 0,
    "paradive": 2, "param divse": 2, "પરમ દિવસે": 2, "parso": 2,
    "aavta athwade": 7, "aavta athvadiye": 7, "આવતા અઠવાડિયે": 7,
    "pachhala athwade": -7, "gaya athwade": -7, "ગયા અઠવાડિયે": -7,
    "aa athwade": 0, "આ અઠવાડિયે": 0,
    "aavta mahine": 30, "આવતા મહિને": 30,
    "gaya mahine": -30, "ગયા મહિને": -30
}

GUJARATI_DAYS_OF_WEEK: Dict[str, int] = {
    "somvar": 0, "સોમવાર": 0,
    "mangalvar": 1, "મંગળવાર": 1,
    "budhvar": 2, "બુધવાર": 2,
    "guruvar": 3, "ગુરુવાર": 3,
    "shukravar": 4, "શુક્રવાર": 4,
    "shanivar": 5, "શનિવાર": 5,
    "ravivar": 6, "રવિવાર": 6
}

GUJARATI_MONTHS: Dict[str, int] = {
    "જાન્યુઆરી": 1, "ફેબ્રુઆરી": 2, "માર્ચ": 3, "એપ્રિલ": 4, "મે": 5, "જૂન": 6,
    "જુલાઈ": 7, "ઓગસ્ટ": 8, "સપ્ટેમ્બર": 9, "ઓક્ટોબર": 10, "નવેમ્બર": 11, "ડિસેમ્બર": 12,
    "કારતક": 11, "માગશર": 12, "પોષ": 1, "મહા": 2, "ફાગણ": 3, "ચૈત્ર": 4,
    "વૈશાખ": 5, "જેઠ": 6, "અષાઢ": 7, "શ્રાવણ": 8, "ભાદરવો": 9, "આસો": 10
}

GUJARATI_DIRECTION_MARKERS = {
    "DATIVE_POSTPOSITIONS": ["ne", "mate", "ને", "માટે", "પાસે"],
    "ABLATIVE_POSTPOSITIONS": ["thi", "pase", "pasethi", "થી", "પાસેથી", "તરફથી"],
    "AGENT_POSTPOSITIONS": ["e", "temne", "teoe", "એ", "તેમણે", "તેણે"],
    "PAID_BY_BUSINESS_VERBS": [
        "ame aapya", "me aapya", "aapi didha", "transfer karya", "pay karya", "didha",
        "મેં આપ્યા", "અમે આપ્યા", "ચૂકવ્યા", "મોકલ્યા", "આપી દીધા"
    ],
    "PAID_BY_CUSTOMER_VERBS": [
        "aapya", "aapiya", "malya", "jama thaya", "jama karya", "aavya", "lavya", "chukavya",
        "મળ્યા", "જમા થયા", "જમા કર્યા", "આવ્યા", "આપ્યા"
    ],
    "PAYABLE_VERBS": [
        "aapvana che", "chukavvana che", "aapvanu che", "dena baki che", "baki che", "aapvano che",
        "આપવાના છે", "ચૂકવવાના છે", "બાકી છે"
    ],
    "RECEIVABLE_VERBS": [
        "levana che", "levanu che", "levani che", "aavvana che", "levano baki che", "malvana che",
        "લેવાના છે", "લેવાનું છે", "આવવાના છે", "મળવાના છે"
    ],
    "PROMISE_VERBS": [
        "aapshe", "aapis", "aapva kidhu", "bolya aapishu", "vaado karyo", "aapshe bolya",
        "આપશે", "આપીશ", "બોલ્યા"
    ],
    "SETTLEMENT_VERBS": ["hisaab puro", "khata chukte", "chuko karyo", "settle thayo", "હિસાબ પૂરો", "ખાતું ચૂકતે"]
}

GUJARATI_HONORIFICS = ["bhai", "ben", "sheth", "kaka", "dada", "ભાઈ", "બહેન", "શેઠ", "કાકા"]
GUJARATI_BUSINESS_TERMS = {
    "dukan": "shop", "vepar": "trade", "dhandho": "business", "pedhi": "firm", "traders": "traders",
    "baki": "balance", "rokad": "cash", "khata": "ledger",
    "દુકાન": "shop", "વેપાર": "trade", "ધંધો": "business", "પેઢી": "firm", "બાકી": "balance"
}
