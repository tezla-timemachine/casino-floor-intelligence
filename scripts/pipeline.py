"""Pipeline v1: image check -> prompt -> model adapter -> answer check -> results and call log.

    .venv/bin/python scripts/pipeline.py --images data/results/pipeline_trial_images.csv --prompt trial-1 --run trial

The images CSV needs columns `split` and `file` (and optionally `group`). Each answer is written to
data/results/runs/<run>.jsonl, and every model call to data/results/call_log.csv (FR-16).
The API key is read from .env and never printed.
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import io
import json
import re
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW, RESULTS, PROMPTS = ROOT / "data" / "raw" / "casino-v3", ROOT / "data" / "results", ROOT / "prompts"
PRICES = {"claude-opus-5-5": (4.00 / 1e6, 20.00 / 1e6), "claude-sonnet-5-5": (2.00 / 1e6, 10.00 / 1e6), "moondream": (0.0, 0.0)}   # $ per token, in and out
CLAUDE = {"model": "claude-opus-5-5", "effort": "medium",  # product setting with prompt v3 (D12)
           "price_in": PRICES["claude-opus-5-5"][0], "price_out": PRICES["claude-opus-5-5"][1]}   # D6, CR-02
MAX_BYTES, FORMATS = 5_000_000, {"JPEG": "image/jpeg", "PNG": "image/png"}
CROWD = ["Normal", "Busy", "Highly occupied"]
MAX_PLAUSIBLE = 500                            # more people than this in one image is treated as a broken answer
CONGESTION = ["No visible congestion", "Moderate congestion", "High concentration requiring review"]

# The answer form (architecture 03, section 2.1). Every answer must fill it exactly (FR-04).
SCHEMA = {
    "type": "object",
    "properties": {
        "people_count": {"type": "integer"},
        "people_by_third": {"type": "object", "properties": {"left": {"type": "integer"}, "centre": {"type": "integer"}, "right": {"type": "integer"}},
                            "required": ["left", "centre", "right"], "additionalProperties": False},
        "crowd_level": {"type": "string", "enum": CROWD},
        "main_occupied_area": {"type": "string"},
        "low_activity_area": {"type": "string"},
        "congestion": {"type": "string", "enum": CONGESTION},
        "visible_floor_objects": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
        "operational_summary": {"type": "string"},
    },
    "required": ["people_count", "people_by_third", "crowd_level", "main_occupied_area", "low_activity_area",
                 "congestion", "visible_floor_objects", "confidence", "operational_summary"],
    "additionalProperties": False,
}


# Answer form v2 (CR-12, D15): a 3x3 grid of counts replaces the thirds; used by prompt v3.1 onwards.
ROW = {"type": "object", "properties": {k: {"type": "integer"} for k in ("left", "centre", "right")},
       "required": ["left", "centre", "right"], "additionalProperties": False}
SCHEMA_V2 = {**SCHEMA, "properties": {**{k: v for k, v in SCHEMA["properties"].items() if k != "people_by_third"},
                                      "people_by_grid": {"type": "object", "properties": {r: ROW for r in ("top", "middle", "bottom")},
                                                         "required": ["top", "middle", "bottom"], "additionalProperties": False}},
             "required": [k if k != "people_by_third" else "people_by_grid" for k in SCHEMA["required"]]}
COUNT_ONLY = {"type": "object", "properties": {"people_count": {"type": "integer"}}, "required": ["people_count"], "additionalProperties": False}
FORM_FOR_PROMPT = {"v3.1": SCHEMA_V2, "m-count": COUNT_ONLY}   # prompts not listed use the original form


def form_for(prompt_name: str) -> dict:
    return FORM_FOR_PROMPT.get(prompt_name, SCHEMA)


def thirds(answer: dict) -> dict:
    """People per third (left, centre, right), from either form."""
    if "people_by_grid" in answer:
        g = answer["people_by_grid"]
        return {c: sum(g[r][c] for r in ("top", "middle", "bottom")) for c in ("left", "centre", "right")}
    return answer.get("people_by_third", {})


def check_image(path: Path) -> tuple[bytes, str]:
    """FR-02: the file must open as a supported image and not be too large. Raises ValueError with the reason."""
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError(f"file too large ({len(data):,} bytes)")
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.verify()
            kind = im.format
    except Exception as e:  # noqa: BLE001 - any failure to open means the image is unusable
        raise ValueError(f"not a readable image ({e.__class__.__name__})") from e
    if kind not in FORMATS:
        raise ValueError(f"unsupported format {kind}")
    return data, FORMATS[kind]


def check_answer(answer: dict, schema: dict = SCHEMA) -> list[str]:
    """FR-05: everything the form requires, with values that make sense. Returns the problems found."""
    problems = [f"missing {k}" for k in schema["required"] if k not in answer]
    if problems:
        return problems
    if answer["people_count"] < 0:
        problems.append("negative count")
    if answer["people_count"] > MAX_PLAUSIBLE:
        problems.append(f"implausible count ({answer['people_count']}; over {MAX_PLAUSIBLE})")
    if schema is COUNT_ONLY:
        return problems
    if sum(thirds(answer).values()) != answer["people_count"]:
        problems.append("grid or thirds don't add up to the count")
    if answer["crowd_level"] not in CROWD or answer["congestion"] not in CONGESTION:
        problems.append("level outside the allowed values")
    if not answer["operational_summary"].strip():
        problems.append("empty summary")
    return problems


NUMBER_WORDS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
                                              "fifteen sixteen seventeen eighteen nineteen twenty".split())}
FREE_TEXT_COUNT = re.compile(r"\b(\d+|" + "|".join(NUMBER_WORDS) + r")(?:\s*(?:-|to|–)\s*(\d+))?\s+(?:\w+\s+){0,2}"
                             r"(?:people|persons|individuals|patrons|players|guests|visitors|gamblers|customers)\b", re.I)


TENS = {w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())}
COMPOUND = re.compile(r"\b(" + "|".join(TENS) + r")(?:[-\s](one|two|three|four|five|six|seven|eight|nine))?\b", re.I)


def count_from_text(text: str):
    """Prompt v1 gives free text: take the first stated number of people (the middle of a range). None if there isn't one."""
    text = COMPOUND.sub(lambda m: str(TENS[m.group(1).lower()] + (NUMBER_WORDS[m.group(2).lower()] if m.group(2) else 0)), text or "")
    m = FREE_TEXT_COUNT.search(text)
    if not m:
        return None
    first = int(m.group(1)) if m.group(1).isdigit() else NUMBER_WORDS[m.group(1).lower()]
    return round((first + int(m.group(2))) / 2) if m.group(2) else first


def call_claude(client: anthropic.Anthropic, image: bytes, media_type: str, prompt: str, settings: dict, structured: bool = True,
                schema: dict = SCHEMA) -> dict:
    """The model adapter for Claude: one call, timed and costed (FR-03, FR-16). Settings: model, effort, price_in, price_out."""
    output_config = {"effort": settings["effort"]}
    if structured:
        output_config["format"] = {"type": "json_schema", "schema": schema}
    start = time.time()
    response = client.beta.messages.create(
        model=settings["model"], max_tokens=4000,
        betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        system=prompt, output_config=output_config,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": base64.standard_b64encode(image).decode()}},
            {"type": "text", "text": "Analyse this casino floor image."}]}],
    )
    u = response.usage
    out = {"seconds": round(time.time() - start, 2), "model_used": response.model, "stop_reason": response.stop_reason,
           "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
           "cost_usd": round(u.input_tokens * settings["price_in"] + u.output_tokens * settings["price_out"], 5),
           "fallback_used": any(getattr(e, "type", "") == "fallback_message" for e in (getattr(u, "iterations", None) or [])),
           "request_id": response._request_id}
    text = next((b.text for b in response.content if b.type == "text"), None)
    if not text or response.stop_reason == "refusal":
        out["answer"] = None
    elif structured:
        out["answer"] = json.loads(text)
    else:
        out["answer"] = {"raw_text": text, "people_count": count_from_text(text)}
    return out


OLLAMA = "http://127.0.0.1:11434/api/chat"     # Moondream runs locally through Ollama: nothing leaves this computer (D5)


def call_moondream(image: bytes, prompt: str, schema: dict, model: str = "moondream") -> dict:
    """The model adapter for Moondream: same shape of result as call_claude, cost always 0 (FR-03, FR-16, FR-20)."""
    import urllib.request
    body = {"model": model, "stream": False, "format": schema, "options": {"temperature": 0, "num_predict": 600},
            "messages": [{"role": "user", "content": prompt + "\n\nAnalyse this casino floor image. Answer only with JSON in the required form.",
                          "images": [base64.standard_b64encode(image).decode()]}]}
    start = time.time()
    req = urllib.request.Request(OLLAMA, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        res = json.loads(r.read())
    out = {"seconds": round(time.time() - start, 2), "model_used": model, "stop_reason": res.get("done_reason", ""),
           "input_tokens": res.get("prompt_eval_count", 0), "output_tokens": res.get("eval_count", 0), "cost_usd": 0.0,
           "fallback_used": False, "request_id": ""}
    try:
        out["answer"] = json.loads(res["message"]["content"])
    except (json.JSONDecodeError, KeyError):
        out["answer"] = {"_unparsed": res.get("message", {}).get("content", "")[:500]}
    return out


def analyse(client, row: dict, prompt_name: str, prompt: str, run: str, settings: dict | None = None, structured: bool = True) -> dict:
    """One image through the whole pipeline. Never guesses: failures are recorded with their reason."""
    settings = settings or CLAUDE
    record = {"run": run, "time": dt.datetime.now().isoformat(timespec="seconds"), "split": row["split"], "file": row["file"],
              "group": row.get("group", ""), "eval_id": row.get("eval_id", ""), "path": row.get("path", ""),
              # video-ready (FR-22): a frame is an image + camera + time
              "camera": row.get("camera", ""), "captured_at": row.get("captured_at", ""),
              "model": settings["model"], "effort": settings["effort"],
              "prompt_version": prompt_name, "status": "", "problems": "",
              "attempts": 0, "seconds": 0.0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
    try:
        image, media_type = check_image(Path(row["path"]) if row.get("path") else RAW / row["split"] / row["file"])
    except ValueError as e:
        record.update(status="image rejected", problems=str(e))
        return record
    for attempt in (1, 2):                                   # one retry (FR-05)
        record["attempts"] = attempt
        try:
            if settings["model"].startswith("moondream"):
                call = call_moondream(image, prompt, form_for(prompt_name), settings["model"])
            else:
                call = call_claude(client, image, media_type, prompt, settings, structured, form_for(prompt_name))
        except OSError as e:                                  # local model not reachable or timed out
            record.update(status="call failed", problems=f"local model: {e.__class__.__name__}")
            continue
        except anthropic.APIStatusError as e:
            record.update(status="call failed", problems=f"API {e.status_code}: {str(getattr(e, 'message', ''))[:160]}")
            continue
        except anthropic.APIConnectionError:
            record.update(status="call failed", problems="network error")
            continue
        for k in ("seconds", "input_tokens", "output_tokens", "cost_usd"):
            record[k] = round(record[k] + call[k], 5)
        record.update(model_used=call["model_used"], fallback_used=call["fallback_used"], request_id=call["request_id"])
        if call["answer"] is None:
            record.update(status="declined", problems=f"stop reason {call['stop_reason']}")
            break                                             # a decline is recorded, not retried or guessed
        if not structured:                                    # free text can't be checked against the form (prompt v1)
            found = call["answer"]["people_count"] is not None
            record.update(status="free text" if found else "free text, no count", problems="not in the answer form", answer=call["answer"])
            break
        problems = check_answer(call["answer"], form_for(prompt_name))
        if not problems:
            record.update(status="ok", problems="", answer=call["answer"])
            break
        record.update(status="answer rejected", problems="; ".join(problems), answer=call["answer"])
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--effort", default=CLAUDE["effort"], choices=["low", "medium", "high"])
    ap.add_argument("--model", default=CLAUDE["model"], choices=list(PRICES))
    args = ap.parse_args()
    CLAUDE["effort"] = args.effort
    CLAUDE.update(model=args.model, price_in=PRICES[args.model][0], price_out=PRICES[args.model][1])
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    prompt = (PROMPTS / f"{args.prompt}.txt").read_text()
    run = f"{dt.date.today():%Y%m%d}_{CLAUDE['model']}-{CLAUDE['effort']}_{args.prompt}_{args.run}"
    rows = list(csv.DictReader(open(args.images)))
    out_path = RESULTS / "runs" / f"{run}.jsonl"
    log_path = RESULTS / "call_log.csv"
    log_fields = ["run", "time", "file", "model", "effort", "model_used", "prompt_version", "status", "problems", "attempts",
                  "seconds", "input_tokens", "output_tokens", "cost_usd", "fallback_used", "confidence", "request_id"]
    new_log = not log_path.exists()
    with out_path.open("w") as out, log_path.open("a", newline="") as log:
        w = csv.DictWriter(log, fieldnames=log_fields, extrasaction="ignore")
        if new_log:
            w.writeheader()
        for row in rows:
            rec = analyse(client, row, args.prompt, prompt, run, dict(CLAUDE))
            out.write(json.dumps(rec) + "\n")
            w.writerow({**rec, "confidence": (rec.get("answer") or {}).get("confidence", "")})
            a = rec.get("answer") or {}
            print(f"{rec['group'] or rec['file'][:20]:9} {rec['status']:15} people {a.get('people_count', '-'):>3}  "
                  f"{a.get('crowd_level', '-'):16} {a.get('confidence', '-'):6} {rec['seconds']:5.1f}s ${rec['cost_usd']:.4f}")
    total = [json.loads(l) for l in out_path.read_text().splitlines()]
    print(f"\n{run}: {sum(r['status'] == 'ok' for r in total)}/{len(total)} ok, "
          f"${sum(r['cost_usd'] for r in total):.4f} total, {sum(r['seconds'] for r in total):.1f}s total")


if __name__ == "__main__":
    main()
