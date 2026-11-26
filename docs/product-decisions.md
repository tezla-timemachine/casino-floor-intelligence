# Product decisions (Step 18)

**Status:** 15 Nov 2026. One section for each question the brief asks, with the evidence behind it. Every decision is recorded in full (what, why, who) in the decision log, section 3 of `docs/casino-floor-intelligence-03-ai-architecture-and-decision-log.md` (D1–D23); the experiments behind them are in `evals/experiment-log.md`.

---

## 1. Why Claude Opus 5.5 was chosen (D12, D19)

| | Claude Opus 5.5 | Claude Sonnet 5.5 | Moondream (local) |
|---|---|---|---|
| Counts within ±1 or 20% | **88–93%** | 70% | 47% |
| Crowds of 16+ within | **78–89%** | 40% (0% over 50) | 0% |
| Fills the answer form | **100%** | 100% | 0 of 5 |
| Cost per image | $0.023 | $0.008 | free |
| Images leave the computer | yes | yes | no |

**Decision:** Opus 5.5, because the product's value is in **busy scenes**, and only Opus counts them reliably and always produces the structured answer. Sonnet was half the price but undercounted crowds badly. Moondream is free and private, but it broke on crowds and couldn't fill the form. The cost limit was raised from $0.01 to $0.025 per image to allow it (CR-10).

## 2. Why structured output is required (CR-05, CR-09)

- **Free text can't be used:** with the simple prompt (v1), only **6 of 30** answers even stated a number of people, none could be stored or compared, and it cost the most (long essays).
- **The answer form** (9 fields, including a 3×3 grid of counts) makes every answer the **same shape**: it can be checked automatically, stored, compared over time, shown on a dashboard and monitored.
- **The answer is checked before it's used:** a missing field, a grid that doesn't add up, or an impossible count (over 500) is rejected and logged, never guessed (FR-05, CR-15).

## 3. How the crowd categories were defined (D14, D16)

- **Crowd level** comes from the people count by a written rule: **Normal 0–10, Busy 11–30, Highly occupied 31+.** The lines fall in the natural gaps in the 30 hand counts.
- **Congestion** comes from the 3×3 grid: any square with **6–14** people is Moderate congestion; **15+** is High concentration requiring review.
- **Why our rules and not the model's labels:** Claude's own crowd and congestion labels changed between runs (on about 1 image in 6, and 1 in 4).
- **Prototype values:** a real casino would set them **per camera and per area** with the operations team (30 people is busy for a bar, quiet for a hall).
- **Result:** the crowd level matches the level from the hand counts on **93%** of images (pass mark 85%, D18).

## 4. How human review works (D21, Step 14)

1. **A result goes to review** if Claude's confidence is **low**, congestion is **high**, Claude says it **isn't a casino floor**, the answer **failed**, or it's picked in a **random 1-in-10 spot-check**.
2. **The reviewer** sees the image, the full output, the count, crowd status, summary and confidence, and marks it **Correct** or **Incorrect**, with a note.
3. **Decisions are saved** and shown on the Monitoring page. If more than 20% are marked incorrect, an alert fires (D22).
- **Evidence:** low confidence alone caught 5 of the 6 biggest counting misses (Step 13).
- **Found in UAT:** all 10 reviews were marked Correct, most in about 2 seconds with no notes. Review can quietly become **rubber-stamping**. Mitigations are in the risk register (R-10).

## 5. How the heatmap supports operations (D15, D17)

- It shows **where people are**, at a glance: warm where the count is high, uncoloured where a square is empty, with the count printed on each of the 9 squares.
- It turns "40 people" into "**the centre-left tables are where the 40 are**", which tells a supervisor which camera or area to look at.
- **Checked:** Tez compared all 30 heatmaps with their photos side by side, and all matched.
- **A lesson from UAT:** the heatmap shows **how many** people are in a square, not how big they look. In E30, two people close to the camera fill the picture, but the warmest square is the background with 4 smaller people. Correct by the rule, but worth explaining to users.

## 6. What the model should not be trusted to decide

| Not to be trusted with | Why |
|---|---|
| **Staffing or any operational action** | It supports the supervisor; it never decides (D4). It says "may want to review", never "send staff" |
| **Safety** ("unsafe", capacity breaches) | No operational standard is built in; the wording never claims safety (FR-10) |
| **Exact counts in big crowds** | Misses grow with crowd size: 160 against 200 in the largest image (Step 13) |
| **Anything about individuals** | No identities, faces or personal characteristics, by design (Step 20) |
| **Unusual scenes** | Non-casino images (a restaurant, a computer area) go to review |
| **Real utilisation percentages** | Area sizes and capacities aren't known; only shares of people are shown |
| **Its own confidence, alone** | Mostly honest, but one image was off by 3 at "medium" confidence; the random spot-check covers this |

## 7. What's required before use in a real casino

1. **Re-test on real CCTV frames:** fixed, high camera angles and real lighting, with new hand counts. These web photos are not CCTV.
2. **Named zones, capacities and thresholds per camera,** agreed with the operations team.
3. **Approval from privacy, legal, security and operations** for footage access, retention and any online AI service (Step 20). Possibly an on-premises model if footage can't leave the building.
4. **A review process with trained reviewers,** protected against rubber-stamping (R-10).
5. **Cost and speed planning at scale:** see the video design; continuous use needs a local counter as well as Claude.
6. **Operational monitoring and support:** the alert limits (D22) watched by a named owner, with a fallback when the API is unavailable (the out-of-credit failure, DF-06).
7. **User training:** what "prototype" levels mean, how to read the heatmap, and that the system advises, never decides.

## 8. How the system can extend to video

See `docs/video-design.md`. In short: every analysis already accepts a **camera name and a time** (FR-22), so a video frame is just an image with a camera and a time. The design pairs **a cheap local person counter every few seconds** with **Claude on key frames every 5–15 minutes, or when counts jump**. Sending every frame to Claude would cost about **$33 per camera per day**.
