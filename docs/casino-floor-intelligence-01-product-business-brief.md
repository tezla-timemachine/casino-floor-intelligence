# Product / Business Brief: Casino Floor Operations Intelligence System

> **Status:** v1.0, approved by the Product Owner, 13 Nov 2026 (D8). Statements marked *(assumption)* are placeholders, to confirm with a real casino before any deployment.
> **Updated at close, 23 Nov 2026:** statuses and figures brought up to date with the final results, after reviewer feedback on the revenue forecasting project asked for every document to give the same final position (D27).
> Builds on the approved use case (D4) and the dataset fact sheet (`docs/dataset.md`).

---

## 1. Problem

A casino resort has many areas where customers move, gather, wait and play: table games, slot floors, bars, walkways. The operations team has CCTV, but **no one can watch every screen all the time.** As a result *(assumption, typical of large floors)*:

- **Busy areas are noticed late.** A crowded table area or a queue builds up before anyone reacts.
- **Quiet areas go unnoticed.** Underused tables or slot rows aren't spotted, so staff and games aren't moved to where customers are.
- **Judgement varies.** Two supervisors watching the same screen may disagree on whether an area is "busy".
- **There's no record.** Decisions about the floor leave no evidence of what was seen, so they can't be reviewed or improved.

**Problem statement:** floor operations staff can't continuously and consistently see how each area of the casino floor is being used, so their attention and staff don't always go where they're needed.

---

## 2. Target users

| User | Role in the product | Priority |
|---|---|---|
| **Floor operations supervisor** | Looks at each analysed image: how busy, where people are gathered, what's quiet, and whether to look closer | **Primary** |
| Duty manager | Reviews a summary across images and periods: where attention went, and what was flagged | Secondary |
| Reviewer (analyst or supervisor) | Checks results the system wasn't sure about, and marks them right or wrong | Secondary |
| Operations analyst | Watches the system's accuracy, cost and drift (monitoring) | Secondary |

**Primary persona:** a floor supervisor covering a large gaming area during a busy evening. They need to know **where to look first**, and how sure the system is, without watching every camera.

---

## 3. Current process *(assumption)*

1. Supervisors walk the floor, and watch a bank of camera screens when they can.
2. Staff report busy areas by radio.
3. The supervisor decides from what they see and hear: open a table, send a host, move staff.
4. Nothing is recorded about how busy each area was, or why a decision was made.

---

## 4. Is AI the right solution?

| Option | Good | Not so good | Verdict |
|---|---|---|---|
| More people watching screens | Human judgement, no new technology | Expensive, tiring, inconsistent, still can't watch everything | Doesn't scale |
| Footfall sensors or door counters | Accurate counts at entrances | Say nothing about *where* people are on the floor; new hardware | Partial answer |
| **A person-detection model** (a computer-vision model trained to draw boxes around people) | Counts and positions people well once trained | Needs training data and tuning; gives boxes only, no observations or summary | Strong for counting; a possible future addition |
| **A multimodal model** (an AI that reads images and writes about them) | Works without training; counts, describes, summarises and explains in one step; easy to change through the prompt | Accuracy must be proven, especially counting crowds; costs per image if online | **Worth a prototype**, with careful evaluation |

**Conclusion:** a multimodal model is the quickest way to test whether images can be turned into useful operations information, which is what the brief asks for. Its counting must be **measured against hand counts** before anyone relies on it (Decision C, D3). If counting proves weak, a person-detection model is the natural next step.

---

## 5. Proposed AI opportunity

For each casino floor image, the system:

1. sends it to a multimodal model with a fixed set of instructions (the prompt);
2. gets back a **structured answer**, the same fields every time: estimated people, crowd level, busiest and quietest parts, possible congestion, floor objects seen, confidence, summary;
3. turns that into a **heatmap** and prototype **crowd and congestion indicators**;
4. sends unsure or unusual results to a **person to review**;
5. shows everything on a **dashboard**, with a history of past images;
6. logs the model and prompt version, time, cost and outcome of every run (**monitoring**).

**It never decides.** It doesn't set staffing, close areas or judge safety. It points the supervisor's attention (D4).

**Later, with video:** the same steps run on frames over time, adding movement, flow, busy periods and repeated congestion (Step 16).

---

## 6. Business value and success measures

**Value, if proven:**
- **Faster attention:** busy and quiet areas flagged as soon as an image is analysed.
- **Consistency:** the same rules applied to every image.
- **Evidence:** a record of what was seen and flagged, for review.
- **A base for video:** the design extends to continuous monitoring.

**How the prototype is judged.** The targets are set after the first results (D4) and recorded in the BRD (02):

| Measure | What it checks |
|---|---|
| Counting error against hand counts | Can the model be trusted to count? Overall, and for busy and dark images separately |
| Answers in the right format | Can the output be stored and shown reliably? |
| Unsupported statements | Does the model claim things that aren't in the image? |
| Crowd-level agreement | Does the crowd level match the level our rule gives from the hand count? |
| Review routing | Do unsure results reach a person? |
| Cost and speed per image | Is it affordable and quick enough? |

**Value in practice, with the costs:** see the case study (09), section 4b.

**In a real deployment (future, not measured here):** time to notice a busy area, the share of flags supervisors agree with, and staff moves made in response.

---

## 7. Key assumptions to test

| # | Assumption | Who confirms | How | Status |
|---|---|---|---|---|
| A1 | A multimodal model can count people in casino scenes well enough to be useful | Delivery Lead | Hand-count evaluation (Step 5) | **Confirmed for this dataset:** 93% of counts within ±1 or 20% (D17); weaker in big crowds from high angles. A fresh test on 20 unseen images is in D26 |
| A2 | The dataset's photos represent real casino CCTV | Delivery Lead | Inspection | **Known false:** they're web photos (fact sheet). Results must be re-tested on real CCTV |
| A3 | Supervisors want suggestions, not automatic decisions | Product Owner | Use case review | **Confirmed (D4)** |
| A4 | The cost per image is acceptable | Product Owner | Measure every call | **Confirmed:** $0.023 per image with Opus 5.5 and prompt v3.1, within the $0.025 limit (CR-10). Continuous video needs a cheaper local counter (Step 16) |
| A5 | Useful output is possible without identifying anyone | Product Owner | Design and testing | **Confirmed:** no descriptions of individuals in 30 summaries (D20) or in UAT (BU-12) |
| A6 | Sending images to an online model is acceptable | Product Owner; in a real casino, privacy and legal | Approval | Yes for the public dataset. **No** for real footage without approval |
| A7 | Crowd levels can be defined in a useful way without knowing area sizes | Product Owner | Prototype rule plus review | **Partly:** the prototype rule matches the hand-count level on 93% of images (D18); real use needs area capacities and thresholds per zone |

---

## 8. Stakeholders and decision rights

Roles are titles only. In this project, Tez holds the Product Owner and Delivery Lead roles.

| Stakeholder | Interest | Decides |
|---|---|---|
| **Product Owner** (Tez) | A product that helps the floor team | Scope, requirements, model choice, thresholds, approvals |
| **Delivery Lead** (Tez) | Building and evaluating the prototype | How it's built and tested |
| Casino operations manager *(future)* | Better floor visibility | Real crowd and congestion thresholds, per area |
| Surveillance / security team *(future)* | Camera access and footage | Who can see images, and how |
| Privacy, legal and information security *(future)* | Lawful, proportionate use of footage | Whether real footage may be used, retention, and any online AI service |
| Reviewer | Quality | Reviews the work |
