# Step 11: multimodal model comparison (14 Nov 2026)

Same 30 hand-counted evaluation images. Claude Opus 5.5 with the product prompt (v3.1, the full answer form, 3×3 grid). Moondream (small open model, run on this Mac through Ollama) could not fill the full form, so its counting was tested with a simple counting question (one-number answer); the full form was tried on 5 images. Detail: `20261114_model_comparison.csv`, `20261114_moondream_per_image.csv`, `20261114_grid_per_image.csv`.

## The brief's table

| Model | Counting error | Crowd accuracy | Response time | Cost | Notes |
|---|---|---|---|---|---|
| **Claude Opus 5.5** (online) | 93% of counts within ±1 or 20%; average miss 3.8 people; 89% within on crowds of 16+ | Crowd level matches the hand count's on 93% of images | 9.0 s per image | $0.023 per image | Fills the full form every time (30 of 30); honest confidence; the images go to Anthropic |
| **Moondream** (on this Mac) | 47% within; **usable counts on only 22 of 30**; 0% within on crowds of 16+ | Crowd level matches on 60% | 7.5 s for one number; **25–138 s for the full form** | **Free** | **Full form 0 of 5**; on 8 images it answered with impossible numbers (e.g. 1,439,646,464,646,464 people) after getting stuck repeating digits. Images never leave the computer |

## The other measures the brief lists

| Measure | Claude Opus 5.5 | Moondream |
|---|---|---|
| People count accuracy | Good, including crowds | Fine on small scenes (92% within on 0–5 people); fails on crowds |
| Crowd classification | 93% agree (rule D14 on its count) | 60% agree |
| Operational observations | Fills every field: busiest and quietest areas, objects, summary | Couldn't produce them reliably |
| Consistency | 87% of images agree across 3 runs (Phase 3) | Not repeated: temperature 0 gives the same answer each time, so repeats add nothing |
| Response time | 9 s | 7.5 s (count only) to over 2 minutes (full form) |
| Cost | $0.023 per image | Free (runs on this Mac) |
| Structured output reliability | 100% (30 of 30) | 0% on the full form (0 of 5); 73% usable on the one-number form |
| Unsupported statements | Checked by hand in the error analysis (Step 13) | Not applicable: no usable observations |

## Which model suits the product, and why

**Claude Opus 5.5.** The product's value is in busy scenes, and only Claude counts them reliably and fills the answer form every time. Moondream's strengths, free and private, matter, but today it can't do the job: it breaks on crowds and can't produce the structured answer. A private, on-premises option would need a larger local model and stronger hardware, which is a question for a real deployment (Step 20).

## A safeguard found by this test

Moondream's impossible numbers passed the original answer check, because a huge number is still a number. **A sense check now rejects any count over 500 people in one image** (CR-15). It applies to every model.
