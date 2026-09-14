"""
Scientific Benchmark Runner.
Evaluates the explicit Telugu-English bookkeeping NLP pipeline
across all 5 linguistic categories on the gold standard testset.
"""

import json
import time
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.nlp.pipeline import nlp_pipeline

DATASET_DIR = Path(__file__).resolve().parent.parent / "datasets"
EVAL_DIR = Path(__file__).resolve().parent

def run_evaluation() -> Dict[str, Any]:
    gold_path = DATASET_DIR / "gold_benchmark_testset.json"
    if not gold_path.exists():
        raise FileNotFoundError(f"Gold benchmark not found at {gold_path}. Run datasets/generator.py first.")
        
    with open(gold_path, "r", encoding="utf-8") as f:
        testset = json.load(f)
        
    category_stats = {}
    total_samples = len(testset)
    total_exact_matches = 0
    total_amount_matches = 0
    total_direction_matches = 0
    total_event_type_matches = 0
    total_latency_ms = 0.0
    
    for item in testset:
        text = item["text"]
        cat = item["language_category"]
        gt = item["ground_truth"]
        
        if cat not in category_stats:
            category_stats[cat] = {
                "count": 0,
                "exact_matches": 0,
                "amount_matches": 0,
                "direction_matches": 0,
                "event_type_matches": 0,
                "latencies_ms": []
            }
            
        t0 = time.time()
        res = nlp_pipeline.process_text(text, session_id="benchmark_session", is_spoken=True)
        latency = (time.time() - t0) * 1000.0
        
        ev = res.event
        
        # Check Amount Match
        amount_match = (ev.amount == gt["amount"]) or (gt["amount"] == 0 and ev.event_type == "full_settlement")
        # Check Direction Match
        direction_match = ev.direction == gt["direction"]
        # Check Event Type Match
        event_match = ev.event_type == gt["event_type"] or (ev.event_type in ["partial_payment", "payment_made"] and gt["event_type"] in ["partial_payment", "payment_made"])
        
        exact = amount_match and direction_match
        
        category_stats[cat]["count"] += 1
        category_stats[cat]["latencies_ms"].append(latency)
        if amount_match:
            category_stats[cat]["amount_matches"] += 1
            total_amount_matches += 1
        if direction_match:
            category_stats[cat]["direction_matches"] += 1
            total_direction_matches += 1
        if event_match:
            category_stats[cat]["event_type_matches"] += 1
            total_event_type_matches += 1
        if exact:
            category_stats[cat]["exact_matches"] += 1
            total_exact_matches += 1
            
        total_latency_ms += latency
        
    # Compile results
    summary_by_cat = {}
    for cat, stats in category_stats.items():
        n = stats["count"]
        summary_by_cat[cat] = {
            "samples": n,
            "exact_match_pct": round((stats["exact_matches"] / n) * 100, 2),
            "amount_match_pct": round((stats["amount_matches"] / n) * 100, 2),
            "direction_match_pct": round((stats["direction_matches"] / n) * 100, 2),
            "avg_latency_ms": round(sum(stats["latencies_ms"]) / n, 2)
        }
        
    overall_report = {
        "benchmark_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_test_samples": total_samples,
        "overall_exact_match_pct": round((total_exact_matches / total_samples) * 100, 2),
        "overall_amount_match_pct": round((total_amount_matches / total_samples) * 100, 2),
        "overall_direction_accuracy_pct": round((total_direction_matches / total_samples) * 100, 2),
        "overall_event_type_accuracy_pct": round((total_event_type_matches / total_samples) * 100, 2),
        "avg_end_to_end_latency_ms": round(total_latency_ms / total_samples, 2),
        "category_breakdown": summary_by_cat
    }
    
    report_path = EVAL_DIR / "benchmark_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(overall_report, f, indent=2)
        
    print("=" * 60)
    print("BILINGUAL FINANCIAL NLP BENCHMARK EVALUATION RESULTS")
    print("=" * 60)
    print(f"Total Evaluated Samples: {total_samples}")
    print(f"Overall Ground Truth Exact Match: {overall_report['overall_exact_match_pct']}%")
    print(f"Amount Exact Match Accuracy:    {overall_report['overall_amount_match_pct']}%")
    print(f"Direction Extraction Accuracy:  {overall_report['overall_direction_accuracy_pct']}%")
    print(f"Average Pipeline Latency:       {overall_report['avg_end_to_end_latency_ms']} ms")
    print("-" * 60)
    print("CATEGORY BREAKDOWN:")
    for cat, data in summary_by_cat.items():
        print(f"  • {cat.ljust(25)}: Exact Match {data['exact_match_pct']}% | Latency {data['avg_latency_ms']} ms")
    print("=" * 60)
    
    return overall_report

if __name__ == "__main__":
    run_evaluation()
