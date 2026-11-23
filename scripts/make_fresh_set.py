"""Choose the fresh test set and make its hand-counting sheets (D26).

    .venv/bin/python scripts/make_fresh_set.py

Why: the 30 evaluation images were also used to choose the prompt (v3 → v3.1), so they no longer give a fully
fair test. These 20 images have never been sent to any model. Rule: from all 322 images, leave out the 30
evaluation images and the 5 trial images, then take the same mix of groups as the evaluation set, scaled to
20: the 4 most crowded by label, the 3 darkest, 3 labelled empty, 5 busy (6-15 labelled) and 5 quiet (1-5),
drawn at random with a fixed seed. The product setting runs on them only after Tez has counted them.

Writes:
  evals/fresh_set.csv                   the set, with blank columns for the hand counts
  evals/fresh_set_dataset_labels.csv    the dataset's own labels, kept apart so they don't sway the counting
  evals/fresh_counting_sheets.pdf       one page per image, as for the evaluation set (not published: faces)
"""
from __future__ import annotations

import csv
import random

import pandas as pd

from make_eval_set import EVALS, RAW, ROOT, sheet

SEED = 26


def choose(d: pd.DataFrame) -> list[tuple[str, str]]:
    used = set(pd.read_csv(EVALS / "eval_set.csv").file) | set(pd.read_csv(ROOT / "data" / "results" / "pipeline_trial_images.csv").file)
    t = d[~d.file.isin(used)].copy()
    rng = random.Random(SEED)
    chosen: list[tuple[str, str]] = []
    taken = set()

    def add(rows, n, group):
        for f in rows:
            if len([c for c in chosen if c[1] == group]) >= n:
                break
            if f not in taken:
                chosen.append((f, group)); taken.add(f)

    add(t.sort_values("person", ascending=False).file, 4, "crowded")
    add(t.sort_values("brightness").file, 3, "dark")
    empty = list(t[t.person == 0].file); rng.shuffle(empty); add(empty, 3, "empty (labelled)")
    busy = list(t[t.person.between(6, 15)].file); rng.shuffle(busy); add(busy, 5, "busy")
    quiet = list(t[t.person.between(1, 5)].file); rng.shuffle(quiet); add(quiet, 5, "quiet")
    return chosen


def main():
    d = pd.read_csv(ROOT / "data" / "inspection" / "per_image.csv")
    chosen = choose(d)
    info = d.set_index("file")
    rows, labels, pages = [], [], []
    for i, (f, group) in enumerate(chosen, 1):
        fid = f"F{i:02d}"
        b, split = info.loc[f, "brightness"], info.loc[f, "split"]
        rows.append({"eval_id": fid, "split": split, "file": f, "chosen_as": group, "brightness": b,
                     "lighting": "dark" if b < 55 else ("bright" if b > 110 else "normal"),
                     "count_best": "", "count_low": "", "count_high": "", "left": "", "centre": "", "right": "",
                     "staff": "", "partial_only": "", "angle": "", "notes": ""})
        labels.append({"eval_id": fid, "labelled_people": int(info.loc[f, "person"])})
        pages.append(sheet(RAW / split / f, fid))
    with (EVALS / "fresh_set.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with (EVALS / "fresh_set_dataset_labels.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(labels[0])); w.writeheader(); w.writerows(labels)
    pages[0].save(EVALS / "fresh_counting_sheets.pdf", save_all=True, append_images=pages[1:], resolution=150)
    print(pd.DataFrame(rows).groupby("chosen_as").size().to_string())
    print(f"{len(rows)} images; splits: {pd.DataFrame(rows).split.value_counts().to_dict()}; "
          f"lighting: {pd.DataFrame(rows).lighting.value_counts().to_dict()}")


if __name__ == "__main__":
    main()
