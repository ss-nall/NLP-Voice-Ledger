import json
from backend.app.nlp.pipeline import nlp_pipeline

with open('datasets/gold_benchmark_testset.json', 'r', encoding='utf-8') as f:
    ts = json.load(f)

print(f"Total samples: {len(ts)}")
mismatches = []
for idx, item in enumerate(ts):
    res = nlp_pipeline.process_text(item['text'], session_id='test', is_spoken=True)
    ev = res.event
    gt = item['ground_truth']
    amount_match = (ev.amount == gt["amount"]) or (gt["amount"] == 0 and ev.event_type == "full_settlement")
    dir_match = (ev.direction == gt["direction"])
    if not (amount_match and dir_match):
        mismatches.append((idx, item['language_category'], item['text'], gt, ev))

print(f"Total mismatches: {len(mismatches)}")
for idx, cat, text, gt, ev in mismatches[:20]:
    print(f"#{idx} [{cat}]: '{text}'")
    print(f"   Expected: amount={gt.get('amount')}, dir={gt.get('direction')}, type={gt.get('event_type')}")
    print(f"   Got:      amount={ev.amount}, dir={ev.direction}, type={ev.event_type}, actor={ev.actor}")
