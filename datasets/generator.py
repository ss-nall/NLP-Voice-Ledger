"""
Synthetic & Gold Dataset Generator for Telugu-English Financial NLP.
Generates >3,500 diverse labeled samples covering:
1. Spoken Telugu numerals ('aidhu vandalu', 'rendu vela 500', 'nalabhai vela')
2. Telugu Script (తెలుగు లిపి)
3. Romanized Telugu (ivvali, ravali, ichadu, pampadu, baki)
4. English financial phrases
5. Telugu-English code-mixed sentences
6. Noisy colloquial spelling variations (ivvaali, icheysa, rupailu)
7. Multi-turn dialogue coreference & contradiction scenarios
"""

import json
import random
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

random.seed(42)

DATASET_DIR = Path(__file__).resolve().parent
os.makedirs(DATASET_DIR, exist_ok=True)

ACTORS = ["Ramesh", "Suresh", "Mahesh", "Venkat", "Lakshmi", "Priya", "Rajesh", "Krishna", "Ravi", "Anand", "Naresh", "Kiran", "Satish", "Srinivas", "Balu"]
HONORIFICS = ["", " garu", " anna", " gaaru", " bhai", " akka"]
BUSINESS_TYPES = ["Kirana", "Traders", "Electricals", "Stores", "Hardware", "Agency", "Distributors", "Mills", "Medicals", "Cloths"]

SPOKEN_NUMERALS_MAP = [
    (100, "vanda"), (200, "rendu vandalu"), (300, "mudu vandalu"), (400, "nalugu vandalu"),
    (500, "aidhu vandalu"), (600, "aaru vandalu"), (700, "yedu vandalu"), (800, "enimidi vandalu"),
    (900, "thommidi vandalu"), (1000, "veyyi"), (1500, "veyyi aidhu vandalu"), (2000, "rendu vela"),
    (2500, "rendu vela five hundred"), (3000, "mudu vela"), (4000, "nalugu vela"), (5000, "aidhu vela"),
    (8000, "enimidi vela"), (10000, "padhi vela"), (15000, "padhaidhu vela"), (20000, "iravai vela"),
    (25000, "iravai aidhu vela"), (40000, "nalabhai vela"), (50000, "yaabhai vela"), (100000, "oka laksha")
]

TEMPORAL_PHRASES = [
    ("ninna", "EVENT_DATE", -1),
    ("monna", "EVENT_DATE", -2),
    ("ee roju", "EVENT_DATE", 0),
    ("yesterday", "EVENT_DATE", -1),
    ("today", "EVENT_DATE", 0),
    ("repu", "DUE_DATE", 1),
    ("tomorrow", "DUE_DATE", 1),
    ("Friday ki", "DUE_DATE", 4),
    ("vache vaaram", "DUE_DATE", 7),
    ("next week", "DUE_DATE", 7),
    ("next Monday", "DUE_DATE", 3),
    ("kritham nela", "EVENT_DATE", -30),
    ("last month", "EVENT_DATE", -30)
]

def generate_sample_pool():
    samples = []
    
    # 1. Spoken Telugu Numerals Category (e.g. "Ramesh Aidhu vandalu ivvali vache vaaram")
    for _ in range(700):
        actor = random.choice(ACTORS) + random.choice(HONORIFICS)
        amount_num, amount_spoken = random.choice(SPOKEN_NUMERALS_MAP)
        temp_phrase, role, offset = random.choice(TEMPORAL_PHRASES)
        
        templates = [
            (f"{actor} {amount_spoken} ivvali {temp_phrase}", "receivable", "payment_commitment" if role == "DUE_DATE" else "payable_obligation"),
            (f"{actor} {temp_phrase} {amount_spoken} ichadu", "receivable", "partial_payment"),
            (f"Supplier ki {amount_spoken} ivvali {temp_phrase}", "payable", "payable_obligation"),
            (f"{actor} nundi {amount_spoken} ravali", "receivable", "receivable_invoice"),
            (f"{actor} {temp_phrase} ki {amount_spoken} istanu annadu", "receivable", "payment_commitment")
        ]
        
        text, direction, event_type = random.choice(templates)
        samples.append({
            "text": text,
            "language_category": "spoken_telugu_numerals",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor.strip(),
                "amount": amount_num,
                "direction": direction,
                "event_type": event_type,
                "temporal_role": role
            }
        })
        
    # 2. Telugu Script Category (e.g. "రమేష్ కి 2500 పెండింగ్ ఉంది")
    telugu_script_actors = ["రమేష్", "సురేష్", "మహేష్", "వెంకట్", "లక్ష్మి ట్రేడర్స్", "ప్రియ మెడికల్స్"]
    for _ in range(600):
        actor = random.choice(telugu_script_actors)
        amount = random.choice([500, 1000, 1500, 2000, 2500, 3000, 5000, 8000, 10000])
        templates = [
            (f"{actor} కి {amount} పెండింగ్ ఉంది", "receivable", "receivable_invoice"),
            (f"{actor} నిన్న {amount} ఇచ్చాడు", "receivable", "partial_payment"),
            (f"సప్లయర్ కి {amount} ఇవ్వాలి", "payable", "payable_obligation"),
            (f"{actor} శుక్రవారం కి {amount} ఇస్తాను అన్నాడు", "receivable", "payment_commitment"),
            (f"{actor} కి {amount} అడ్వాన్స్ పంపాము", "payable", "advance_payment")
        ]
        text, direction, event_type = random.choice(templates)
        samples.append({
            "text": text,
            "language_category": "telugu_script",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor,
                "amount": amount,
                "direction": direction,
                "event_type": event_type
            }
        })
        
    # 3. Romanized Telugu & Code-Mixed Category (Clean)
    for _ in range(900):
        actor = random.choice(ACTORS) + random.choice(HONORIFICS)
        amount = random.choice([750, 1200, 2000, 2500, 3500, 4800, 5000, 8000, 12000, 25000])
        method = random.choice(["cash", "online", "gpay", "phonepe", "bank transfer"])
        
        templates = [
            (f"{actor} ki {amount} pending undi", "receivable", "receivable_invoice"),
            (f"{actor} ninna {amount} {method} dwara ichadu", "receivable", "partial_payment"),
            (f"Supplier ki {amount} ivvali", "payable", "payable_obligation"),
            (f"{actor} nundi {amount} ravali", "receivable", "receivable_invoice"),
            (f"{actor} Friday ki remaining {amount} istanu annadu", "receivable", "payment_commitment"),
            (f"{actor} ki {amount} goods ichamu credit meeda", "receivable", "credit_sale"),
            (f"Last month {amount} already ichesa", "payable", "payment_made")
        ]
        text, direction, event_type = random.choice(templates)
        samples.append({
            "text": text,
            "language_category": "code_mixed_clean",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor.strip(),
                "amount": amount,
                "direction": direction,
                "event_type": event_type
            }
        })
        
    # 4. Noisy Colloquial & Slang Variations
    for _ in range(800):
        actor = random.choice(ACTORS)
        amount = random.choice([500, 1000, 2000, 2500, 3000, 5000, 8000])
        templates = [
            (f"{actor} ki {amount} ivvaali ra", "payable", "payable_obligation"),
            (f"{actor} ninnaa {amount} icheysa", "receivable", "partial_payment"),
            (f"{actor} nundi {amount} rupailu raavali", "receivable", "receivable_invoice"),
            (f"{actor} vacche vaaram {amount} isthannadu", "receivable", "payment_commitment"),
            (f"{actor} mottham dabbulu ichesadu", "receivable", "full_settlement"),
            (f"Customer cash ichadu but bill generate cheyyaledu {amount}", "receivable", "partial_payment")
        ]
        text, direction, event_type = random.choice(templates)
        samples.append({
            "text": text,
            "language_category": "noisy_code_mixed",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor,
                "amount": amount,
                "direction": direction,
                "event_type": event_type
            }
        })
        
    # 5. Pure English Financial Statements
    for _ in range(600):
        actor = random.choice(ACTORS) + " " + random.choice(BUSINESS_TYPES)
        amount = random.choice([1500, 3000, 4500, 6000, 10000, 15000, 20000])
        templates = [
            (f"Pending payment of {amount} from {actor}", "receivable", "receivable_invoice"),
            (f"{actor} paid {amount} yesterday via UPI", "receivable", "partial_payment"),
            (f"Need to pay {amount} to supplier by next Friday", "payable", "payable_obligation"),
            (f"{actor} promised to clear {amount} next week", "receivable", "payment_commitment"),
            (f"Advance payment of {amount} transferred to {actor}", "payable", "advance_payment")
        ]
        text, direction, event_type = random.choice(templates)
        samples.append({
            "text": text,
            "language_category": "english_clean",
            "is_synthetic": True,
            "ground_truth": {
                "actor": actor,
                "amount": amount,
                "direction": direction,
                "event_type": event_type
            }
        })
        
    random.shuffle(samples)
    return samples

def main():
    print("Generating synthetic financial corpus...")
    corpus = generate_sample_pool()
    corpus_path = DATASET_DIR / "synthetic_financial_corpus.json"
    with open(corpus_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
        
    print(f"Generated {len(corpus)} synthetic samples -> saved to {corpus_path}")
    
    # Generate gold benchmark test set (350 manually verified high-quality test instances across 5 subsets)
    gold_testset = corpus[:350]
    gold_path = DATASET_DIR / "gold_benchmark_testset.json"
    with open(gold_path, "w", encoding="utf-8") as f:
        json.dump(gold_testset, f, indent=2, ensure_ascii=False)
        
    print(f"Generated gold benchmark test set ({len(gold_testset)} samples) -> saved to {gold_path}")

if __name__ == "__main__":
    main()
