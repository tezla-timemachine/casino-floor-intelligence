"""Casino floor operations dashboard (brief Steps 14, 15, 17). Runs on this computer only.

    .venv/bin/streamlit run dashboard/app.py --server.port 8505
    VIEW_ONLY=1 .venv/bin/streamlit run dashboard/app.py --server.port 8505    # for demos: no API calls, no changes

Pages: Floor view (one analysed image), History (all images), Review queue (human review), Monitoring.
History starts from the evaluation run with the product setting (Claude Opus 5.5, prompt v3.1) and grows with
each image analysed here. Review decisions are saved to data/results/reviews.csv.
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import insights as ins  # noqa: E402
import monitoring as mon  # noqa: E402
import pipeline as pl  # noqa: E402

RESULTS = ROOT / "data" / "results"
HISTORY, REVIEWS, UPLOADS = RESULTS / "history.jsonl", RESULTS / "reviews.csv", ROOT / "data" / "uploads"
# View-only mode for demos (D28): no calls to the Claude API and no changes to saved results.
VIEW_ONLY = os.environ.get("VIEW_ONLY", "").strip().lower() in {"1", "true", "yes"}
LEVEL_COLOURS = {"Normal": "#2e7d32", "Busy": "#e08a00", "Highly occupied": "#c62828"}

st.set_page_config(page_title="Casino floor operations", page_icon="🎰", layout="wide")


def seed_history() -> None:
    """First run: start the history from the product-setting evaluation run."""
    if HISTORY.exists():
        return
    run = sorted(glob.glob(str(RESULTS / "runs" / "*claude-opus-5-5*_v3.1_grid.jsonl")))[-1]
    HISTORY.write_text("".join(l if l.endswith("\n") else l + "\n" for l in open(run) if json.loads(l)["status"] == "ok"))


@st.cache_data
def load_history(_stamp: float) -> list[dict]:
    return [json.loads(l) for l in open(HISTORY)]


def image_path(r: dict) -> Path:
    return Path(r["path"]) if r.get("path") else pl.RAW / r["split"] / r["file"]


def label(r: dict) -> str:
    return r.get("eval_id") or Path(r.get("path", r["file"])).name


def badge(text: str, colour: str) -> str:
    return f"<span style='background:{colour};color:white;padding:3px 10px;border-radius:10px;font-size:0.85em'>{text}</span>"


seed_history()
history = load_history(HISTORY.stat().st_mtime)
reviews = mon.reviews()

st.sidebar.title("Casino floor operations")
page = st.sidebar.radio("Page", ["Floor view", "History", "Review queue", "Monitoring"])
st.sidebar.caption("Prototype. Crowd and congestion levels are prototype values, not operational standards. "
                   "Supports supervisors' decisions; never makes them. Counts only: no one is identified.")
if VIEW_ONLY:
    st.sidebar.info("**View-only mode.** Saved results only: no calls to Claude, so no API cost, and nothing is changed.")

# ---- Floor view: one image (Step 15) -----------------------------------------------------------
if page == "Floor view":
    if not VIEW_ONLY:
        with st.sidebar.expander("Analyse a new image (sends it to Claude, about $0.02)"):
            up = st.file_uploader("JPEG or PNG", type=["jpg", "jpeg", "png"])
            camera = st.text_input("Camera or area (optional)", placeholder="e.g. CAM-07 poker room")
            when = st.text_input("Captured at (optional)", value=f"{dt.datetime.now():%Y-%m-%d %H:%M}")
            if up and st.button("Analyse"):
                UPLOADS.mkdir(parents=True, exist_ok=True)
                path = UPLOADS / f"{dt.datetime.now():%Y%m%d_%H%M%S}_{up.name}"
                path.write_bytes(up.getvalue())
                import anthropic
                from dotenv import load_dotenv
                load_dotenv(ROOT / ".env")
                settings = {"model": "claude-opus-5-5", "effort": "medium", "price_in": pl.PRICES["claude-opus-5-5"][0], "price_out": pl.PRICES["claude-opus-5-5"][1]}
                with st.spinner("Analysing…"):
                    rec = pl.analyse(anthropic.Anthropic(), {"split": "", "file": path.name, "path": str(path), "camera": camera, "captured_at": when}, "v3.1",
                                     (pl.PROMPTS / "v3.1.txt").read_text(), f"{dt.date.today():%Y%m%d}_dashboard", settings)
                with (RESULTS / "call_log.csv").open("a") as log:
                    import csv
                    csv.DictWriter(log, fieldnames=["run", "time", "file", "model", "effort", "model_used", "prompt_version", "status", "problems", "attempts",
                                                    "seconds", "input_tokens", "output_tokens", "cost_usd", "fallback_used", "confidence", "request_id"],
                                   extrasaction="ignore").writerow({**rec, "confidence": (rec.get("answer") or {}).get("confidence", "")})
                with HISTORY.open("a") as h:
                    h.write(json.dumps(rec) + "\n")
                st.cache_data.clear()
                st.success(f"{rec['status']}: {rec['seconds']} s, ${rec['cost_usd']:.4f}")
                st.rerun()

    names = [label(r) for r in history]
    choice = st.sidebar.selectbox("Image", names, index=len(names) - 1 if names else 0)
    r = history[names.index(choice)]
    st.markdown(f"## {choice}")
    if r["status"] != "ok":
        st.error(f"No result: {r['status']} ({r['problems']}). Sent to review.")
        st.image(str(image_path(r)), width=480)
    else:
        a = r["answer"]; info = ins.insights(a); reasons = ins.review_reasons(r)
        level = info["crowd_level"]["value"]
        st.markdown(badge(level, LEVEL_COLOURS[level]) + " &nbsp; " +
                    badge(info["congestion"]["value"], "#c62828" if info["congestion"]["value"].startswith("High") else "#6b7280") + " &nbsp; " +
                    (badge("Review required: " + "; ".join(reasons), "#b26b00") if reasons else badge("No review needed", "#2e7d32")),
                    unsafe_allow_html=True)
        left, right = st.columns(2)
        left.image(str(image_path(r)), caption="Original image", use_container_width=True)
        right.image(ins.heatmap(image_path(r), a), caption="Heatmap: warm where people are; number = people in each square (estimated)", use_container_width=True)
        m = st.columns(4)
        m[0].metric("People (estimated)", a["people_count"])
        m[1].metric("Crowd level (prototype rule)", level, help="Normal 0–10, Busy 11–30, Highly occupied 31+ (D14)")
        m[2].metric("Confidence (model's own)", a["confidence"])
        m[3].metric("Busiest square", info["space_use"]["value"]["busiest_square"])
        st.markdown(f"**Operational summary** (written from the fields above only): {info['summary']['value']}")
        with st.expander("Space use and the model's own observations"):
            st.write("Share of people per third (calculated from estimates):", info["space_use"]["value"]["third_shares_pct"])
            st.write("Floor objects seen:", ", ".join(a["visible_floor_objects"]))
            st.caption(f"Model's own observations (secondary; its own level words may differ from the rules above): {a['operational_summary']}")
        st.caption(f"Model {r['model']} · prompt {r['prompt_version']} · {r['seconds']} s · ${r['cost_usd']:.4f} · run {r['run']}")

# ---- History (Step 15) ---------------------------------------------------------------------------
elif page == "History":
    st.markdown("## History of analysed images")
    rows = []
    for r in history:
        if r["status"] == "ok":
            a = r["answer"]; info = ins.insights(a)
            rows.append({"image": label(r), "camera": r.get("camera", ""), "captured at": r.get("captured_at", ""), "people (est.)": a["people_count"], "crowd level": info["crowd_level"]["value"],
                         "congestion": info["congestion"]["value"], "confidence": a["confidence"],
                         "review": "; ".join(ins.review_reasons(r)) or "-", "seconds": r["seconds"], "cost $": round(r["cost_usd"], 4)})
        else:
            rows.append({"image": label(r), "camera": r.get("camera", ""), "captured at": r.get("captured_at", ""), "people (est.)": None, "crowd level": "-", "congestion": "-", "confidence": "-",
                         "review": f"answer {r['status']}", "seconds": r["seconds"], "cost $": r["cost_usd"]})
    df = pd.DataFrame(rows)
    c = st.columns(4)
    c[0].metric("Images analysed", len(df))
    c[1].metric("Highly occupied", int((df["crowd level"] == "Highly occupied").sum()))
    c[2].metric("Sent to review", int((df.review != "-").sum()))
    c[3].metric("Average people", round(df["people (est.)"].mean(), 1))
    st.bar_chart(df.set_index("image")["people (est.)"], height=260)
    st.dataframe(df, hide_index=True, use_container_width=True)

# ---- Review queue (Step 14) ----------------------------------------------------------------------
elif page == "Review queue":
    st.markdown("## Review queue")
    st.caption("Results sent for review (D21): low confidence, high concentration, not a casino floor, failed answers, or a random 1-in-10 spot-check.")
    done = set(zip(reviews.run, reviews.file))
    queue = [r for r in history if ins.review_reasons(r) and (r["run"], r["file"]) not in done]
    st.write(f"**{len(queue)}** waiting · **{len(reviews)}** reviewed ({int((reviews.decision == 'correct').sum())} correct, {int((reviews.decision == 'incorrect').sum())} incorrect)")
    if queue:
        r = queue[0]; reasons = ins.review_reasons(r)
        st.markdown(f"### {label(r)} &nbsp; " + badge("; ".join(reasons), "#b26b00"), unsafe_allow_html=True)
        left, right = st.columns([3, 2])
        left.image(str(image_path(r)), caption="Original image", use_container_width=True)
        if r["status"] == "ok":
            a = r["answer"]; info = ins.insights(a)
            right.metric("People (estimated)", a["people_count"])
            right.metric("Crowd status (prototype)", info["crowd_level"]["value"])
            right.metric("Confidence", a["confidence"])
            right.write(f"**Congestion:** {info['congestion']['value']}")
            right.write(f"**Summary:** {info['summary']['value']}")
            with right.expander("Full model output"):
                st.json(a)
        else:
            right.error(f"{r['status']}: {r['problems']}")
        if VIEW_ONLY:
            st.info("View-only mode: a reviewer would mark this result ✓ Correct or ✗ Incorrect here. Decisions aren't saved in this mode.")
            decision = None
        else:
            note = st.text_input("Note (optional), e.g. the count you see")
            b1, b2 = st.columns(2)
            decision = "correct" if b1.button("✓ Correct", use_container_width=True) else ("incorrect" if b2.button("✗ Incorrect", use_container_width=True) else None)
        if decision:
            new = pd.DataFrame([{"time": dt.datetime.now().isoformat(timespec="seconds"), "run": r["run"], "file": r["file"],
                                 "eval_id": r.get("eval_id", ""), "reasons": "; ".join(reasons), "decision": decision, "note": note}])
            pd.concat([reviews, new]).to_csv(REVIEWS, index=False)
            st.rerun()
    if len(reviews):
        st.markdown("#### Decisions so far")
        st.dataframe(reviews.iloc[::-1], hide_index=True, use_container_width=True)

# ---- Monitoring (Step 17) ------------------------------------------------------------------------
else:
    s = mon.status(); m = s["measures"]; ev = s["evaluation"]
    st.markdown("## Model monitoring")
    st.caption(f"Product setting: {m['model']}, prompt {m['prompt_version']}. Last {s['window']} calls of this setting, from the call log.")
    if s["alerts"]:
        st.error("**Needs investigation:**\n\n" + "\n".join(f"- {a}" for a in s["alerts"]))
    else:
        st.success("No alerts.")
    c = st.columns(6)
    c[0].metric("Calls", m["calls"])
    c[1].metric("Failed requests", f"{m['failed_pct']}%", help="Limit 5%")
    c[2].metric("Rejected answers", f"{m['rejected_pct']}%", help="Limit 5%")
    c[3].metric("Low confidence", f"{m['low_conf_pct']}%", help="Limit 30%")
    c[4].metric("Avg response", f"{m['avg_seconds']} s", help="Limit 15 s")
    c[5].metric("Avg cost", f"${m['avg_cost']}", help="Limit $0.025 (BRD v1.1)")
    st.markdown("#### Latest evaluation against the pass marks")
    if ev:
        e = st.columns(5)
        e[0].metric("Within ±1 or 20%", f"{ev['within_pct']}%", help="Pass mark: at least 85%")
        e[1].metric("Average miss", ev["avg_miss"], help="Pass mark: 3 or fewer")
        e[2].metric("Small scenes within", f"{ev['small_within_pct']}%", help="Pass mark: 100%")
        e[3].metric("Crowds within", f"{ev['crowd_within_pct']}%", help="Pass mark: at least 75%")
        e[4].metric("Crowd level agrees", f"{ev['crowd_level_pct']}%", help="Pass mark: at least 85%")
        st.caption(f"From {ev['file']}")
    st.markdown("#### Human review results")
    st.write(f"{m['reviews']} reviewed; {m['incorrect_pct']}% marked incorrect (alert above 20% once 10 or more are reviewed).")
    calls = mon.calls()
    calls = calls[calls.model == m["model"]]
    by_run = calls.groupby("run").agg(prompt=("prompt_version", "first"), calls=("run", "size"),
                                      failed=("status", lambda x: int((x == "call failed").sum())),
                                      avg_seconds=("seconds", "mean"), cost=("cost_usd", "sum")).round(3)
    st.markdown("#### Every run of this model")
    st.dataframe(by_run, use_container_width=True)
