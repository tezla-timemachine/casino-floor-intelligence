# Labelling Log

Every hard call, rule change and re-count during hand labelling, with the date and why. Rules live in `evals/labelling-guide.md`; this log records how they were applied and changed.

---

## What labelling revealed

- **The dataset's labels capture about a fifth of the people:** hand counts total 699 across the 30 images, against 140 labelled. The gap is largest in crowds (E01: 200 counted, 17 labelled) and in some images grouped as "quiet" (E25: 32 counted, 1 labelled).
- **Low and high were reversed** in 9 rows when entered (E15, E17, E20–E22, E24–E26, E30). They were swapped back; the file as entered is kept as `evals/.eval_set_as_entered.csv`.
- **E12 and E29:** body-part cases, settled by the new rule (CR-08).
- **Camera angles** were proposed by Claude from the three definitions (elevated, eye-level, close-up) and confirmed by Tez: 5 elevated, 6 close-up, 19 eye-level (`evals/angle_proposal.jpg`). Angle is a description, not a count.
- **Not every image is a casino floor:** E24 is a computer and print station area, E19 a restaurant. Both kept, as a realistic test of how the model handles other scenes.
- **Candidates for the 5 re-counts** (widest ranges, hardest scenes): E01, E02, E21, E18, E25.

## Rule changes

| Date | Rule | Change | Why |
|---|---|---|---|
| 13 Nov 2026 | All | First version of the labelling guide | Before any counting (D3) |
| 13 Nov 2026 | Body parts | An arm, hand or other part counts as a person if it clearly belongs to someone not otherwise in the picture; new field `partial_only` records how many such people are in each count (CR-08) | Tez's rule, after E12 (an arm and a mannequin) and E29 (a hand) |

## Re-count check

| Image | First count | Second count | Difference | Action |
|---|---|---|---|---|
| *(5 images, Phase 3)* | | | | |
