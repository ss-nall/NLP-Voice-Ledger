"""
Malayalam Financial & Numerals Lexicon.
Covers spoken numerals, compound units, multiplier scales, postpositions, and transaction verbs.
"""

from typing import Dict, List

MALAYALAM_NUMERALS: Dict[str, float] = {
    # Digits (1-10)
    "onnu": 1.0, "ondu": 1.0, "ഒന്ന്": 1.0, "൧": 1.0,
    "randu": 2.0, "rendu": 2.0, "രണ്ട്": 2.0, "൨": 2.0,
    "moonnu": 3.0, "munnu": 3.0, "മൂന്ന്": 3.0, "൩": 3.0,
    "naalu": 4.0, "nallu": 4.0, "നാല്": 4.0, "൪": 4.0,
    "anchu": 5.0, "anju": 5.0, "അഞ്ച്": 5.0, "൫": 5.0,
    "aaru": 6.0, "aru": 6.0, "ആറ്": 6.0, "൬": 6.0,
    "ezhu": 7.0, "ഏഴ്": 7.0, "൭": 7.0,
    "ettu": 8.0, "എട്ട്": 8.0, "൮": 8.0,
    "onpathu": 9.0, "onpadhu": 9.0, "ഒമ്പത്": 9.0, "൯": 9.0,
    "pathu": 10.0, "പത്ത്": 10.0, "൧൦": 10.0,

    # Teens (11-19)
    "pathinonnu": 11.0, "പതിനൊന്ന്": 11.0,
    "pantrandu": 12.0, "പന്ത്രണ്ട്": 12.0,
    "pathinmoonnu": 13.0, "പതിമൂന്ന്": 13.0,
    "pathinaalu": 14.0, "പതിനാല്": 14.0,
    "pathinanchu": 15.0, "പതിനഞ്ച്": 15.0,
    "pathinaaru": 16.0, "പതിനാറ്": 16.0,
    "pathinezhu": 17.0, "പതിനേഴ്": 17.0,
    "pathinettu": 18.0, "പതിനെട്ട്": 18.0,
    "patthonpathu": 19.0, "പത്തൊമ്പത്": 19.0,

    # Tens (20-90)
    "irupathu": 20.0, "ഇരുപത്": 20.0,
    "muppathu": 30.0, "മുപ്പത്": 30.0,
    "nalpathu": 40.0, "നാൽപ്പത്": 40.0,
    "ambathu": 50.0, "അമ്പത്": 50.0,
    "arubathu": 60.0, "അറുപത്": 60.0,
    "ezhupathu": 70.0, "എഴുപത്": 70.0,
    "enbapathu": 80.0, "എൺപത്": 80.0,
    "thonnooru": 90.0, "തൊണ്ണൂറ്": 90.0,

    # Multipliers
    "nooru": 100.0, "നൂറ്": 100.0,
    "innooru": 200.0, "ഇരുന്നൂറ്": 200.0,
    "munnooru": 300.0, "മുന്നൂറ്": 300.0,
    "naanooru": 400.0, "നാനൂറ്": 400.0,
    "anchooru": 500.0, "അഞ്ഞൂറ്": 500.0,
    "aarnooru": 600.0, "ആറുന്നൂറ്": 600.0,
    "ezhnooru": 700.0, "എഴുന്നൂറ്": 700.0,
    "ettnooru": 800.0, "എണ്ണൂറ്": 800.0,
    "thollayiram": 900.0, "തൊള്ളായിരം": 900.0,

    "aayiram": 1000.0, "ayiram": 1000.0, "ആയിരം": 1000.0,
    "randaayiram": 2000.0, "രണ്ടായിരം": 2000.0,
    "anchaayiram": 5000.0, "അഞ്ചായിരം": 5000.0,
    "pathinaayiram": 10000.0, "പതിനായിരം": 10000.0,
    "laksham": 100000.0, "lakh": 100000.0, "ലക്ഷം": 100000.0,
    "kodi": 10000000.0, "crore": 10000000.0, "കോടി": 10000000.0,
}

MALAYALAM_TEMPORAL_LEXICON: Dict[str, int] = {
    "innale": -1, "ഇന്നലെ": -1,
    "innu": 0, "ഇന്ന്": 0,
    "naale": 1, "നാളെ": 1,
    "mattedhu": 2, "mattannal": 2, "മറ്റന്നാൾ": 2,
    "adutha aazhcha": 7, "adutha varam": 7, "അടുത്ത ആഴ്ച": 7,
    "kazhinja aazhcha": -7, "കഴിഞ്ഞ ആഴ്ച": -7,
    "ee aazhcha": 0, "ഈ ആഴ്ച": 0,
    "adutha maasam": 30, "അടുത്ത മാസം": 30,
    "kazhinja maasam": -30, "കഴിഞ്ഞ മാസം": -30
}

MALAYALAM_DAYS_OF_WEEK: Dict[str, int] = {
    "thinkal": 0, "thinkalaazhcha": 0, "തിങ്കൾ": 0, "തിങ്കളാഴ്ച": 0,
    "chovva": 1, "chovvaazhcha": 1, "ചൊവ്വ": 1, "ചൊവ്വാഴ്ച": 1,
    "budhan": 2, "budhanaazhcha": 2, "ബുധൻ": 2, "ബുധനാഴ്ച": 2,
    "vyaazham": 3, "vyaazhaazhcha": 3, "വ്യാഴം": 3, "വ്യാഴാഴ്ച": 3,
    "velli": 4, "velliaazhcha": 4, "വെള്ളി": 4, "വെള്ളിയാഴ്ച": 4,
    "shani": 5, "shaniaazhcha": 5, "ശനി": 5, "ശനിയാഴ്ച": 5,
    "njaayar": 6, "njaayaraazhcha": 6, "ഞായർ": 6, "ഞായറാഴ്ച": 6
}

MALAYALAM_MONTHS: Dict[str, int] = {
    "ജനുവരി": 1, "ഫെബ്രുവരി": 2, "മാർച്ച്": 3, "ഏപ്രിൽ": 4, "മേയ്": 5, "ജൂൺ": 6,
    "ജൂലൈ": 7, "ഓഗസ്റ്റ്": 8, "സെപ്റ്റംബർ": 9, "ഒക്ടോബർ": 10, "നവംബർ": 11, "ഡിസംബർ": 12,
    "ചിങ്ങം": 8, "കന്നി": 9, "തുലാം": 10, "വൃശ്ചികം": 11, "ധനു": 12, "മകരം": 1,
    "കുംഭം": 2, "മീനം": 3, "മേടം": 4, "ഇടവം": 5, "മിഥുനം": 6, "കർക്കിടകം": 7
}

MALAYALAM_DIRECTION_MARKERS = {
    "DATIVE_POSTPOSITIONS": ["kku", "inu", "lekku", "kk", "nu", "ക്ക്", "ഇന്", "ലേക്ക്", "അടുത്തേക്ക്", "ന്", "നു"],
    "ABLATIVE_POSTPOSITIONS": ["il ninnu", "ninnu", "thante pakkal ninnu", "thante", "ൽ നിന്ന്", "നിന്ന്"],
    "PAID_BY_BUSINESS_VERBS": [
        "njan koduthu", "njangal koduthu", "koduthu", "koduthittund", "koduthekkunnu", "pay cheythu", "koduthu theerthu",
        "ഞാൻ കൊടുത്തു", "ഞങ്ങൾ കൊടുത്തു", "കൊടുത്തു", "കൊടുത്തുതീർത്തു"
    ],
    "PAID_BY_CUSTOMER_VERBS": [
        "thannu", "thannittund", "kittiyath", "nalkiyath", " അടച്ചു",
        "തന്നു", "ലഭിച്ചു", "തന്നിട്ടുണ്ട്"
    ],
    "PAYABLE_VERBS": [
        "kodukkanam", "kodukkanund", "nalkanam", "kodukkendathund", "baaki und",
        "കൊടുക്കണം", "കൊടുക്കാനുണ്ട്", "നൽകാനുണ്ട്", "ബാക്കി ഉണ്ട്"
    ],
    "RECEIVABLE_VERBS": [
        "tharanam", "tharanund", "kittanam", "kittanund", "vasool aakkanam",
        "തരണം", "തരാനുണ്ട്", "ലഭിക്കാനുണ്ട്", "കിട്ടാനുണ്ട്"
    ],
    "PROMISE_VERBS": [
        "tharaam", "tharaam ennu paranju", "nalkaam ennu paranju", "paranju",
        "തരാം", "തരാമെന്ന് പറഞ്ഞു", "നൽകാമെന്ന് പറഞ്ഞു"
    ],
    "SETTLEMENT_VERBS": ["kanakku theernnu", "kanakku theerthu", "settle aayi", "കണക്ക് തീർത്തു", "കണക്ക് കഴിഞ്ഞു"]
}

MALAYALAM_HONORIFICS = ["chetan", "chettan", "chechi", "ikka", "sahib", "sir", "ചേട്ടൻ", "ചേച്ചി", "ഇക്ക", "സാഹിബ്"]
MALAYALAM_BUSINESS_TERMS = {
    "kada": "shop", "vyaaparam": "trade", "stores": "stores", "supermarket": "supermarket", "panam": "money", "baki": "balance",
    "കട": "shop", "വ്യാപാരം": "trade", "സ്റ്റോർസ്": "stores", "പണം": "money"
}
