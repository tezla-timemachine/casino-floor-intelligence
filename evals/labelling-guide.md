# Evaluation Set: Labelling Guide

How to count people by hand on the evaluation images. These counts are the **true count** the models are judged against (D3). The rules exist so that every hard case is decided **the same way every time**.

---

## The set

- About 30 images, listed in `evals/eval_set.csv` with their tags (evaluation plan, 07, section 3).
- Each one has a counting sheet: the image enlarged, with a **3×3 grid** and the parts named left, centre and right. The dataset's own labels are shown separately, **as a cross-check only**: they undercount.

---

## How to label

For each image, record in `evals/eval_set.csv`:

| Column | What to enter |
|---|---|
| `count_best` | Your best count of people visible |
| `count_low`, `count_high` | The lowest and highest plausible counts. The same as best when you're sure |
| `left`, `centre`, `right` | People in each third of the image (for space use and congestion) |
| `staff` | How many of them are clearly staff (dealers, hosts), if you can tell. Otherwise blank |
| `partial_only` | How many of the counted people are **only a body part** (an arm, a hand, part of a head) of someone not otherwise in the picture. Blank if not recorded (CR-08) |
| `angle` | eye-level / elevated / close-up |
| `notes` | Anything hard: hidden people, reflections, crowds |

Lighting (dark, normal, bright) is filled in automatically from the image's measured brightness.

---

## Rules for hard calls (decide once, apply every time)

| Situation | Rule |
|---|---|
| **Partly visible person** (head only, behind a machine, cut off by the edge) | **Count** them, if it's clearly a real person |
| **Only an arm, hand or other body part** | **Count it as a person** if it clearly belongs to someone who isn't otherwise in the picture, and add it to `partial_only`. If several parts could belong to the same person, count the **fewest distinct people**. Don't count it if it could belong to someone already counted (CR-08) |
| **Dealers, hosts, staff** | **Count.** Occupancy includes everyone. Also note them under `staff` |
| **Reflections** in mirrors, glass or shiny surfaces | **Don't count** |
| **People on screens, posters, statues, mannequins** | **Don't count** |
| **Very distant figures** | Count if you can tell it's a person at full zoom. If not, leave them in the range (`count_high`) only |
| **Dense crowd** where people can't be told apart | Count one grid cell carefully, scale it to the crowded cells, and record a range. Write "estimated crowd" in notes |
| **A person across two thirds** | Put them in the third holding most of their body |
| **Unsure** | Give your best guess in `count_best`, put the doubt in the range, and explain in notes |

---

## What counts as an "unsupported statement"

When the model's summaries are checked (07, section 2), a statement is **unsupported** if it:
- claims something not visible in the image (for example "a queue at the bar" when no bar is shown);
- states a cause or intention ("people waiting for a show");
- judges safety or staffing ("unsafe", "needs two more dealers");
- describes an individual (appearance, age, gender, identity).

Plain descriptions of what's visible are fine ("most people are around the left tables").

---

## Bias checks

- **Count before looking at any model's answer** for that image.
- **Don't** use the dataset's labels as a starting count. Look at them only after counting, as a check.
- **Re-count 5 images on a different day.** If the counts differ by more than 10%, tighten the rules above and log why.

---

## Running the evaluation

See the evaluation plan (07), section 5. Every rule change or hard call goes in `evals/labelling-log.md`.
