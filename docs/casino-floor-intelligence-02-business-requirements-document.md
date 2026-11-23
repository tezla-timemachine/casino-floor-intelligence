# Business Requirements Document: Casino Floor Operations Intelligence System (prototype)

> **Status:** v1.2, 23 Nov 2026 (targets filled in from D13 and D18; space use by 3×3 grid, CR-12). v1.1, 14 Nov 2026: cost limit changed (CR-10). Baseline v1.0 approved by the Product Owner, 13 Nov 2026 (D8). Changes from here go through the change control log (10).
> Sources: Product brief (01), approved use case (D4), dataset fact sheet (`docs/week5-dataset.md`), the Week 5 brief.
> The targets first marked "set after first results" were set from the Phase 3 and 4 results (D13, D18), in v1.2.

---

## 1. Product objective

Turn casino floor images into operations information that helps a floor supervisor see **how busy each part of the floor is, where people are gathered, what's quiet, and what may need a closer look**, with an honest measure of how far to trust each result.

---

## 2. Prototype scope

**In scope**
- The 322 images of the Roboflow "Casino" dataset (version 3), analysed one at a time.
- Two multimodal models: Claude Opus 5.5 (online) and Moondream (on this Mac) (D5, D6).
- Structured output, the people-count evaluation, crowd levels, heatmap, space use, congestion, management summary.
- Prompt versions and the model comparison, error analysis, human review, the dashboard and monitoring.
- A design for video, written down but not built.

**Out of scope:** see section 9.

---

## 3. User / persona

**Floor operations supervisor** (primary), as in the brief (01, section 2): covers a large gaming area, can't watch every camera, and needs to know where to look first and how sure the system is. Secondary users: duty manager, reviewer, operations analyst.

---

## 4. User journey

1. An image arrives: from the dataset now, from a camera frame later.
2. The system checks it can be read, then sends it to the model with the current prompt.
3. The model's answer is checked against the fixed format, and retried or logged if it doesn't fit.
4. The system works out the crowd level, congestion and heatmap, and decides whether review is needed.
5. The supervisor sees it on the dashboard: image, heatmap, count, crowd level, congestion, summary, confidence and the review flag.
6. **The supervisor decides** what to do, if anything.
7. If flagged, a reviewer opens it, marks it correct or incorrect, and adds a note.
8. Every step is logged for monitoring.

---

## 5. Functional requirements

| ID | Requirement | Brief step | Priority |
|---|---|---|---|
| **FR-01 Load images** | The system shall analyse one image, or a chosen set of images from the dataset folder | 3 | Must |
| **FR-02 Check the image** | Before analysis, the system shall check the file opens as an image and is a supported type and size. It shall not send an unreadable file to the model, and shall log why | 12 | Must |
| **FR-03 Analyse with a multimodal model** | The system shall send the image and the current prompt to the selected model: Claude or Moondream | 3 | Must |
| **FR-04 Structured output** | Every answer shall contain the same fields: estimated people count, crowd level, main occupied area, low-activity area, possible congestion, visible floor objects, confidence, operational summary. Plus the model, prompt version, time and cost | 4 | Must |
| **FR-05 Reject bad answers** | An answer that doesn't fit the format shall be retried once, then recorded as failed. It is never guessed or silently dropped | 4, 17 | Must |
| **FR-06 People count** | The system shall show the model's estimated people count, labelled "estimate" | 3, 5 | Must |
| **FR-07 Crowd level** | The system shall give a prototype crowd level (Normal, Busy, Highly occupied) using a **written rule** with documented thresholds, labelled "prototype" | 6 | Must |
| **FR-08 Space use** | The system shall name the busiest and quietest parts of the image (a 3×3 grid: top, middle, bottom × left, centre, right; CR-12), and show each part's share of the people. It shall not give percentages of capacity | 8 | Must |
| **FR-09 Heatmap** | The system shall show a heatmap over the image: warm where people are concentrated, cool where it's empty, with a legend | 7 | Must |
| **FR-10 Congestion** | The system shall give one of: No visible congestion / Moderate congestion / High concentration requiring review, using a written rule, labelled "prototype". It shall never call an area "unsafe" | 9 | Must |
| **FR-11 Floor objects** | The system shall list the casino floor objects seen (for example tables, slot machines, chairs) | 3, 4 | Should |
| **FR-12 Management summary** | The system shall write a two-to-four sentence summary **from the structured fields only** | 10 | Must |
| **FR-13 Confidence and review flag** | The system shall show the model's confidence, and flag the result for review when a written trigger applies (low confidence, unusual count, or the models disagree), giving the reason | 14 | Must |
| **FR-14 Human review** | A reviewer shall see the image, the output, count, crowd status, summary and confidence, and mark the result correct or incorrect with a note. The decision is saved | 14 | Must |
| **FR-15 Dashboard** | The dashboard shall show the image, people count, crowd status, heatmap, congestion status, summary, confidence and review flag, plus a history of processed images | 15 | Must |
| **FR-16 Monitoring log** | Every run shall record the model version, prompt version, response time, cost, any failure, confidence, review outcome, and whether the answer was later found incorrect or unsupported | 17 | Must |
| **FR-17 Monitoring alerts** | The system shall flag when monitoring shows the model needs investigation, using written rules (for example a rise in failed or rejected answers, or in counting error) | 17 | Must |
| **FR-18 Prompt versions** | The prompt shall exist in at least three numbered versions (simple, strict format, strict format plus operational rules). The version used is recorded with every result | 12 | Must |
| **FR-19 Counting evaluation** | The system shall run a chosen set of images and produce the brief's table (image, actual, model count, difference, result), the average error, and the best and worst images | 5 | Must |
| **FR-20 Model comparison** | The same images and prompt shall run through both models, comparing count accuracy, crowd level, observations, consistency, response time, cost, format reliability and unsupported statements | 11 | Must |
| **FR-21 Measured or estimated** | Every number shown shall be tagged **from the dataset**, **measured** or **estimated** | 1, 8 | Must |
| **FR-22 Video-ready input** | Each analysis shall accept an optional time and camera name, so video frames can be processed later without redesign | 16 | Should |

---

## 6. AI quality requirements

How each is met technically goes in the architecture document (03). Pass marks are recorded in the evaluation plan (07).

| Area | Requirement |
|---|---|
| **Counting accuracy** | The average counting error against hand counts, on a set of about 30 images, **reported separately** for empty, quiet, busy and dark images. Target: **at least 85% of counts within ±1 or 20%; average miss 3 people or fewer; 100% within on 0–5 people; at least 75% within on crowds of 16+** (D13) |
| **Format reliability** | 100% of answers usable after one retry. Failures are logged, never hidden |
| **No unsupported statements** | Summaries and observations say nothing that isn't visible in the image or in the structured fields. Target: **none**, checked by hand on the evaluation set |
| **Consistency** | The same image, run three times, gives a similar count and the same crowd level. Target: **at least 85% of images whose 3 counts all fall within ±1 or 20% of each other** (D13). Reported alongside, not a target: the share giving exactly the same count all 3 times |
| **Crowd-level agreement** | The crowd level from the model's count matches the level our rule gives from the hand count. Target: **at least 85% of images** (D18) [was: set after first results]** |
| **Honest confidence** | Low-confidence answers should be wrong more often than high-confidence ones. If not, confidence alone can't trigger review |
| **Privacy in outputs** | No description of individuals: no appearance, age, gender or identity. Target: **none**, checked by hand |
| **Declines handled** | If the model declines an image, the result is recorded as such, and is never guessed |

---

## 7. Non-functional requirements

| Area | Requirement |
|---|---|
| **Cost** | Claude: under **$0.025 per image** at the chosen settings (Opus 5.5 + prompt v3 measured at $0.020; was $0.01 until CR-10). Whole prototype: under **$10** of API spend |
| **Speed** | Claude: under 10 seconds per image. Moondream: under 60 seconds per image on this Mac *(proposed)* |
| **Where it runs** | Everything on this computer, except calls to Claude (the same principle as Week 4) |
| **Keys and secrets** | The API key stays in a private local file, never in code, chat or GitHub |
| **Reproducible** | Package versions pinned; the dataset version and fingerprint recorded; prompts versioned |
| **Traceable** | Every result traceable to its image, model, prompt version and time |
| **Readable** | Plain-language labels on the dashboard; prototype values marked as prototype |

---

## 8. Data sourcing and ethics

- **Source:** public dataset, CC BY 4.0, crediting its author (sva, Roboflow Universe).
- **People in the images:** faces are visible in many web photos. The system:
  - **does no facial recognition**;
  - **doesn't identify** anyone, or **describe personal characteristics**;
  - keeps only counts and positions.
- **Sending images online:** only dataset images are sent to Anthropic, and only with the Product Owner's approval for each batch. No real casino footage is used.
- **Retention:** results and logs are kept in the project. Images aren't copied anywhere else. The retention rules for real footage are covered in the privacy note (Step 20).
- **Real deployment** would need approval from the casino's privacy, security, legal and operations teams (Step 20).

---

## 9. Out of scope (prototype)

- Video, tracking movement, and live camera feeds (designed for, not built: Step 16).
- Real casino footage.
- Staffing decisions or any automatic action.
- Identifying people, facial recognition, personal characteristics.
- Safety judgements ("unsafe", capacity breaches).
- Training a custom detection model.
- Hosting online.

---

## 10. Open questions

| # | Question | Decided when |
|---|---|---|
| Q1 | What counting error is acceptable? | **Answered (D13):** pass marks in the evaluation plan (07, section 6) |
| Q2 | Crowd-level and congestion thresholds | Phase 4, from the spread of hand counts |
| Q3 | Where does the heatmap's position data come from: the model, a detector, or labels? (Decision E) | Phase 4 |
| Q4 | Exact review triggers (Decision G) | Phase 6 |
| Q5 | Is Moondream accurate enough to be useful at all? | Phase 5 |

---

## 11. Expected business outcomes

- **A tested answer** to whether multimodal AI can turn casino images into trustworthy floor information, and where it can't.
- **A working prototype** a supervisor could try, with human review built in.
- **A design** that extends to video when footage is available.
- **Clear conditions** for real use: accuracy, privacy approvals, thresholds agreed with operations.

---

## 12. Approvals

| What is approved | By | Status |
|---|---|---|
| Requirements (this document) | Product Owner | **Approved, 13 Nov 2026 (D8)** |
| Use of an online AI service with dataset images | Product Owner | Approved for the connection test; each batch approved separately |
| Real footage, thresholds and deployment | Casino privacy, legal, security and operations *(future)* | Not applicable to the prototype |

---

## Appendix A: Changes since baseline

| Version | Date | Change | Change request |
|---|---|---|---|
| v1.2 | 23 Nov 2026 | Targets for counting, consistency and crowd level filled in as set in D13 and D18; space use described by the 3×3 grid | D13, D18, CR-12 (D27) |
| v1.1 | 14 Nov 2026 | Cost limit per image $0.01 → $0.025, after the Phase 3 evaluation chose Opus 5.5 + prompt v3 for its accuracy in crowds | CR-10 (D12) |
