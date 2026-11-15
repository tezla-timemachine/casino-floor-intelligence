# Phase 4 results: operations insights (14 Nov 2026)

Brief Steps 6–10. Claude Opus 5.5, prompt v3.1 (3×3 grid), 30 hand-counted evaluation images, $0.70. Per-image detail: `20261114_grid_per_image.csv` and `20261114_grid_insights.csv`; heatmaps in `heatmaps/` (kept on the project computer and not published, because they show people's faces).

## 1. The rules (all prototype, written down)

| Output | Rule | Decision |
|---|---|---|
| Crowd level | From the people count: Normal 0–10, Busy 11–30, Highly occupied 31+ | D14 |
| Heatmap | Claude's count in each square of a 3×3 grid, smoothed into a warm overlay; each square's count shown | D15, D17 |
| Space use | Each third's and square's share of the people; busiest square; empty squares. No % of capacity | Step 8 |
| Congestion | Any square with 6–14 people = Moderate; 15+ = High concentration requiring review. Never "unsafe" | D16 |
| Summary | Written only from the fields above | FR-12 |

## 2. How they did

| Check | Result |
|---|---|
| Counting (pass marks, D13) | 93% within ±1 or 20% ✓; crowds 16+ 89% ✓; small scenes 100% ✓; **average miss 3.8 ✗** (limit 3; one 200-person image) |
| Crowd level from the model's count matches the level from the hand count | **93%** of images |
| Busiest third matches the hand count's busiest third | **80%** |
| Heatmap matches the photo (Tez, by eye, side by side) | **All 30** |
| Crowd levels given | Normal 18, Busy 7, Highly occupied 5 |
| Congestion given | No visible congestion 19, Moderate congestion 6, High concentration requiring review 5 |
| Answers in the form | 30 of 30 |
| Cost and speed | $0.023 and 9.0 s per image |

## 3. Example summaries

- **E01** (hand count 200): About 160 people are visible; crowd level Highly occupied (prototype). Activity is highest in the middle-centre of the image (22% of the people). High concentration requiring review in the top-centre, top-right, middle-left, middle-centre, middle-right squares; operations staff may want to review these areas. The count is uncertain (low confidence), so these figures are approximate.
- **E05** (hand count 20): About 17 people are visible; crowd level Busy (prototype). Activity is highest in the top-left of the image (35% of the people); 3 of the 9 squares appear empty. Moderate congestion in the top-left square; operations staff may want to review this area.
- **E07** (hand count 0): No people are visible in this image. Crowd level: Normal (prototype). No visible congestion.
- **E15** (hand count 12): About 11 people are visible; crowd level Busy (prototype). Activity is highest in the middle-centre of the image (55% of the people); 5 of the 9 squares appear empty. Moderate congestion in the middle-centre square; operations staff may want to review this area.

## 4. Where the crowd level differed

- **E24:** hand count 32 (Highly occupied), Claude 27 (Busy)
- **E25:** hand count 32 (Highly occupied), Claude 27 (Busy)

## 5. Notes

- The summary names grid squares ("middle-centre"): precise but mechanical. The model's own free-text observations are kept separately and checked for unsupported statements in Phase 5.
- All thresholds are prototype values; a real casino would set them per camera and area with operations.
