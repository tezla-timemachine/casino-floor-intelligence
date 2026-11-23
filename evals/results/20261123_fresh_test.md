# Fresh test on 20 unseen images (23 Nov 2026, D26)

**Why:** mentor feedback on Week 4 asked for validation on new data. Every Week 5 result came from the same 30 evaluation images, and the product prompt (v3.1) was chosen by its score on them. These 20 images had never been sent to any model.

**What ran:** the product setting (Claude Opus 5.5, medium effort, prompt v3.1, answer form v2), **3 times on each image**, 60 calls, **$1.45**. Images chosen by `scripts/make_fresh_set.py` (seed 26) in the same mix of groups as the evaluation set: 4 crowded, 3 dark, 3 labelled empty, 5 busy, 5 quiet. Scored by `scripts/score_fresh.py`; per-image detail in `20261123_fresh_per_image.csv`.

**What it can't show:** whether the counts are **accurate**. There are no hand counts for these images (the Product Owner chose the automatic test), so accuracy on unseen images is still unproven. They're also web photos, not CCTV.

---

## 1. Results

| Check | Result | Mark or limit | |
|---|---|---|---|
| Answers in the form | **60 of 60** | 100% | ✓ |
| Rejected answers | **0** | under 5% | ✓ |
| Consistency: the 3 counts agree within ±1 or 20% | **95%** (19 of 20) | at least 85% (D13) | ✓ |
| Consistency: exactly the same count all 3 times | 65% (13 of 20) | reported only (evaluation set, v3: 63%) | |
| Same crowd level in all 3 runs | **20 of 20** | | ✓ |
| Same congestion in all 3 runs | 18 of 20 | | |
| Average response time | **8.9 s** (longest 14.4 s) | under 15 s | ✓ |
| Average cost per image | **$0.0241** (highest $0.036) | under $0.025 | ✓ (just) |
| Low-confidence answers | 32% (19 of 60) | alert over 30% (D22) | **over** |
| Results sent to review | 40% (24 of 60) | | |
| Counts below the dataset's labels | **none** | | ✓ |

**Consistency on prompt v3.1 is now measured** (UAT AQ-04 passed); it was the open gap from Phase 4.

## 2. What it means

- **The product behaves on new images as it did on the test set:** it fills the form every time, gives a steady crowd level, and stays inside the time limit.
- **Crowded images drive low confidence and review.** The 4 crowded images and F11 were low confidence in every run, each counted at 42–119 people: 15 of the 19 low-confidence answers. On these crowd-rich images, monitoring's low-confidence limit (30%) would fire. A real floor with fewer crowds would flag less, but the limit should be watched in a pilot.
- **Cost is close to its limit, and not because of crowds.** 24 of the 60 calls cost more than $0.025, spread across 12 images, quiet ones included: the cost depends on how long the answer is. The average ($0.0241) is just inside the limit; a pilot should check it, or shorten the answer (DF-02).
- **The one image outside the margin is F11** (42, 46 and 58 people), a crowd the dataset labelled as 6. All three runs went to review, which is where it belongs.
- **The labels floor check passed:** no count fell below the dataset's own labels. In the crowded images Claude counted 63 to 119 people where the labels have 12 to 15, the same undercounting by the labels seen in Phase 1 (D3).
- **Two "empty" images were checked:** F08 and F10 were counted as 0 with high confidence; F09 as 2 with low confidence, so it went to review.

## 3. A bug it found (DF-11)

The test found a real defect. Since the video-ready change on 15 Nov (FR-22), a code comment had swallowed two fields: **results were saved without the model name and effort.** Monitoring picks out the product's calls by model name, so it **silently left every new call out of its window**, and still showed the old credit outage as 38% failed requests.

- **Fixed:** the fields are restored in `scripts/pipeline.py`. The 60 affected log rows and records were repaired, since only today's calls were affected.
- **Monitoring now:** 50 latest calls, 0% failed, 28% low confidence (limit 30%), $0.0246 average cost (limit $0.025), 9.1 s. One alert remains: the evaluation's average miss (3.8 against 3, accepted in D17).
- **Lesson:** a monitoring check that filters calls should also alert when it sees no new calls. Added to the handover as a next step.

This is the value of a test on new data: the backtest-style evaluation couldn't have found it, because it was all run before the change.
