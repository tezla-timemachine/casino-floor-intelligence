"""Run the evaluation set through each model and prompt (evaluation plan 07, section 5).

    .venv/bin/python scripts/run_eval.py --prompts v1 v2 v3 --models claude-opus-5-5 claude-sonnet-5-5 --name prompts
    .venv/bin/python scripts/run_eval.py --prompts v3 --models claude-opus-5-5 claude-sonnet-5-5 --repeats 2 --name repeat

Each model x prompt (x repeat) is one run, saved to data/results/runs/<run>.jsonl as answers arrive; every call
is added to data/results/call_log.csv. Stops starting new calls once this session's spend passes --cap dollars.
Prompt v1 is free text (no answer form); v2 and v3 use the form.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic
from dotenv import load_dotenv

import pipeline as pl

FREE_TEXT_PROMPTS = {"v1"}
LOG_FIELDS = ["run", "time", "file", "model", "effort", "model_used", "prompt_version", "status", "problems", "attempts",
              "seconds", "input_tokens", "output_tokens", "cost_usd", "fallback_used", "confidence", "request_id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", nargs="+", required=True)
    ap.add_argument("--models", nargs="+", required=True, choices=list(pl.PRICES))
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--name", required=True)
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--cap", type=float, default=5.0)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    load_dotenv(pl.ROOT / ".env")
    client = anthropic.Anthropic()
    rows = list(csv.DictReader(open(pl.ROOT / "evals" / "eval_set.csv")))
    for r in rows:
        r["group"] = r["chosen_as"]

    jobs = []
    for model in args.models:
        settings = {"model": model, "effort": args.effort, "price_in": pl.PRICES[model][0], "price_out": pl.PRICES[model][1]}
        for prompt_name in args.prompts:
            prompt = (pl.PROMPTS / f"{prompt_name}.txt").read_text()
            for rep in range(1, args.repeats + 1):
                run = f"{dt.date.today():%Y%m%d}_{model}-{args.effort}_{prompt_name}_{args.name}{rep if args.repeats > 1 else ''}"
                for row in rows:
                    jobs.append((run, row, prompt_name, prompt, settings, prompt_name not in FREE_TEXT_PROMPTS))

    print(f"{len(jobs)} calls planned; stop at ${args.cap:.2f}")
    spent, done, lock = 0.0, 0, threading.Lock()
    stop = threading.Event()
    log_path = pl.RESULTS / "call_log.csv"

    def work(job):
        if stop.is_set():
            return None
        run, row, prompt_name, prompt, settings, structured = job
        return pl.analyse(client, row, prompt_name, prompt, run, settings, structured)

    with ThreadPoolExecutor(args.workers) as pool, log_path.open("a", newline="") as log:
        writer = csv.DictWriter(log, fieldnames=LOG_FIELDS, extrasaction="ignore")
        futures = [pool.submit(work, j) for j in jobs]
        for f in as_completed(futures):
            rec = f.result()
            if rec is None:
                continue
            with lock:
                spent += rec["cost_usd"]; done += 1
                with (pl.RESULTS / "runs" / f"{rec['run']}.jsonl").open("a") as out:
                    out.write(json.dumps(rec) + "\n")
                writer.writerow({**rec, "confidence": (rec.get("answer") or {}).get("confidence", "")}); log.flush()
                if spent > args.cap and not stop.is_set():
                    stop.set(); print(f"!! spend ${spent:.2f} passed the ${args.cap:.2f} cap: no new calls")
                if done % 20 == 0:
                    print(f"{done}/{len(jobs)} done, ${spent:.2f} spent", flush=True)
    print(f"finished: {done} calls, ${spent:.4f}")


if __name__ == "__main__":
    main()
