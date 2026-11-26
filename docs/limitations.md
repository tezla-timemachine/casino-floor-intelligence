# Limitations (Step 21)

**Status:** 15 Nov 2026. What this prototype can't show, and why. **This is a prototype and a starting point, not a system ready for a casino floor.**

---

## 1. The data

| Limitation | Evidence | What it means |
|---|---|---|
| **Web photos, not casino CCTV** | All 322 images come from a public scene-photo collection (fact sheet) | Fixed, high CCTV angles, real lighting and real crowds may behave differently |
| **Not every casino environment** | 322 images; mostly quiet scenes; some aren't casinos at all (E19, E24) | Results may not hold for other casinos, layouts or events |
| **Images stretched to squares** | Roboflow resized every image to 640×640 | Shapes and positions are slightly distorted |
| **No time, camera or zone** | Not in the dataset | Can't measure change over time, busy periods or named areas |
| **Labels can't be trusted** | 140 labelled people against 699 hand-counted (D3) | Ground truth had to be counted by hand |

## 2. The evaluation

| Limitation | Evidence | What it means |
|---|---|---|
| **Small evaluation set** | 30 images | Shows patterns, not precise rates |
| **One person's counts** | Tez counted all 30; the planned re-count of 5 images hasn't been done yet | Some hand counts are uncertain, especially big crowds (E01 range 180–250; E03 40–75) |
| **Accuracy on unseen images not hand-checked** | The fresh test (D26) ran 20 new images 3 times: consistent (95%) and reliable, but without hand counts | Counting accuracy is proven only on the 30 evaluation images, which also chose the prompt |
| **Summaries judged by one reader** | 30 summaries checked by hand | Another reader might judge borderline cases differently |

## 3. The model

| Limitation | Evidence | What it means |
|---|---|---|
| **Big crowds are undercounted** | E01: 160 against 200; misses grow with crowd size | Large-crowd counts are estimates; low confidence sends them to review |
| **High, wide angles are hardest** | 4 of the 6 biggest misses (Step 13) | Exactly the angle CCTV uses: must be re-tested |
| **Answers vary run to run** | Same count all 3 times on 63% of images | One reading isn't certain; our rules keep levels steady |
| **Cost and speed per image** | $0.023 and 9 s on average; up to $0.040 and 18 s | Fine for a prototype; continuous video needs a cheaper counter (video design) |
| **One online provider** | Anthropic; an outage happened when credit ran out (DF-06) | Needs a fallback in real use |

## 4. The product

| Limitation | What it means |
|---|---|
| **Images only, so no movement over time** | Traffic flow, movement direction and continuous occupancy **need real video**. The design for that exists (Step 16), but it isn't built |
| **Prototype thresholds** | Crowd and congestion levels come from 30 web photos. A real floor needs levels per zone, agreed with operations |
| **No capacities** | "Busy" is a count, not a percentage of an area's capacity |
| **Dashboard runs on one Mac, with no sign-in** | Real use needs hosting inside the casino's network, with access control (privacy note) |
| **Review can become a formality** | Seen in UAT: 10 of 10 marked Correct, mostly in 2 seconds (R-10) |

## 5. What would make it a real system

1. **Real CCTV footage**, with new hand counts and the same evaluation.
2. **Real video,** to measure flow and occupancy over time (Step 16 design).
3. **Zones, capacities and thresholds** agreed with operations.
4. **Privacy, security and legal approval** (Step 20).
5. **A review process** protected against rubber-stamping.

Until then, everything here should be presented as **a tested prototype and a starting point**: it shows that multimodal AI can turn casino images into useful floor information, and exactly where it can't yet be trusted.
