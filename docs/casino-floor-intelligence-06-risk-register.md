# Risk Register: Casino Floor Operations Intelligence System

> **Status:** v1.0, approved by the Product Owner, 15 Nov 2026 (D24). R-01 to R-10 are the brief's risks (Step 19), each with what we actually saw; R-11 to R-16 are risks we met in this project.
> **Likelihood** and **impact** are rated High / Medium / Low; **left over** is what remains after the protections in place. Owners are roles (brief 01, section 8).

---

## 1. Summary heat map (left over, after protections)

| | **Low impact** | **Medium impact** | **High impact** |
|---|---|---|---|
| **High likelihood** | | R-13 | R-07, R-10 |
| **Medium likelihood** | R-15, R-16 | R-02, R-05, R-08, R-12, R-14 | R-01, R-03, R-09 |
| **Low likelihood** | R-04, R-11 | R-06 | |

**The ones to watch:** **R-07** (a real casino looks different from these photos), **R-10** (staff trusting it without really checking, which we saw happen in UAT) and **R-09** (privacy of camera footage).

---

## 2. Register

| # | Risk | What we saw in this project | Protection in place | Likelihood | Impact | Left over | Owner |
|---|---|---|---|---|---|---|---|
| **R-01** | The model may **miss people** | Undercounts big crowds: E01 160 against 200; leans low (−2.2 on average) | Low confidence goes to review (it caught 5 of 6 big misses); counting pass marks monitored (D13, D22) | High | High | **Medium** | Delivery Lead |
| **R-02** | It may **count the same person twice**, or count non-people | One overcount: E03 75 against 60; counts vary run to run (spread up to 30 in E01) | Prompt rules (don't count reflections, screens, statues); consistency pass mark; review on low confidence | Medium | Medium | **Medium** | Delivery Lead |
| **R-03** | It may **misunderstand crowded scenes** | Sonnet: 0% within over 50 people; Moondream broke completely. Opus: 78–89% within on crowds | Opus chosen for crowds (D12); high concentration goes to review | High | High | **Medium** | Delivery Lead |
| **R-04** | **Lighting** may affect performance | The 4 darkest images were counted well (average miss 1). E02 was dim with pillars and was undercounted | Dark images in the evaluation set; low confidence flags hard cases | Low | Medium | **Low** | Delivery Lead |
| **R-05** | **Camera angle** may affect performance | Elevated, CCTV-like views were the hardest: 4 of the 6 biggest misses | Evaluation tagged by angle; review triggers. **Must be re-tested on real CCTV** | Medium | High | **Medium** | Delivery Lead |
| **R-06** | It may make **unsupported operational conclusions** | None in 30 summaries; 2 borderline (D20). Our summary is written from the fields only | Prompt v3.1 rules; summary built by rule; never "unsafe" or staffing advice | Low | High | **Low** | Product Owner |
| **R-07** | It may perform **differently in a real casino** | The dataset is web photos, not CCTV; 2 images weren't casinos at all; images stretched to squares | Prototype labels everywhere; limitations stated (Step 21); real deployment needs re-testing (product decisions, section 7) | High | High | **High** | Product Owner |
| **R-08** | It may give **inconsistent answers** for similar images | Same count in all 3 runs on only 63% of images; the model's own crowd labels changed on 1 in 6 | Our written rules decide the levels (D14, D16); consistency pass mark (87%) | Medium | Medium | **Medium** | Delivery Lead |
| **R-09** | **Sensitive camera footage** raises privacy concerns | Faces are clearly visible in many dataset photos; images are sent to an online model | Counts and areas only; no identification or descriptions (checked); approval before any batch is sent; privacy note (Step 20) | Medium | High | **Medium** | Product Owner; privacy and legal (future) |
| **R-10** | Staff may **trust it without reviewing** uncertain results | **Seen in UAT:** 10 of 10 reviews marked Correct, most in about 2 seconds, no notes (DF-08) | Review queue with reasons; monitoring of incorrect reviews. **To add:** require a note on low-confidence confirmations, show the reviewer what to check, track time per review | High | High | **High** | Product Owner; reviewers |
| **R-11** | **The dataset's labels are wrong** | They found 140 people where hand counts found 699; some people labelled as chairs | Hand counts as the true count (D3); labels used only as a cross-check | Low (now) | Low (now) | **Low** | Delivery Lead |
| **R-12** | **The online model is unavailable** | Account ran out of credit: 30 calls failed on 14 Nov (DF-06) | Failures logged with the reason; monitoring alert on failed requests (fired correctly); needs a funded account and a fallback plan in real use | Medium | Medium | **Medium** | Delivery Lead; operations (future) |
| **R-13** | **Cost grows with scale** | $0.023 per image; video at 1 frame a minute would be $33 per camera per day | Cost logged per call; alert at $0.025 average; video design uses a local counter plus Claude on key frames | High | Medium | **Medium** | Product Owner |
| **R-14** | **The model changes** behind the same name | Not seen yet | Model and prompt version on every result; monitoring alerts and the evaluation re-run after any change (change log) | Medium | Medium | **Medium** | Delivery Lead |
| **R-15** | **Prototype levels are taken as official** | Thresholds set from 30 web photos, not a real floor | "Prototype" shown next to every level; real thresholds per zone with operations | Medium | Low | **Low** | Product Owner |
| **R-16** | **Unusual images** (not a casino, posters, mannequins) | E19 (restaurant) and E24 (computer area); E12 mannequin correctly not counted | The model says when it isn't a casino floor, and that sends it to review | Medium | Low | **Low** | Delivery Lead |

---

## 3. Top risks: why they matter

- **R-07, a real casino is different.** Everything here was measured on web photos. Fixed, high CCTV cameras are the hardest angle in our results (R-05). **No real deployment without re-testing on real footage.**
- **R-10, trusting without checking.** The product's safety net is human review. UAT showed how fast a reviewer can click "Correct" without looking. If review becomes a formality, the low-confidence warning stops protecting anyone. **This is the most important process risk.**
- **R-09, privacy.** Casino CCTV shows identifiable people. The product deliberately counts and never identifies, but where footage goes (online model, storage) needs formal approval (Step 20).

---

## 4. Review log

| Date | Change | By |
|---|---|---|
| 15 Nov 2026 | First version: the brief's 10 risks plus 6 of our own, with evidence from Phases 1–6 | Delivery Lead; approved by the Product Owner (D24) |
