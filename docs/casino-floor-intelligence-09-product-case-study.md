# Case Study: Casino Floor Operations Intelligence System

**Week 5, 13–15 November 2026.** A prototype that turns casino floor images into operations information, built and evaluated as an AI product, one phase at a time. Tez was Product Owner and Delivery Lead, with Claude building the system and drafting the documents.

---

## 1. Problem

Casinos have CCTV, but nobody can watch every screen. Busy areas get noticed late, quiet areas go unnoticed, judgement varies between supervisors, and nothing is recorded. The question: **can AI look at a floor image first, and point a supervisor's attention to where it's needed?**

## 2. User

The **floor operations supervisor**, who needs to know where to look first and how sure the system is. Also the duty manager, a reviewer, and an operations analyst watching quality and cost.

## 3. AI opportunity

A **multimodal model** (one that reads images) counts people, says where they are, and writes about the floor in one step, with no training. The catch: it always gives an answer, even when it's wrong. So the product had to be **measured before it was trusted**.

## 4. Product decisions

| Decision | Choice | Why |
|---|---|---|
| Model (D12, D19) | Claude Opus 5.5 | Only model accurate on crowds (78–89% within) and always filling the answer form |
| Output (CR-09) | Structured answer form | Free text gave a usable count on 6 of 30 images |
| Truth (D3) | Hand counts, not dataset labels | Labels found 140 people; hand counts found 699 |
| Levels (D14, D16) | Our written rules on the count and grid | The model's own labels changed between runs |
| Review (D21) | 5 triggers incl. low confidence and a 1-in-10 spot-check | Low confidence caught 5 of the 6 biggest misses |
| Cost (CR-10) | Limit raised $0.01 → $0.025 per image | Accuracy on crowds mattered more than the price difference |

All 25 decisions: decision log (03); all 18 experiments: `evals/experiment-log.md`.

## 4b. The decision it supports, and what it's worth

**The decision:** at each check, **where should the supervisor look, or send someone, first?** And which results must a person check before anyone acts on them? The product ranks the floor (busiest areas, congestion flags) and routes uncertain results to review. It never makes the staffing call (D4).

**What it costs to run (measured):** $0.023 and 9 seconds per image.

| Checks per camera | Per camera per day | 50 cameras per day | 50 cameras per year |
|---|---|---|---|
| Every 15 minutes | $2.20 | $110 | about $40,000 |
| Every 5 minutes | $6.60 | $331 | about $121,000 |

**Against the alternative** *(assumption, to confirm with a real casino)*: one extra person watching screens around the clock, at an assumed $30 an hour, costs about $720 a day. A first look at 50 cameras every 15 minutes costs about $110 a day, roughly a sixth. It doesn't replace the supervisor; it tells them where to look.

**The human cost it adds:** on the test images the review rules sent **10 of 30 results** to a person (low confidence 6, high concentration 5, not a casino floor 4, random spot-check 3; some images have more than one reason). That share is high because the test set is rich in crowds; a quiet real floor would flag fewer. Each review needs a real look, not a click (R-10).

**The value on the floor is not proven yet.** What makes it possible is measured: 93% of counts within ±1 or 20%, and every big miss flagged for review. What a pilot on real CCTV must measure:
- **time to notice** a busy area, with and without the product;
- the **share of flags supervisors agree with**;
- **what they did** about them (a table opened, a host sent), and whether queues or idle tables went down.

## 5. Architecture

Image → image check → numbered prompt → model adapter (Claude online, Moondream on the Mac) → answer check → operations rules (crowd level, congestion, space use) → heatmap → review rules → results and logs → dashboard (floor view, history, review queue, monitoring). Only the call to Claude leaves the computer (03, section 1).

## 6. Prototype

- **Pipeline:** structured answers, a 3×3 grid of counts, a sense check, retry and logging.
- **Operations insights:** crowd level, heatmap, space use, congestion, and a summary written only from the fields.
- **Dashboard:** floor view, history, review queue and monitoring with alerts; new images analysed in about 10 seconds for about 2 cents.
- **Video-ready:** every result carries a camera and a time.

## 7. Evaluation

- **30 test images**, chosen before any model saw them, **hand-counted by Tez** with written rules for hard cases.
- **Three prompts, two Claude models, then Moondream;** each image run 3 times for consistency.
- **Pass marks set from the results** (D13, D18) and turned into monitoring alerts.
- **Final:** 93% of counts within ±1 or 20%; 89% on crowds; crowd level right on 93%; heatmaps matched all 30 photos; no unsupported statements or descriptions of people in 30 summaries; **12 of 12 business UAT tests passed**.
- **Fresh test on 20 unseen images** (D26), because the 30 evaluation images also chose the prompt: each run 3 times, no hand counts. 60 of 60 in the form; the 3 counts agreed within the margin on 95%; the crowd level never changed. Accuracy on unseen images is still unproven.

## 8. What failed

- **Free-text prompts:** a usable number on only 6 of 30 images.
- **Sonnet 5.5:** half the cost, but 0% within on crowds over 50 people.
- **Moondream:** couldn't fill the form, and invented counts like 1,439,646,464,646,464.
- **The average-miss pass mark:** 3.8 against 3, caused by one 200-person image.
- **The API ran out of credit:** 30 calls failed.
- **UAT bugs:** uploaded images couldn't be shown, and the heatmap squashed wide photos.
- **Review rubber-stamping:** 10 of 10 reviews marked Correct, most in about 2 seconds.
- **A silent monitoring bug (DF-11),** found by the fresh test: since 15 Nov, results were saved without the model name, so monitoring quietly ignored every new call.

## 9. What changed because of it

| Failure | Change |
|---|---|
| Free text | Answer form required |
| Sonnet's crowd counts | Opus chosen; cost limit raised through change control |
| Impossible counts | Sense check rejects anything over 500 (CR-15) |
| Inconsistent model labels | Our own written rules for crowd level and congestion |
| Credit outage | Failures logged with the reason; monitoring alert on failed requests |
| UAT bugs | Results keep the image path; heatmap keeps the photo's shape |
| Rubber-stamping | Recorded as a High risk (R-10), with fixes proposed |
| Monitoring ignored new calls | Fields restored and logs repaired; next step: alert when no new calls arrive |

## 10. Results

| Measure | Result |
|---|---|
| Counts within ±1 or 20% | **93%** (pass mark 85%) |
| Crowds of 16+ within | **89%** (75%) |
| Crowd level agrees with hand count | **93%** (85%) |
| Average miss | **3.8** people (pass mark 3: **missed**, one image) |
| Answers in the form | **100%** |
| Cost and speed | **$0.023 and 9 s** per image |
| Business UAT | **12 of 12 passed** |
| Consistency on unseen images (fresh test) | **95%** (pass mark 85%) |
| Total API spend | **$6.64** of a $10 budget |

## 11. Next iteration

1. **Re-test on real CCTV frames** from fixed, high cameras.
2. **Count very large crowds in zoomed tiles,** to fix the biggest misses.
3. **Harden human review:** a required note on low-confidence confirmations; track time per review.
4. **Build the video design:** a cheap local counter all the time, Claude on key frames.
5. **Zones, capacities and thresholds** with operations; sign-in and access control.

## What I'd tell another PM

- **Measure before you trust.** The model answered every image confidently; only hand counts showed where it was wrong.
- **Don't trust the dataset's labels either.** Ours missed four in five people.
- **Make the AI fill a form.** Structure turned an essay generator into something you can check, store and monitor.
- **Use the model for what it's good at, and rules for the rest.** Counting by AI, levels by written rules.
- **Pick the model on the hardest case, not the average.** Two models looked the same on quiet scenes; only crowds told them apart.
- **Watch the humans in the loop, too.** Review is a safety net only if people really check.
- **Test on data the project hasn't touched.** The fresh images found a bug that every earlier test had missed.
