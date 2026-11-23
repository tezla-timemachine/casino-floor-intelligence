# Change Control Log: Casino Floor Operations Intelligence System

> **Status:** Started 13 Nov 2026. Every change to something that affects the AI's results, or what's been agreed, is recorded here, with its evidence and who approved it.

---

## 1. What needs change control

| Item | Why it matters | Current version |
|---|---|---|
| **Model** (name and version) | Different models give different answers | Claude Opus 5.5 (`claude-opus-5-5`), the product model; Moondream through Ollama, comparison only (D19) |
| **Prompt** | The wording changes what the model sees and says | **v3.1** (CR-14); v1, v2, v3 kept in `prompts/` |
| **Answer form** (the schema) | Changes what can be stored, shown and compared | Form v2, with the 3×3 grid (CR-12) |
| **Crowd and congestion thresholds** | Change what's flagged | Crowd: 0–10 / 11–30 / 31+ (D14); congestion: 6–14 / 15+ in a square (CR-13) |
| **Review triggers** | Change what reaches a person | Five triggers (CR-16) |
| **Evaluation set and labelling rules** | Change what "correct" means | 30-image evaluation set and labelling guide (D10, CR-07, CR-08); 20-image fresh set (D26) |
| **Requirements** (02) and pass marks (07) | Change what's agreed | BRD v1.2; pass marks set (D13, D18) |
| **Model settings** (effort, maximum length, fallback) | Change quality, cost and speed | Effort medium; fallback on (D6) |

Routine edits that don't change results (typos, layout, refactoring code without changing output) don't need a change request.

---

## 2. How a change is made

1. **Propose:** what changes and why, with evidence (usually an evaluation run).
2. **Assess:** what else it affects: requirements, thresholds, documents, cost.
3. **Approve:** the Product Owner says yes or no.
4. **Apply:** give it a new version (for example prompt v2 → v3), and record it below.
5. **Re-run** the evaluation where results could change, and link the run.

---

## 3. Change register

| CR | Date | Change | Item | Evidence | Approved by | Status |
|---|---|---|---|---|---|---|
| CR-01 | 13 Nov 2026 | Baseline requirements set: BRD v1.0 | Requirements | Review of 01 and 02 | Product Owner (D8) | Done |
| CR-02 | 13 Nov 2026 | Model set: Claude Opus 5.5 at medium effort, with automatic fallback | Model, settings | Connection test: correct count, $0.0062, 3.6 s (D6) | Product Owner (D5, D6) | Done |
| CR-03 | 13 Nov 2026 | Plan and architecture baselined: 03, 04, 05 v1.0 | Plan | Review | Product Owner (D9) | Done |
| CR-04 | 13 Nov 2026 | Evaluation plan v1.0 and labelling guide v1 baselined | Evaluation set and rules | Review | Product Owner (D10) | Done |
| CR-05 | 13 Nov 2026 | Answer form v1 (9 fields, including people per third) and a trial prompt `trial-1` created for pipeline v1. `trial-1` is for testing the pipeline only; prompts v1–v3 for the evaluation come in Phase 3 | Prompt, answer form | Trial run: 5 of 5 answers fit the form, $0.085 (`data/results/runs/trial-1_summary.md`) | Product Owner (approved the run) | Done |
| CR-06 | 13 Nov 2026 | Claude Sonnet 5.5 (`claude-sonnet-5-5`, $2 / $10 per million tokens) trialled against Opus 5.5 on the same 5 images. **No change to the model yet:** pending evidence from the counting evaluation | Model (candidate) | Sonnet $0.0082 per image against Opus $0.0170; same answers on easy images, lower counts on hard ones (`data/results/runs/trial-1_opus-vs-sonnet.md`) | Product Owner (asked for the test); both go into the evaluation (D11) | **Closed:** not adopted (D12) |
| CR-07 | 13 Nov 2026 | Evaluation set: "dark" becomes the 4 darkest test images (brightness 41–50), instead of "brightness under 45"; images tagged dark if under 55 | Evaluation set | Only 1 test image is under 45. Keeping to the test split keeps the set apart from the trial images | Delivery Lead, to confirm with the Product Owner | Done |
| CR-08 | 13 Nov 2026 | Labelling rule: an arm, hand or other body part counts as a person if it clearly belongs to someone not otherwise in the picture. New eval-set field `partial_only`. E12 becomes 1 (arm, left), E29 becomes 3 (hand) | Labelling rules, evaluation set | E12 and E29 notes during hand counting | Product Owner | Done |
| CR-09 | 14 Nov 2026 | **Prompt v3 adopted** for the product. v1 (free text) and v2 (form only) kept for the record but retired | Prompt | Phase 3: v3 had the smallest misses and least lean on both models; v1 counted only 6 of 30 (`evals/results/20261113_phase3_summary.md`) | Product Owner (D12) | Done |
| CR-10 | 14 Nov 2026 | **Cost limit per image raised from $0.01 to $0.025** (BRD 02, section 7, now v1.1). The $10 total API budget is unchanged | Requirements | Opus + v3 costs $0.020 per image; the accurate model is needed for crowds | Product Owner (D12) | Done |
| CR-11 | 14 Nov 2026 | Crowd-level thresholds set (prototype): Normal 0–10, Busy 11–30, Highly occupied 31+ | Thresholds | Spread of the 30 hand counts; the model's own labels were inconsistent | Product Owner (D14) | Done |
| CR-12 | 14 Nov 2026 | Answer form v2: `people_by_third` replaced by `people_by_grid`, a 3×3 grid of counts; prompt v3 → **v3.1** to explain the grid | Answer form, prompt | Needed for the heatmap (D15); thirds become column totals | Product Owner (D15) | Done: re-run 14 Nov, adopted (D17) |
| CR-13 | 14 Nov 2026 | Congestion thresholds set (prototype): any grid square with 6–14 people = Moderate; 15+ = High concentration requiring review | Thresholds | The model's own labels were inconsistent | Product Owner (D16) | Done |
| CR-14 | 14 Nov 2026 | **Product prompt v3 → v3.1** (3×3 grid; otherwise identical) | Prompt | 93% within (v3: 88%), better in crowds; average miss 3.8 misses the ≤3 mark because of one 200-person image (`evals/results/20261114_grid.md`) | Product Owner (D17) | Done |
| CR-15 | 14 Nov 2026 | **Sense check added to the answer check:** a count over 500 people in one image is rejected as implausible, for every model | Answer check | Moondream answered 1,439,646,464,646,464 and similar on 8 crowd images, which the old check accepted (`evals/results/20261114_model_comparison.md`) | Delivery Lead; to confirm with the Product Owner | Done |
| CR-16 | 14 Nov 2026 | Review triggers set: low confidence; high concentration; not a casino floor; failed or rejected answer; random 1 in 10 | Review triggers | Error analysis and a test on the 30 answers (9 of 30 flagged) | Product Owner (D21) | Done |
| CR-17 | 14 Nov 2026 | Monitoring alert limits set (failed 5%, rejected 5%, low confidence 30%, 15 s, $0.025, 20% incorrect reviews, evaluation pass marks) | Alert thresholds | Normal behaviour in the evaluation runs | Product Owner (D22) | Done |
