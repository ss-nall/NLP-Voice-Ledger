"""
Urdu Financial & Numerals Lexicon.
Covers Urdu script & Nastaliq / Romanized Urdu financial numerals, postpositions, and accounting verbs.
"""

from typing import Dict, List

URDU_NUMERALS: Dict[str, float] = {
    # Digits (1-10)
    "ek": 1.0, "ایک": 1.0, "۱": 1.0,
    "do": 2.0, "دو": 2.0, "۲": 2.0,
    "teen": 3.0, "تین": 3.0, "۳": 3.0,
    "chaar": 4.0, "char": 4.0, "چار": 4.0, "۴": 4.0,
    "paanch": 5.0, "panch": 5.0, "پانچ": 5.0, "۵": 5.0,
    "chhe": 6.0, "chheh": 6.0, "چھ": 6.0, "۶": 6.0,
    "saat": 7.0, "سات": 7.0, "۷": 7.0,
    "aath": 8.0, "آٹھ": 8.0, "۸": 8.0,
    "nau": 9.0, "نو": 9.0, "۹": 9.0,
    "das": 10.0, "دس": 10.0, "۱۰": 10.0,

    # Teens (11-19)
    "gyarah": 11.0, "گیارہ": 11.0,
    "barah": 12.0, "بارہ": 12.0,
    "terah": 13.0, "تیرہ": 13.0,
    "chaudah": 14.0, "چودہ": 14.0,
    "pandrah": 15.0, "پندرہ": 15.0,
    "solah": 16.0, "سولہ": 16.0,
    "satrah": 17.0, "سترہ": 17.0,
    "atharah": 18.0, "اٹھارہ": 18.0,
    "unnees": 19.0, "انیس": 19.0,

    # Tens (20-90)
    "bees": 20.0, "بیس": 20.0,
    "tees": 30.0, "تیس": 30.0,
    "chalis": 40.0, "چالیس": 40.0,
    "pachas": 50.0, "پچاس": 50.0,
    "saath": 60.0, "ساٹھ": 60.0,
    "sattar": 70.0, "ستر": 70.0,
    "assi": 80.0, "اسی": 80.0,
    "nabbe": 90.0, "نود": 90.0, "نوے": 90.0,

    # Multipliers
    "sau": 100.0, "سو": 100.0,
    "dosau": 200.0, "do sau": 200.0, "دو سو": 200.0,
    "paanchsau": 500.0, "paanch sau": 500.0, "پانچ سو": 500.0,
    "hazaar": 1000.0, "hazar": 1000.0, "ہزار": 1000.0,
    "dohazaar": 2000.0, "do hazaar": 2000.0, "دو ہزار": 2000.0,
    "paanchhazaar": 5000.0, "paanch hazaar": 5000.0, "پانچ ہزار": 5000.0,
    "dashazaar": 10000.0, "das hazaar": 10000.0, "دس ہزار": 10000.0,
    "laakh": 100000.0, "lakh": 100000.0, "لاکھ": 100000.0,
    "crore": 10000000.0, "karor": 10000000.0, "کروڑ": 10000000.0,
}

URDU_TEMPORAL_LEXICON: Dict[str, int] = {
    "kal": 1, "کل": 1,
    "aaj": 0, "آج": 0,
    "parson": 2, "پرسوں": 2,
    "agle hafte": 7, "اگلے ہفتے": 7, "agla hafta": 7,
    "pichle hafte": -7, "پچھلے ہفتے": -7,
    "is hafte": 0, "اس ہفتے": 0,
    "agle mahine": 30, "اگلے مہینے": 30,
    "pichle mahine": -30, "پچھلے مہینے": -30
}

URDU_DAYS_OF_WEEK: Dict[str, int] = {
    "peer": 0, "somwar": 0, "پیر": 0,
    "mangal": 1, "منگل": 1,
    "budh": 2, "بدھ": 2,
    "jumerat": 3, "جمعرات": 3,
    "jumma": 4, "جمعہ": 4,
    "hafta": 5, "ہفتہ": 5, "sanichar": 5,
    "itwar": 6, "اتوار": 6
}

URDU_MONTHS: Dict[str, int] = {
    "جنوری": 1, "فروری": 2, "مارچ": 3, "اپریل": 4, "مئی": 5, "جون": 6,
    "جولائی": 7, "اگست": 8, "ستمبر": 9, "اکتوبر": 10, "نومبر": 11, "دسمبر": 12,
    "محرم": 1, "صفر": 2, "ربیع الاول": 3, "ربیع الثانی": 4, "جمادی الاول": 5, "جمادی الثانی": 6,
    "رجب": 7, "شعبان": 8, "رمضان": 9, "شوال": 10, "ذی القعدہ": 11, "ذی الحجہ": 12
}

URDU_DIRECTION_MARKERS = {
    "DATIVE_POSTPOSITIONS": ["ko", "keliye", "ke paas", "کو", "کے لیے", "کے پاس"],
    "ABLATIVE_POSTPOSITIONS": ["se", "se lekar", "کی طرف سے", "سے"],
    "AGENT_POSTPOSITIONS": ["ne", "usne", "unhone", "نے", "اس نے", "انہوں نے"],
    "PAID_BY_BUSINESS_VERBS": [
        "maine diya", "humne diya", "maine bhej diya", "humne ada kiya", "ada kardiya", "payment kiya",
        "میں نے دیا", "ہم نے دیا", "ادا کیا", "دے دیا"
    ],
    "PAID_BY_CUSTOMER_VERBS": [
        "diya", "diye", "wasool hua", "jama kiya", "jama hua", "mila", "pahuncha", "ada kiya",
        "وصول ہوا", "جمع کیا", "دیا", "ملا"
    ],
    "PAYABLE_VERBS": [
        "dena hai", "deni hai", "dene hain", "ada karna hai", "wajib ul ada", "baqi hai",
        "دینا ہے", "دینے ہیں", "ادا کرنا ہے", "باقی ہے"
    ],
    "RECEIVABLE_VERBS": [
        "lena hai", "leni hai", "lene hain", "wasool karna hai", "aana hai",
        "لینا ہے", "لینے ہیں", "وصول کرنا ہے", "آنا ہے"
    ],
    "PROMISE_VERBS": [
        "dega", "denge", "dunga", "dene ka wada kiya", "bola de dunga", "wada kiya",
        "دے گا", "دیں گے", "دوں گا", "بولا", "وعدہ کیا"
    ],
    "SETTLEMENT_VERBS": ["hisaab barabar", "hisaab clear", "chuka diya", "حساب برابر", "حساب ختم"]
}

URDU_HONORIFICS = ["sahab", "saheb", "bhai", "janab", "sahiba", "صاحب", "جناب", "بھائی"]
URDU_BUSINESS_TERMS = {
    "dukaan": "shop", "tijarat": "trade", "karobar": "business", "traders": "traders", "agency": "agency",
    "baqi": "balance", "hisaab": "ledger", "raqam": "amount", "roker": "cash",
    "دکان": "shop", "تجارت": "trade", "کاروبار": "business", "باقی": "balance"
}
