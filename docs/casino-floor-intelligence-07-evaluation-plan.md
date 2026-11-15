# Evaluation Plan: Casino Floor Operations Intelligence System

> **Status:** v1.0, approved 13 Nov 2026 (D10).
> Measures the AI quality requirements in the BRD (02, section 6). Pass marks are set by the Product Owner after the first results (D4), and recorded here and in the change log (10).
> Working files live in `evals/`: the evaluation set, the labelling guide, the labelling log and one results file per run.
> **Every variant tested** (models, effort, prompts, answer forms), with cost, score and decision: `evals/experiment-log.md`.

---

## 1. Why we evaluate

A multimodal model will always give an answer, even when it's wrong. Before anyone relies on it, we need to know **how far to trust each part of its output, and where it breaks.** The brief says it plainly: *"You should not assume that the model is always correct. The output must be evaluated."*

---

## 2. What we measure

| Question | Measure | How | Brief step |
|---|---|---|---|
| Does it count people correctly? | **Average miss in people** (the model's count minus the hand count, ignoring the sign). **Share of images within ±1 person, or within 20% on busy images.** **Lean:** does it count high or low on average? | Model count against hand count, on every evaluation image | 5 |
| Where does counting break? | The same measures **by group:** empty, quiet (1–5), busy (6–15), crowded (16+), dark images, and by camera angle | Group the evaluation images by their tags | 5, 13 |
| Is the crowd level right? | Share of images where the level from the model's count matches the level from the hand count, using the same rule | The written crowd rule applied to both counts | 6 |
| Are busiest and quietest parts right? | Share of images where the model's busiest part matches the part with most people in our hand count by thirds (left, centre, right) | Hand counts by thirds | 8 |
| Does the heatmap match the scene? | Yes / partly / no, judged by eye, with the original image beside it | Visual check on every evaluation image | 7 |
| Is congestion sensible? | Agreement with the congestion level from the hand counts by thirds, plus a check by eye | Written congestion rule | 9 |
| Is it consistent? | Each image run **3 times**: the spread of counts, and whether the crowd level stays the same | Repeated runs | 11 |
| Does it say things that aren't there? | **Unsupported statements per image:** any claim in the summary or observations not visible in the image or not in the fields | Read every summary against its image | 10, 11 |
| Does it describe individuals? | Any mention of appearance, age, gender or identity | Read every answer | 20 |
| Is the format reliable? | Share of answers that fit the form first time, after one retry, or not at all | Automatic check | 4, 11 |
| Is confidence honest? | Average counting miss at each confidence level. Low-confidence answers should miss more | Group by confidence | 14 |
| Speed and cost | Seconds and dollars per image, and in total | Logged on every call | 11, 17 |

---

## 3. The evaluation set

- **Size:** about **30 images**, enough to see patterns while hand counting stays manageable *(assumption, revisited after the first run)*.
- **Chosen before any model results are seen,** so the choice can't favour a model.
- **Chosen to cover the variation found in the dataset** (fact sheet, section 5):

| Group | About how many | Why |
|---|---|---|
| Labelled as empty (0 people) | 4 | Some aren't really empty (fact sheet, section 6) |
| Quiet (1–5 labelled) | 8 | The most common kind of image |
| Busy (6–15 labelled) | 8 | Where counting starts to get hard |
| The most crowded (under-labelled) | 4 | The hardest case, and the one operations cares about most |
| Dark: the 4 darkest test images (brightness 41–50; typical is 81) | 4 | Lighting risk (Step 19). Changed from "under 45", which only one test image meets (CR-07) |
| Close-ups and posed shots | 2 | Unusual angles |

  Groups overlap: an image can be busy and dark. The final list, with each image's tags, is saved in `evals/eval_set.csv`, along with the rule used to pick it.
- **Kept fixed** for every prompt and model, so the comparisons are fair. Changes go through the change log (10).

---

## 4. The true count (ground truth)

- **Counted by a person, not by an AI** (D3). Claude is the model being tested, so an AI can't also be the judge.
- **Who:** Tez, using a counting sheet I prepare. The sheet has each image enlarged with a 3×3 grid drawn on it, and the dataset's labels shown separately as a cross-check.
- **How:** following the rules in `evals/labelling-guide.md`. For example: people cut off by the edge count; reflections and people on screens don't.
- **Busy scenes:** count one grid cell at a time, and record a range (lowest and highest plausible) as well as a best figure.
- **Checking the counting itself:** 5 images are counted a second time on another day. If the two counts differ by more than 10%, the rules are tightened.
- Every hard call and rule change goes in `evals/labelling-log.md`.

---

## 5. How a run works

1. **Name the run:** date, model and prompt version, for example `20261115_claude-opus-5-5_v2`.
2. **Approval:** the Product Owner approves the images and cost before any online run (02, section 8).
3. **Run:** every evaluation image goes through the pipeline. Repeats for consistency are run 3 times.
4. **Score:** a script compares answers with the hand counts and writes `evals/results/<run>.md`, plus a CSV.
5. **Inspect:** the worst images are looked at by eye (Step 13), and failures are written up as expected result, model result, difference, likely reason and possible improvement.
6. **Decide:** any change to the prompt, model or thresholds goes through the change log (10), then everything is re-run.

---

## 6. Pass marks

| Measure | Pass mark | Status |
|---|---|---|
| Counting: average miss | **3 people or fewer** (Opus + v3: 2.6) | **Set (D13)** |
| Counting: small scenes (0–5 people) within ±1 or 20% | **100%** (now 100%) | **Set (D13)** |
| Counting: crowds (16+ people) within ±1 or 20% | **At least 75%** (now 78%) | **Set (D13)** |
| Counting: share within ±1 or 20%, overall | **At least 85%** (now 88%) | **Set (D13)** |
| Crowd-level agreement (our rule on the model's count against our rule on the hand count) | **At least 85%** (Opus + v3.1: 93%) | **Set (D18)** |
| Consistency: the 3 runs of an image agree within ±1 or 20% | **At least 85% of images** (now 87%) | **Set (D13)** |
| Format reliability (after one retry) | 100% | From 02 |
| Unsupported statements | None | From 02 |
| Describing individuals | None | From 02 |
| Cost per image (Claude) | Under $0.01 | From 02 |
| Speed per image | Claude under 10 s; Moondream under 60 s | From 02 |

**How the open marks get set:** after the first run, I'll show you the results by group. You set each mark from what's achievable, and from what a supervisor could live with. A mark that can't be reached is still useful: it tells us what the prototype **can't** be trusted with.

---

## 7. Limits of this evaluation

- **Small set:** about 30 images shows patterns, not precise rates.
- **Web photos, not CCTV:** results won't automatically carry over to real cameras (Step 21).
- **Hand counts have error too,** especially in crowds. That's why we record ranges and a re-count.
- **Judging summaries is subjective.** The rules for what counts as "unsupported" are written in the labelling guide.
