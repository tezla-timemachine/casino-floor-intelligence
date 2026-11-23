# Project Handover: Casino Floor Operations Intelligence System

## 1. What this is
A Week 5 prototype: Claude Opus 5.5 reads casino floor images and returns a structured answer; written rules turn it into crowd level, congestion, space use, a heatmap and a summary; uncertain results go to human review; a dashboard shows it all, with model monitoring. Story: case study (09). Every brief point: `docs/week5-plan.md`.

## 2. Data
- Roboflow "Casino" v3 (322 web photos, CC BY 4.0), in `data/raw/casino-v3/` (not in Git). Fingerprint: `data/raw/MANIFEST.md`.
- Evaluation set: 30 test images hand-counted by Tez, `evals/eval_set.csv`. The dataset's own labels undercount badly; don't use them as truth (D3).

## 3. Status
- All 7 phases done; business UAT 12 of 12 passed (D23).
- Product setting: `claude-opus-5-5`, effort medium, prompt `v3.1`, answer form v2.
- API spend: $6.64 of $10.
- Fresh test on 20 unseen images (D26): consistent and reliable; found and fixed DF-11.

## 4. How it works (short)
`scripts/pipeline.py` (check image → call model → check answer, retry once, log) → `scripts/insights.py` (rules, heatmap, review triggers) → `dashboard/app.py`. Monitoring rules: `scripts/monitoring.py`. Every call: `data/results/call_log.csv`.

## 5. Running it
See README. Dashboard: `.venv/bin/streamlit run dashboard/app.py --server.port 8505`. Analysing a new image sends it to Anthropic (about $0.02).

## 6. Conventions
- Every decision goes in the decision log (03); every change to model, prompt, thresholds or requirements goes in the change log (10), then the evaluation is re-run.
- Images are sent online only with the Product Owner's approval; the API key stays in `.env`.
- Documents: Markdown is the master; Word copies via `scripts/build_word.py`.

## 7. Open issues and to-dos
| Item | Where |
|---|---|
| Re-count 5 evaluation images (E01, E02, E18, E21, E25) on another day | Labelling log |
| Hand-count the 20 fresh images (F01–F20) to check accuracy on unseen images; the model's answers are already saved | `evals/fresh_set.csv`, D26 |
| Monitoring should alert when no new calls arrive (DF-11 went unnoticed because new calls were silently excluded) | `scripts/monitoring.py` |
| Average cost ($0.0241) and low confidence (32% on crowded images) are close to or over their limits | Fresh test, D22 |
| Single images over the cost and speed limits | DF-02, DF-03 |
| Harden review against rubber-stamping | DF-08, R-10 |
| Real CCTV evaluation; zones and thresholds with operations; sign-in | Product decisions, section 7 |
| Remove Ollama and Moondream (about 1.8 GB) when no longer needed: `ollama rm moondream`, `brew uninstall ollama` | — |
