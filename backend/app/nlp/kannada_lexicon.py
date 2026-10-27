"""
Kannada Financial & Numerals Lexicon.
Covers spoken numerals, compound fractions, multiplier scale words,
grammatical postpositions (Dative/Ablative/Locative), tenses, and financial verbs.
"""

from typing import Dict, List

# Spoken and Script Numerals Mapping (Kannada Script + Romanized Kannada)
KANNADA_NUMERALS: Dict[str, float] = {
    # Digits (1-10)
    "ondhu": 1.0, "ondu": 1.0, "onnu": 1.0, "ఒందు": 1.0, "ಒಂದು": 1.0, "೧": 1.0,
    "eradu": 2.0, "yeradu": 2.0, "ಎರಡು": 2.0, "೨": 2.0,
    "mooru": 3.0, "muru": 3.0, "ಮೂರು": 3.0, "೩": 3.0,
    "naalaku": 4.0, "naalku": 4.0, "nalku": 4.0, "ನಾಲ್ಕು": 4.0, "೪": 4.0,
    "aidu": 5.0, "aaydu": 5.0, "aydu": 5.0, "ಐದು": 5.0, "೫": 5.0,
    "aaru": 6.0, "aru": 6.0, "ಆರು": 6.0, "೬": 6.0,
    "elu": 7.0, "yelu": 7.0, "ಏಳು": 7.0, "೭": 7.0,
    "entu": 8.0, "yentu": 8.0, "ಎಂಟು": 8.0, "೮": 8.0,
    "ombattu": 9.0, "ombatu": 9.0, "ಒಂಬತ್ತು": 9.0, "೯": 9.0,
    "hattu": 10.0, "hatu": 10.0, "ಹತ್ತು": 10.0, "೧೦": 10.0,

    # Teens (11-19)
    "hannondu": 11.0, "ಹನ್ನೊಂದು": 11.0,
    "hanneradu": 12.0, "ಹನ್ನೆರಡು": 12.0,
    "hadimooru": 13.0, "ಹದಿಮೂರು": 13.0,
    "hadinaalaku": 14.0, "hadinalku": 14.0, "ಹದಿನಾಲ್ಕು": 14.0,
    "hadinaidu": 15.0, "hadinaydu": 15.0, "ಹದಿನೈದು": 15.0,
    "hadinaaru": 16.0, "ಹದಿನಾರು": 16.0,
    "hadinelu": 17.0, "ಹದಿನೇಳು": 17.0,
    "hadinentu": 18.0, "ಹದಿನೆಂಟು": 18.0,
    "hattombattu": 19.0, "ಹತ್ತೊಂಬತ್ತು": 19.0,

    # Tens (20-90)
    "ippattu": 20.0, "ಇಪ್ಪತ್ತು": 20.0,
    "muvvattu": 30.0, "ಮೂವತ್ತು": 30.0,
    "nalvattu": 40.0, "ನಲವತ್ತು": 40.0,
    "aivattu": 50.0, "ayvattu": 50.0, "ಐವತ್ತು": 50.0,
    "aravattu": 60.0, "ಅರವತ್ತು": 60.0,
    "eppattu": 70.0, "ಎಪ್ಪತ್ತು": 70.0,
    "enbattu": 80.0, "ಎಂಬತ್ತು": 80.0,
    "tombattu": 90.0, "ತೊಂಬತ್ತು": 90.0,

    # Multipliers (Hundreds, Thousands, Lakhs, Crores)
    "nooru": 100.0, "nuru": 100.0, "ನೂರು": 100.0,
    "innooru": 200.0, "ಇನ್ನೂರು": 200.0,
    "munnooru": 300.0, "ಮುನ್ನೂರು": 300.0,
    "naanooru": 400.0, "ನಾನೂರು": 400.0,
    "ainooru": 500.0, "aynooru": 500.0, "ಐನೂರು": 500.0,
    "aarnooru": 600.0, "ಆರ್ನೂರು": 600.0,
    "elnooru": 700.0, "ಏಳ್ನೂರು": 700.0,
    "entnooru": 800.0, "ಎಂಟುನೂರು": 800.0,
    "ombaynooru": 900.0, "ಒಂಬೈನೂರು": 900.0,

    "saavira": 1000.0, "savira": 1000.0, "savirada": 1000.0, "ಸಾವಿರ": 1000.0,
    "ersaavira": 2000.0, "eradu saavira": 2000.0,
    "aidu saavira": 5000.0, "hattusaavira": 10000.0, "ಹತ್ತು ಸಾವಿರ": 10000.0,
    "laksha": 100000.0, "lakh": 100000.0, "ಲಕ್ಷ": 100000.0,
    "koti": 10000000.0, "crore": 10000000.0, "ಕೋಟಿ": 10000000.0,
}

KANNADA_TEMPORAL_LEXICON: Dict[str, int] = {
    "ninne": -1, "ನೆನ್ನೆ": -1,
    "ivathu": 0, "ee dina": 0, "ಇವತ್ತು": 0, "ಇಂದು": 0, "indu": 0,
    "naale": 1, "ನಾಳೆ": 1,
    "naadidhu": 2, "ನಾಡಿದ್ದು": 2, "nadiddu": 2,
    "mundina vaara": 7, "ಮುಂದಿನ ವಾರ": 7, "adutha vaara": 7,
    "hindina vaara": -7, "ಹಿಂದಿನ ವಾರ": -7, "kaleda vaara": -7,
    "ee vaara": 0, "ಈ ವಾರ": 0,
    "mundina tingalu": 30, "ಮುಂದಿನ ತಿಂಗಳು": 30,
    "hindina tingalu": -30, "ಹಿಂದಿನ ತಿಂಗಳು": -30
}

KANNADA_DAYS_OF_WEEK: Dict[str, int] = {
    "somavaara": 0, "somavara": 0, "ಸೋಮವಾರ": 0,
    "mangalavaara": 1, "mangalavara": 1, "ಮಂಗಳವಾರ": 1,
    "budhavaara": 2, "budhavara": 2, "ಬುಧವಾರ": 2,
    "guruvaara": 3, "guruvara": 3, "ಗುರುವಾರ": 3,
    "shukravaara": 4, "shukravara": 4, "ಶುಕ್ರವಾರ": 4,
    "shanivaara": 5, "shanivara": 5, "ಶನಿವಾರ": 5,
    "bhanuvaara": 6, "bhanuvara": 6, "ಭಾನುವಾರ": 6, "aadivaara": 6, "ಆದಿವಾರ": 6
}

KANNADA_MONTHS: Dict[str, int] = {
    "ಜನವರಿ": 1, "ಫೆಬ್ರವರಿ": 2, "ಮಾರ್ಚ್": 3, "ಏಪ್ರಿಲ್": 4, "ಮೇ": 5, "ಜೂನ್": 6,
    "ಜುಲೈ": 7, "ಆಗಸ್ಟ್": 8, "ಸೆಪ್ಟೆಂಬರ್": 9, "ಅಕ್ಟೋಬರ್": 10, "ನವೆಂಬರ್": 11, "ಡಿಸೆಂಬರ್": 12,
    "ಯುಗಾದಿ": 4, "ಚೈತ್ರ": 4, "ವೈಶಾಖ": 5, "ಜ್ಯೇಷ್ಠ": 6, "ಆಷಾಢ": 7, "ಶ್ರಾವಣ": 8,
    "ಭಾದ್ರಪದ": 9, "ಆಶ್ವಯುಜ": 10, "ಕಾರ್ತಿಕ": 11, "ಮಾರ್ಗಶಿರ": 12, "ಪುಷ್ಯ": 1, "ಮಾಘ": 2, "ಫಾಲ್ಗುಣ": 3
}

KANNADA_DIRECTION_MARKERS = {
    "DATIVE_POSTPOSITIONS": ["ige", "ge", "kke", "ಗೆ", "ಇಗೆ", "ಕ್ಕೆ", "alli", "ಅಲ್ಲಿ"],
    "ABLATIVE_POSTPOSITIONS": ["inda", "indha", "ಇಂದ", "ಹತ್ತಿರ"],
    "PAID_BY_BUSINESS_VERBS": [
        "naanu kotte", "naavu kottidini", "kottiddene", "kottu", "kottayithu", "kottbitte", "pavamadide",
        "ಕೊಟ್ಟೆ", "ಕೊಟ್ಟಿದ್ದೇನೆ", "ಪಾವತಿಸಿದೆ", "ಕೊಟ್ಟಾಯಿತು"
    ],
    "PAID_BY_CUSTOMER_VERBS": [
        "kotte", "kottaru", "kottidare", "kottiddare", "kottanu", "kottalu", "kottbittaru", "thagondidini",
        "ಕೊಟ್ಟರು", "ಕೊಟ್ಟಿದ್ದಾರೆ", "ನೀಡಿದರು"
    ],
    "PAYABLE_VERBS": [
        "kodabeku", "kodbeku", "kodbekagide", "salavide",
        "ಕೊಡಬೇಕು", "ಕೊಡಬೇಕಾಗಿದೆ", "ಬಾಕಿ ಇದೆ"
    ],
    "RECEIVABLE_VERBS": [
        "barabeku", "barbeku", "barbekagide", "thagobeku", "thagolbeku", "padiyabeku", "barabeku",
        "ಬರಬೇಕು", "ಬರಬೇಕಾಗಿದೆ", "ಪಡೆಯಬೇಕು", "ತೆಗೆದುಕೊಳ್ಳಬೇಕು"
    ],
    "PROMISE_VERBS": [
        "kodtini", "kodtane", "kodtare", "kodtini antha helida", "kodtini andaru", "kodtene",
        "ಕೊಡುತ್ತೇನೆ", "ಕೊಡುತ್ತಾರೆ", "ಕೊಡುತ್ತೇನೆ ಎಂದರು"
    ],
    "SETTLEMENT_VERBS": ["hisaab mugiyithu", "chuktayithu", "settle aayithu", "ಖಾತೆ ಮುಕ್ತಾಯವಾಯಿತು", "ಮುಕ್ತಾಯ"]
}

KANNADA_HONORIFICS = ["avaru", "garu", "anna", "sahukara", "sethru", "ಅವರು", "ಅಣ್ಣ", "ಸಾಹುಕಾರ", "ಶೆಟ್ರು"]
KANNADA_BUSINESS_TERMS = {
    "angadi": "shop", "vyapara": "trade", "dukaan": "shop", "dhaanya": "grains", "kirana": "groceries", "traders": "traders",
    "baki": "outstanding_balance", "khata": "ledger", "rokkha": "cash",
    "ಅಂಗಡಿ": "shop", "ವ್ಯಾಪಾರ": "trade", "ಕಿರಣ": "groceries", "ಬಾಕಿ": "balance"
}
