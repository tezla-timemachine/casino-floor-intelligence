"""Score the automatic fresh test (D26): 20 unseen images, product setting, 3 runs each.

    .venv/bin/python scripts/score_fresh.py

There are no hand counts for these images, so accuracy isn't scored. What is scored:
  - consistency: the 3 counts agree within ±1 or 20% (the D13 measure), and the exact same count all 3 times;
  - whether the rule-based crowd level and congestion stay the same across the 3 runs;
  - answers in the form, rejected answers, speed and cost against the monitoring limits (D22);
  - how many results go to review, and why (D21);
  - a floor check against the dataset's labels: the labels miss people but rarely invent them, so a count
    below the labelled count is a likely miss.

Writes evals/results/20261123_fresh_per_image.csv and prints the figures for the write-up.
"""
from __future__ import annotations

import json
from collections import Counter

import pandas as pd

import insights as ins
import pipeline as pl

RUNS = [f"20261123_claude-opus-5-5-medium_v3.1_fresh{i}" for i in (1, 2, 3)]
OUT = pl.ROOT / "evals" / "results"


def within(a: float, b: float) -> bool:
    return abs(a - b) <= max(1, 0.2 * max(a, b))


def main():
    recs = [json.loads(line) for run in RUNS for line in open(pl.RESULTS / "runs" / f"{run}.jsonl")]
    labels = pd.read_csv(pl.ROOT / "evals" / "fresh_set_dataset_labels.csv").set_index("eval_id").labelled_people
    fresh = pd.read_csv(pl.ROOT / "evals" / "fresh_set.csv").set_index("eval_id")
    reasons = Counter()
    rows = []
    for r in recs:
        a = r.get("answer") or {}
        ok = r["status"] == "ok"
        why = ins.review_reasons(r)
        reasons.update(x.split(" (")[0] for x in why)
        rows.append({"eval_id": r["eval_id"], "run": r["run"][-1], "status": r["status"], "seconds": r["seconds"],
                     "cost": r["cost_usd"], "count": a.get("people_count") if ok else None,
                     "confidence": a.get("confidence"),
                     "level": ins.crowd_level(a["people_count"]) if ok else None,
                     "congestion": ins.congestion(ins.grid(a))[0] if ok else None, "review": bool(why), "reasons": "; ".join(why)})
    d = pd.DataFrame(rows)
    per = []
    for eid, g in d.sort_values("run").groupby("eval_id"):
        c = g["count"].dropna().tolist()
        per.append({"eval_id": eid, "group": fresh.loc[eid, "chosen_as"], "labelled": int(labels[eid]),
                    "counts": " / ".join(str(int(x)) for x in c), "spread": max(c) - min(c) if c else None,
                    "within_margin": len(c) == 3 and all(within(x, y) for x in c for y in c),
                    "same_count": len(c) == 3 and len(set(c)) == 1,
                    "same_level": g.level.nunique() == 1, "same_congestion": g.congestion.nunique() == 1,
                    "level": " / ".join(g.level.astype(str)), "confidence": " / ".join(g.confidence.astype(str)),
                    "below_labels": bool(c) and min(c) < labels[eid], "reviewed_runs": int(g.review.sum())})
    p = pd.DataFrame(per)
    p.to_csv(OUT / "20261123_fresh_per_image.csv", index=False)

    n = len(d)
    print(f"calls {n}; ok {int((d.status == 'ok').sum())}; statuses {d.status.value_counts().to_dict()}")
    print(f"avg seconds {d.seconds.mean():.1f} (max {d.seconds.max():.1f}); avg cost ${d.cost.mean():.4f} (max ${d.cost.max():.4f}); total ${d.cost.sum():.2f}")
    print(f"over 15 s: {int((d.seconds > 15).sum())}; over $0.025: {int((d.cost > 0.025).sum())}")
    print(f"confidence {d.confidence.value_counts().to_dict()}")
    print(f"within margin all 3: {int(p.within_margin.sum())}/20 = {100 * p.within_margin.mean():.0f}%")
    print(f"same count all 3: {int(p.same_count.sum())}/20 = {100 * p.same_count.mean():.0f}%")
    print(f"same crowd level: {int(p.same_level.sum())}/20; same congestion: {int(p.same_congestion.sum())}/20")
    print(f"results sent to review: {int(d.review.sum())}/{n} = {100 * d.review.mean():.0f}%; reasons {dict(reasons)}")
    print(f"images with a count below the labels (any run): {int(p.below_labels.sum())}")
    print(p.to_string(index=False))


if __name__ == "__main__":
    main()
