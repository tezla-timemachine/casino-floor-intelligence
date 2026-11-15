"""Choose the evaluation set and make the hand-counting sheets (evaluation plan 07, section 3; D10).

    .venv/bin/python scripts/make_eval_set.py

Rule: 30 images from the test split only (the trial images came from train), chosen before any model has
seen them, to cover the groups in 07: the 4 most crowded by label, the 4 darkest (CR-07), 4 labelled empty,
the 2 with the largest people (close-ups), then 8 busy (6-15 labelled) and 8 quiet (1-5), drawn at random
with a fixed seed so the choice can be repeated.

Writes:
  evals/eval_set.csv                    the set, with blank columns for the hand counts
  evals/eval_set_dataset_labels.csv     the dataset's own labels, kept apart so they don't sway the counting
  evals/counting_sheets.pdf             one page per image, enlarged, with a 3x3 grid
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RAW, EVALS = ROOT / "data" / "raw" / "casino-v3", ROOT / "evals"
SEED, SIZE = 5, 1100


def choose(d: pd.DataFrame) -> list[tuple[str, str]]:
    rng = random.Random(SEED)
    t = d[d.split == "test"].copy()
    chosen: list[tuple[str, str]] = []
    taken = set()

    def add(rows, n, group):
        for f in rows:
            if len([c for c in chosen if c[1] == group]) >= n:
                break
            if f not in taken:
                chosen.append((f, group)); taken.add(f)

    add(t.sort_values("person", ascending=False).file, 4, "crowded")
    add(t.sort_values("brightness").file, 4, "dark")   # the 4 darkest test images (CR-07)
    empty = list(t[t.person == 0].file); rng.shuffle(empty); add(empty, 4, "empty (labelled)")
    t["box"] = pd.to_numeric(t.person_box_median_px, errors="coerce")
    add(t.sort_values("box", ascending=False).file, 2, "close-up")
    busy = list(t[t.person.between(6, 15)].file); rng.shuffle(busy); add(busy, 8, "busy")
    quiet = list(t[t.person.between(1, 5)].file); rng.shuffle(quiet); add(quiet, 8, "quiet")
    return chosen


def sheet(path: Path, eval_id: str) -> Image.Image:
    im = Image.open(path).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for k in (1, 2):
        x = y = SIZE * k // 3
        for off, col in ((1, (0, 0, 0)), (0, (255, 255, 255))):
            d.line([(x + off, 0), (x + off, SIZE)], fill=col, width=2)
            d.line([(0, y + off), (SIZE, y + off)], fill=col, width=2)
    page = Image.new("RGB", (SIZE + 80, SIZE + 230), "white")
    page.paste(im, (40, 120))
    p = ImageDraw.Draw(page)
    try:
        big, small = ImageFont.truetype("Arial.ttf", 34), ImageFont.truetype("Arial.ttf", 22)
    except OSError:
        big = small = ImageFont.load_default()
    p.text((40, 30), f"{eval_id}", fill=(31, 59, 87), font=big)
    p.text((160, 40), "Count people by the rules in the labelling guide, before looking at any model answer.", fill=(90, 90, 90), font=small)
    for i, name in enumerate(("LEFT", "CENTRE", "RIGHT")):
        p.text((40 + SIZE * i // 3 + SIZE // 6 - 40, 88), name, fill=(46, 117, 182), font=small)
    p.text((40, SIZE + 135), "best ____   low ____   high ____      left ____   centre ____   right ____      staff ____", fill=(0, 0, 0), font=small)
    p.text((40, SIZE + 170), "angle:  eye-level  /  elevated  /  close-up          notes:", fill=(0, 0, 0), font=small)
    return page


def main():
    d = pd.read_csv(ROOT / "data" / "inspection" / "per_image.csv")
    chosen = choose(d)
    info = d.set_index("file")
    rows, labels, pages = [], [], []
    for i, (f, group) in enumerate(chosen, 1):
        eid = f"E{i:02d}"
        b = info.loc[f, "brightness"]
        rows.append({"eval_id": eid, "split": "test", "file": f, "chosen_as": group, "brightness": b,
                     "lighting": "dark" if b < 55 else ("bright" if b > 110 else "normal"),
                     "count_best": "", "count_low": "", "count_high": "", "left": "", "centre": "", "right": "",
                     "staff": "", "angle": "", "notes": ""})
        labels.append({"eval_id": eid, "labelled_people": int(info.loc[f, "person"])})
        pages.append(sheet(RAW / "test" / f, eid))
    with (EVALS / "eval_set.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with (EVALS / "eval_set_dataset_labels.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(labels[0])); w.writeheader(); w.writerows(labels)
    pages[0].save(EVALS / "counting_sheets.pdf", save_all=True, append_images=pages[1:], resolution=150)
    print(pd.DataFrame(rows).groupby("chosen_as").size().to_string())
    print(f"{len(rows)} images; lighting: {pd.DataFrame(rows).lighting.value_counts().to_dict()}")


if __name__ == "__main__":
    main()
