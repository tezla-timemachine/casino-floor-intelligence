"""Score evaluation runs against the hand counts (evaluation plan 07, sections 2 and 5).

    .venv/bin/python scripts/score_eval.py --name prompts

Reads evals/eval_set.csv (the true counts) and every data/results/runs/*_<name>*.jsonl.
Writes evals/results/<date>_<name>.md (the summary) and evals/results/<date>_<name>_per_image.csv (the brief's
table: image, actual, model count, difference, result, for every run).

A count is "within" when it misses by no more than 1 person, or 20% of the true count, whichever is larger (07).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import json
from pathlib import Path

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import insights as ins  # crowd-level rule (D14)
import pipeline as pl  # thirds from either answer form

ROOT = Path(__file__).resolve().parents[1]
EVALS, RUNS = ROOT / "evals", ROOT / "data" / "results" / "runs"


def band(n: float) -> str:
    return "0" if n == 0 else "1-5" if n <= 5 else "6-15" if n <= 15 else "16-50" if n <= 50 else "over 50"


def load(name: str) -> pd.DataFrame:
    truth = pd.read_csv(EVALS / "eval_set.csv")
    for c in ("count_best", "count_low", "count_high", "left", "centre", "right"):
        truth[c] = pd.to_numeric(truth[c])
    rows = []
    for path in sorted(glob.glob(str(RUNS / f"*_{name}*.jsonl"))):
        for line in open(path):
            r = json.loads(line)
            a = r.get("answer") or {}
            t = (pl.thirds(a) if a else {}) or {}
            rows.append({"run": r["run"], "model": r["model"], "prompt": r["prompt_version"], "file": r["file"], "status": r["status"],
                         "model_count": a.get("people_count"), "confidence": a.get("confidence", ""), "crowd_level": a.get("crowd_level", ""),
                         "congestion": a.get("congestion", ""), "m_left": t.get("left"), "m_centre": t.get("centre"), "m_right": t.get("right"),
                         "summary": a.get("operational_summary", a.get("raw_text", "")), "seconds": r["seconds"], "cost": r["cost_usd"],
                         "output_tokens": r["output_tokens"]})
    d = pd.DataFrame(rows).merge(truth, on="file", how="left")
    d["actual"] = d.count_best
    d["difference"] = d.model_count - d.actual
    d["abs_error"] = d.difference.abs()
    d["allowed"] = np.maximum(1, 0.2 * d.actual)
    d["within"] = d.abs_error <= d.allowed
    d["in_range"] = (d.model_count >= d.count_low) & (d.model_count <= d.count_high)
    d["result"] = np.where(d.model_count.isna(), "no count", np.where(d.within, "good", np.where(d.difference > 0, "over", "under")))
    d["band"] = d.actual.map(band)
    d["rule_level_model"] = d.model_count.map(lambda n: ins.crowd_level(int(n)) if pd.notna(n) else "")
    d["rule_level_true"] = d.actual.map(lambda n: ins.crowd_level(int(n)))
    d["level_agrees"] = d.rule_level_model == d.rule_level_true
    thirds = ["left", "centre", "right"]
    d["true_busiest"] = d[thirds].idxmax(axis=1).where(d[thirds].max(axis=1) > 0, "none")
    m3 = d[["m_left", "m_centre", "m_right"]].astype(float)
    d["model_busiest"] = m3.fillna(-1).idxmax(axis=1).str[2:].where(m3.max(axis=1) > 0, "none").where(m3.notna().all(axis=1), "")
    return d


def summarise(g: pd.DataFrame) -> dict:
    counted = g[g.model_count.notna()]
    structured = g[g.prompt != "v1"]
    return {"images": len(g),
            "counted": len(counted),
            "avg_miss": round(counted.abs_error.mean(), 1) if len(counted) else None,
            "median_miss": round(counted.abs_error.median(), 1) if len(counted) else None,
            "within_pct": round(100 * counted.within.mean()) if len(counted) else None,
            "in_range_pct": round(100 * counted.in_range.mean()) if len(counted) else None,
            "lean": round(counted.difference.mean(), 1) if len(counted) else None,
            "crowd_level_agree_pct": round(100 * g.level_agrees[g.model_count.notna()].mean()) if len(counted) else None,
            "busiest_third_pct": round(100 * (g.model_busiest == g.true_busiest)[g.prompt != "v1"].mean()) if len(structured) else None,
            "form_ok_pct": round(100 * (g.status == "ok").mean()),
            "avg_cost": round(g.cost.mean(), 4), "total_cost": round(g.cost.sum(), 3), "avg_seconds": round(g.seconds.mean(), 1)}


def table(df: pd.DataFrame, cols: list[str]) -> list[str]:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |" for r in df[cols].itertuples(index=False)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    args = ap.parse_args()
    d = load(args.name)
    stamp = f"{dt.date.today():%Y%m%d}_{args.name}"
    (EVALS / "results").mkdir(exist_ok=True)
    d[["model", "prompt", "run", "eval_id", "chosen_as", "lighting", "angle", "actual", "count_low", "count_high", "model_count",
       "difference", "result", "in_range", "confidence", "crowd_level", "congestion", "true_busiest", "model_busiest", "status",
       "seconds", "cost", "summary"]].sort_values(["model", "prompt", "run", "eval_id"]).to_csv(EVALS / "results" / f"{stamp}_per_image.csv", index=False)

    overall = pd.DataFrame([{"model": m, "prompt": p, **summarise(g)} for (m, p), g in d.groupby(["model", "prompt"])])
    lines = [f"# Evaluation results: {args.name} ({dt.date.today():%d %b %Y})", "",
             "True counts: Tez's hand counts (D3, D10). \"Within\" = misses by no more than 1 person or 20% of the true count, whichever is larger. "
             "\"In range\" = inside Tez's low-high range. \"Lean\" = average (model minus true): positive counts too high.", "",
             "## Overall, by model and prompt", ""]
    lines += table(overall, ["model", "prompt", "counted", "avg_miss", "median_miss", "within_pct", "in_range_pct", "lean",
                             "crowd_level_agree_pct", "busiest_third_pct", "form_ok_pct", "avg_cost", "avg_seconds", "total_cost"])
    for by, title in [("band", "By true number of people"), ("chosen_as", "By group in the evaluation set"),
                      ("lighting", "By lighting"), ("angle", "By camera angle"), ("confidence", "By the model's confidence")]:
        rows = []
        for (m, p, k), g in d[d.prompt != "v1"].groupby(["model", "prompt", by]):
            s = summarise(g); rows.append({"model": m, "prompt": p, by: k, "images": s["images"], "avg_miss": s["avg_miss"],
                                           "within_pct": s["within_pct"], "lean": s["lean"]})
        lines += ["", f"## {title} (prompts v2 and v3)", ""] + table(pd.DataFrame(rows), ["model", "prompt", by, "images", "avg_miss", "within_pct", "lean"])
    worst = d[d.model_count.notna()].sort_values("abs_error", ascending=False).head(10)
    lines += ["", "## The 10 biggest misses", ""] + table(worst, ["model", "prompt", "eval_id", "chosen_as", "actual", "model_count", "difference", "confidence"])
    (EVALS / "results" / f"{stamp}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:12 + len(overall)]))


if __name__ == "__main__":
    main()
