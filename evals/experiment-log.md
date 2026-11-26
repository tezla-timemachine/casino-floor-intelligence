# Experiment log: every variant tested

Every model, setting, prompt and answer form we tried, in order, with what it cost, how it scored and what was decided. It plays the role of an MLflow run history. The raw record of every call is `data/results/call_log.csv`; each run's answers are in `data/results/runs/<run>.jsonl`.

**Scores** are against Tez's hand counts on the 30-image evaluation set (D3, D10), unless the images are the 5 trial images. "Within" = misses by no more than 1 person or 20% of the true count.

---

## 1. What was varied

| Dimension | Variants tried | Chosen | Decided in |
|---|---|---|---|
| **Model** | Claude Opus 5.5; Claude Sonnet 5.5; Moondream (local); Sonnet-first escalating to Opus (simulated) | **Claude Opus 5.5** | D12, D19 |
| **Effort** (how long the model thinks) | medium (all runs); low (proposed, not run) | **medium** | CR-02 |
| **Prompt** | trial-1; v1 (simple, free text); v2 (answer form); v3 (form + operational rules); v3.1 (v3 + 3×3 grid); m-count (one-number question, Moondream) | **v3.1** | CR-09, CR-14, D17 |
| **Answer form** | none (v1); form v1 (people per third); form v2 (3×3 grid); count-only (Moondream) | **form v2** | CR-05, CR-12 |
| **Repeats** | 1 run, 3 runs (consistency) | 3 runs for consistency checks | D11 |

---

## 2. Runs, in order

| # | Date | Purpose | Model | Effort | Prompt / form | Images | Calls | Outcome | Key result | Cost |
|---|---|---|---|---|---|---|---|---|---|---|
| X01 | 13 Nov | Connection test | Opus 5.5 | medium | test / count only | 1 trial | 1 | 1 ok | Counted 4 of 4 | $0.006 |
| X02 | 13 Nov | Pipeline v1 trial | Opus 5.5 | medium | trial-1 / form v1 | 5 trial | 5 | 5 ok | Sensible counts; $0.017 per image, over the $0.01 limit | $0.085 |
| X03 | 13 Nov | Cheaper model trial | Sonnet 5.5 | medium | trial-1 / form v1 | 5 trial | 5 | 5 ok | $0.008 per image; lower counts on hard images | $0.041 |
| X04 | 13 Nov | Prompt comparison | Opus 5.5 | medium | v1 / none | 30 eval | 30 | 6 counts, 24 no count | Free text unusable: 6 of 30 gave a number | $0.867 |
| X05 | 13 Nov | Prompt comparison | Opus 5.5 | medium | v2 / form v1 | 30 eval | 30 | 30 ok | 90% within, average miss 3.5 | $0.504 |
| X06 | 13 Nov | Prompt comparison | Opus 5.5 | medium | v3 / form v1 | 30 eval | 30 | 30 ok | 87% within, average miss 2.8, least lean | $0.602 |
| X07 | 13 Nov | Prompt comparison | Sonnet 5.5 | medium | v1 / none | 30 eval | 30 | 6 counts, 24 no count | Free text unusable | $0.263 |
| X08 | 13 Nov | Prompt comparison | Sonnet 5.5 | medium | v2 / form v1 | 30 eval | 30 | 30 ok | 60% within, average miss 10.5 | $0.189 |
| X09 | 13 Nov | Prompt comparison | Sonnet 5.5 | medium | v3 / form v1 | 30 eval | 30 | 30 ok | 73% within; 0% within on crowds over 50 | $0.247 |
| X10–X11 | 13 Nov | Consistency (2 repeats) | Opus 5.5 | medium | v3 / form v1 | 30 eval ×2 | 60 | 60 ok | Over 3 runs: 88% within, average miss 2.6; same count on 63% of images | $1.166 |
| X12–X13 | 13 Nov | Consistency (2 repeats) | Sonnet 5.5 | medium | v3 / form v1 | 30 eval ×2 | 60 | 60 ok | Over 3 runs: 70% within, average miss 8.7, steadily too low in crowds | $0.494 |
| X14 | 13 Nov | Escalation design (simulated on X06, X09–X13) | Sonnet → Opus | medium | v3 / form v1 | 30 eval ×3 | 0 (no new calls) | — | Same accuracy as Opus, only 12% cheaper ($0.0173 against $0.0196) | $0 |
| X15 | 14 Nov | Grid form (first attempt) | Opus 5.5 | medium | v3.1 / form v2 | 30 eval | 30 | **30 failed:** account out of credit | Logged as failed requests; no charge | $0 |
| X16 | 14 Nov | Grid form | Opus 5.5 | medium | v3.1 / form v2 | 30 eval | 30 | 30 ok | 93% within, 89% on crowds; average miss 3.8 (misses the ≤3 mark, one 200-person image); crowd level 93% | $0.700 |
| X17 | 14 Nov | Second model: counting | Moondream | — | m-count / count only | 30 eval | 30 | 22 usable, 8 impossible numbers | 47% within; 0% on crowds | $0 |
| X18 | 14 Nov | Second model: full form | Moondream | — | v3.1 / form v2 | 5 eval | 5 | 0 ok | Can't fill the form; 25–138 s per image | $0 |
| X19 | 23 Nov | Fresh test, automatic (D26) | Opus 5.5 | medium | v3.1 / form v2 | 20 fresh ×3 | 60 | 60 ok | Never seen before; no hand counts. Consistency 95% within the margin, 65% same count; crowd level the same in all 20; 40% of results to review; average $0.0241, 8.9 s. Found DF-11 | $1.449 |

**Totals:** 19 experiments, 466 model calls (including 30 refused for lack of credit; X01 adds 1 call not in the log), **$6.62** of the $10 budget. One more image analysed in UAT brings the project total to **$6.64**.

---

## 3. Variants considered but not run

| Variant | Why not |
|---|---|
| Opus 5.5 at **low effort** (cheaper, less thinking) | Proposed to cut cost; Tez chose to test the cheaper Sonnet model instead |
| Moondream through **Python** (instead of Ollama) | About 4.5 GB; too much for the free disk |
| A separate **person-detection model** for heatmap positions | Over 1 GB to install and a second model to maintain; the 3×3 grid from Claude was enough (D15) |
| **A dot per person** from Claude for the heatmap | Costly and hard to check in crowds (D15) |
| The **dataset's own boxes** as the true count | They miss most people: 140 labelled against 699 hand-counted (D3) |

---

## 4. Safeguards that came out of the experiments

| Found in | Problem | Safeguard |
|---|---|---|
| X04, X07 | Free-text answers can't be stored or compared | Answer form required (CR-09) |
| X06, X10–X13 | The model's own crowd and congestion labels changed between runs | Our written rules decide them (D14, D16) |
| X15 | Calls fail when the account runs out of credit | Failures logged with the API's message (FR-16) |
| X17 | A model can return an impossible count (1,439,646,464,646,464) | Sense check rejects counts over 500 (CR-15) |
