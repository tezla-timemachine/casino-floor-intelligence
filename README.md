# Casino floor operations intelligence system

Week 5 project: a prototype that uses a multimodal AI model (Claude) to turn casino floor images into operations information: people counts, crowd levels, a heatmap, space use, congestion and a short summary, with human review, a dashboard and model monitoring. **A tested prototype and a starting point, not a system ready for a casino floor.**

**Start here:** [`docs/casino-floor-intelligence-09-product-case-study.md`](docs/casino-floor-intelligence-09-product-case-study.md), then the annotated brief [`docs/week5-brief-what-we-did.docx`](docs/week5-brief-what-we-did.docx), which says what we did under every point of the brief.

## Results in brief

| | |
|---|---|
| Model | Claude Opus 5.5, prompt v3.1, structured answer form with a 3×3 grid |
| Counts within ±1 person or 20% (30 hand-counted images) | 93%; crowds of 16+: 89% |
| Crowd level matches the hand count | 93% |
| Answers in the form | 100% |
| Cost and speed | $0.023 and 9 seconds per image |
| Business UAT | 12 of 12 passed |
| Fresh test, 20 unseen images × 3 runs (no hand counts) | 60 of 60 in the form; 95% consistent; found and fixed a monitoring bug (D26) |
| Known gaps | Average miss 3.8 people (pass mark 3), from one 200-person image. Accuracy on unseen images not yet hand-checked |

## Documents

| Document | What it covers |
|---|---|
| [01 Product / business brief](docs/casino-floor-intelligence-01-product-business-brief.md) | Problem, users, is AI right, assumptions, stakeholders |
| [02 Business requirements](docs/casino-floor-intelligence-02-business-requirements-document.md) | FR-01 to FR-22, AI quality and non-functional requirements |
| [03 Architecture and decision log](docs/casino-floor-intelligence-03-ai-architecture-and-decision-log.md) | Design, components, decisions D1–D25 |
| [04 Project plan](docs/casino-floor-intelligence-04-project-plan.md) and [05 schedule](docs/casino-floor-intelligence-05-project-schedule.csv) | Phases, milestones, Gantt chart |
| [06 Risk register](docs/casino-floor-intelligence-06-risk-register.md) | 16 risks with evidence |
| [07 Evaluation plan](docs/casino-floor-intelligence-07-evaluation-plan.md) | Measures, the evaluation set, pass marks |
| [08 UAT workbook](docs/casino-floor-intelligence-08-user-acceptance-testing.xlsx) | Business and system tests, defects |
| [09 Case study](docs/casino-floor-intelligence-09-product-case-study.md) | The whole story |
| [10 Change control log](docs/casino-floor-intelligence-10-change-control-log.md) | Every change to model, prompt, thresholds and requirements |
| [Dataset fact sheet](docs/week5-dataset.md) | What's in the dataset, and what isn't |
| [Product decisions](docs/week5-product-decisions.md) | The brief's Step 18 questions answered |
| [Video design](docs/week5-video-design.md) | How it extends to video |
| [Privacy and responsible use](docs/week5-privacy-and-responsible-use.md) and [limitations](docs/week5-limitations.md) | Steps 20 and 21 |
| [Experiment log](evals/experiment-log.md) | Every model, prompt and setting tested, with cost and score |
| [Evaluation results](evals/results/) | Phase 3 and 4 summaries, model comparison, error analysis |

Every document has a Word copy alongside it.

## Set up and run

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # then paste your own Anthropic API key after the = sign
.venv/bin/streamlit run dashboard/app.py --server.port 8505
```

- **For a demo with no API cost,** start it in view-only mode. It shows every saved result but never calls Claude and saves nothing (D28):

  ```bash
  VIEW_ONLY=1 .venv/bin/streamlit run dashboard/app.py --server.port 8505
  ```


- **The dataset** isn't in this repository. Download "Casino" version 3 (COCO JSON) from [Roboflow Universe](https://universe.roboflow.com/sva-q5vsp/casino-vavjk/dataset/3) (free account) and unzip it into `data/raw/casino-v3/`. Its fingerprint is in [`data/raw/MANIFEST.md`](data/raw/MANIFEST.md).
- **Main scripts:**
  - `scripts/pipeline.py`: the analysis pipeline;
  - `scripts/insights.py`: operations rules, heatmap, review rules;
  - `scripts/monitoring.py`: monitoring alerts;
  - `scripts/run_eval.py` and `score_eval.py`: the evaluation.
- **Optional local model:** Moondream through [Ollama](https://ollama.com) (`brew install ollama`, then `ollama pull moondream`).

## Layout

| Folder | Contents |
|---|---|
| `scripts/` | Pipeline, rules, evaluation, monitoring, diagrams, document builders |
| `prompts/` | Prompt versions v1, v2, v3, v3.1 (product), trial-1, m-count |
| `dashboard/` | Streamlit dashboard |
| `evals/` | Evaluation set (hand counts), labelling guide and log, experiment log, results |
| `data/results/` | Model answers per run, call log, review decisions |
| `docs/` | Documents (Markdown and Word) and diagrams |

## Data and privacy

Dataset: "Casino" by sva, Roboflow Universe, **CC BY 4.0**. The images are public web photos and some show people's faces, so **the dataset images and uploaded images are not included in this repository**. The system counts people and never identifies them (see the privacy note). The API key lives in `.env`, which is never committed.
