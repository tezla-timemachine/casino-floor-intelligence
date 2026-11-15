"""Model monitoring (brief Step 17, FR-16, FR-17): what is tracked, and when the model needs investigation.

Tracked from data/results/call_log.csv (every model call), data/results/reviews.csv (human review decisions)
and the latest evaluation scores (evals/results/*_per_image.csv).

Alert rules (proposed in Phase 6; values to approve). Each is checked over the last WINDOW calls of the
product setting (model and prompt in PRODUCT):
  failed requests        more than 5% of calls fail (API errors, no credit, local model down)
  rejected answers       more than 5% don't fit the form or fail the sense check
  low confidence         more than 30% of answers say low confidence
  response time          average over 15 seconds per image
  cost                   average over $0.025 per image (BRD 02, CR-10)
  review outcomes        more than 20% of reviewed results marked incorrect (once 10 or more are reviewed)
  evaluation             the latest evaluation run fails any pass mark (D13, D18)
"""
from __future__ import annotations

import glob
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS, EVALS = ROOT / "data" / "results", ROOT / "evals" / "results"
PRODUCT = {"model": "claude-opus-5-5", "prompt_version": "v3.1"}       # D12, D17
WINDOW = 50
LIMITS = {"failed_pct": 5, "rejected_pct": 5, "low_conf_pct": 30, "avg_seconds": 15, "avg_cost": 0.025, "incorrect_pct": 20}
PASS_MARKS = {"within_pct": 85, "avg_miss": 3.0, "small_within_pct": 100, "crowd_within_pct": 75, "crowd_level_pct": 85}


def calls() -> pd.DataFrame:
    c = pd.read_csv(RESULTS / "call_log.csv")
    for k in ("seconds", "cost_usd"):
        c[k] = pd.to_numeric(c[k], errors="coerce")
    return c


def reviews() -> pd.DataFrame:
    path = RESULTS / "reviews.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame(columns=["time", "run", "file", "eval_id", "reasons", "decision", "note"])


def latest_eval() -> dict:
    """Pass-mark measures from the latest product evaluation run."""
    files = sorted(glob.glob(str(EVALS / "*_grid_per_image.csv")))
    if not files:
        return {}
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import insights as ins
    d = pd.read_csv(files[-1])
    good = d.result == "good"
    level = (d.model_count.map(lambda n: ins.crowd_level(int(n))) == d.actual.map(lambda n: ins.crowd_level(int(n)))).mean()
    return {"file": Path(files[-1]).name, "within_pct": round(100 * good.mean()), "avg_miss": round((d.model_count - d.actual).abs().mean(), 1),
            "small_within_pct": round(100 * good[d.actual <= 5].mean()), "crowd_within_pct": round(100 * good[d.actual >= 16].mean()),
            "crowd_level_pct": round(100 * level)}


def status() -> dict:
    """The tracked measures for the product setting, and any alerts."""
    c = calls()
    prod = c[(c.model == PRODUCT["model"]) & (c.prompt_version == PRODUCT["prompt_version"])].sort_values("time").tail(WINDOW)
    answered = prod[prod.status.isin(["ok", "answer rejected"])]
    r = reviews()
    m = {"calls": len(prod), "model": PRODUCT["model"], "prompt_version": PRODUCT["prompt_version"],
         "failed_pct": round(100 * prod.status.eq("call failed").mean(), 1) if len(prod) else 0,
         "rejected_pct": round(100 * prod.status.eq("answer rejected").mean(), 1) if len(prod) else 0,
         "low_conf_pct": round(100 * answered.confidence.eq("low").mean(), 1) if len(answered) else 0,
         "avg_seconds": round(answered.seconds.mean(), 1) if len(answered) else 0,
         "avg_cost": round(answered.cost_usd.mean(), 4) if len(answered) else 0,
         "reviews": len(r), "incorrect_pct": round(100 * r.decision.eq("incorrect").mean(), 1) if len(r) else 0}
    alerts = []
    for k, label in [("failed_pct", "failed requests"), ("rejected_pct", "rejected answers"), ("low_conf_pct", "low-confidence answers"),
                     ("avg_seconds", "average response time (s)"), ("avg_cost", "average cost per image ($)")]:
        if m[k] > LIMITS[k]:
            alerts.append(f"{label}: {m[k]} (limit {LIMITS[k]})")
    if m["reviews"] >= 10 and m["incorrect_pct"] > LIMITS["incorrect_pct"]:
        alerts.append(f"reviews marked incorrect: {m['incorrect_pct']}% (limit {LIMITS['incorrect_pct']}%)")
    ev = latest_eval()
    for k, mark in PASS_MARKS.items():
        if k in ev and ((k == "avg_miss" and ev[k] > mark) or (k != "avg_miss" and ev[k] < mark)):
            alerts.append(f"evaluation: {k} {ev[k]} misses the pass mark ({mark})")
    return {"measures": m, "evaluation": ev, "alerts": alerts, "window": WINDOW}


if __name__ == "__main__":
    import json
    print(json.dumps(status(), indent=1))
