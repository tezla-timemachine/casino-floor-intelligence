"""Step 1: inspect the Roboflow casino dataset exactly as it is, before building anything.

    python scripts/inspect_dataset.py

Reads data/raw/casino-v3/{train,valid,test}/_annotations.coco.json and the images.
Writes, in data/inspection/:
  per_image.csv     one row per image: split, labels per class, brightness, contrast, duplicate check
  summary.md        the facts, in numbers
  charts and contact sheets (sample images with the labelled boxes drawn on)
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw" / "casino-v3", ROOT / "data" / "inspection"
SPLITS = ["train", "valid", "test"]
COLOURS = {"person": (230, 57, 70), "chair": (46, 134, 222), "table": (39, 174, 96), "slots": (243, 156, 18)}


def load():
    rows, boxes = [], defaultdict(list)
    for split in SPLITS:
        d = json.load(open(RAW / split / "_annotations.coco.json"))
        names = {c["id"]: c["name"] for c in d["categories"]}
        for a in d["annotations"]:
            boxes[(split, a["image_id"])].append((names[a["category_id"]], a["bbox"]))
        for im in d["images"]:
            rows.append({"split": split, "id": im["id"], "file": im["file_name"], "original": im["extra"]["name"],
                         "width": im["width"], "height": im["height"]})
    return rows, boxes


def describe(rows, boxes):
    for r in rows:
        labels = Counter(name for name, _ in boxes[(r["split"], r["id"])])
        for c in COLOURS:
            r[c] = labels.get(c, 0)
        r["other_labels"] = sum(v for k, v in labels.items() if k not in COLOURS)
        people = [b for name, b in boxes[(r["split"], r["id"])] if name == "person"]
        r["person_box_median_px"] = round(float(np.median([w * h for _, _, w, h in people])), 0) if people else ""
        path = RAW / r["split"] / r["file"]
        img = np.asarray(Image.open(path).convert("L"), dtype=float)
        r["brightness"] = round(img.mean(), 1)        # 0 black to 255 white
        r["contrast"] = round(img.std(), 1)
        r["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    seen_original = Counter(r["original"] for r in rows)
    seen_bytes = Counter(r["sha256"] for r in rows)
    for r in rows:
        r["same_original_elsewhere"] = seen_original[r["original"]] - 1
        r["identical_file_elsewhere"] = seen_bytes[r["sha256"]] - 1
    return rows


def draw(r, boxes, size=320):
    img = Image.open(RAW / r["split"] / r["file"]).convert("RGB")
    d = ImageDraw.Draw(img)
    for name, (x, y, w, h) in boxes[(r["split"], r["id"])]:
        d.rectangle([x, y, x + w, y + h], outline=COLOURS.get(name, (128, 128, 128)), width=3)
    img = img.resize((size, size))
    ImageDraw.Draw(img).rectangle([0, 0, size, 22], fill=(0, 0, 0))
    ImageDraw.Draw(img).text((6, 5), f"{r['split']} · people {r['person']} · light {r['brightness']:.0f}", fill=(255, 255, 255),
                             font=ImageFont.load_default())
    return img


def sheet(images, path, cols=4, size=320):
    rows_n = (len(images) + cols - 1) // cols
    out = Image.new("RGB", (cols * size, rows_n * size), "white")
    for i, im in enumerate(images):
        out.paste(im, ((i % cols) * size, (i // cols) * size))
    out.save(path, quality=85)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, boxes = load()
    rows = describe(rows, boxes)
    fields = ["split", "file", "original", "width", "height", "person", "chair", "table", "slots", "other_labels",
              "person_box_median_px", "brightness", "contrast", "sha256", "same_original_elsewhere", "identical_file_elsewhere"]
    with (OUT / "per_image.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)

    people = np.array([r["person"] for r in rows])
    light = np.array([r["brightness"] for r in rows])
    # charts
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
    ax[0].hist(people, bins=range(0, people.max() + 2), color="#2e75b6", edgecolor="white")
    ax[0].set_title("Labelled people per image"); ax[0].set_xlabel("people"); ax[0].set_ylabel("images")
    ax[1].hist(light, bins=20, color="#b26b00", edgecolor="white")
    ax[1].set_title("Image brightness (0 = black, 255 = white)"); ax[1].set_xlabel("average brightness"); ax[1].set_ylabel("images")
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "people_and_brightness.png", dpi=150); plt.close(fig)

    # contact sheets: the most crowded, the empty, the darkest, and a spread across the range
    by_people = sorted(rows, key=lambda r: -r["person"])
    sheet([draw(r, boxes) for r in by_people[:8]], OUT / "sheet_most_people.jpg")
    sheet([draw(r, boxes) for r in [r for r in rows if r["person"] == 0][:8]], OUT / "sheet_no_people.jpg")
    sheet([draw(r, boxes) for r in sorted(rows, key=lambda r: r["brightness"])[:8]], OUT / "sheet_darkest.jpg")
    spread = [sorted(rows, key=lambda r: r["person"])[int(i)] for i in np.linspace(0, len(rows) - 1, 12)]
    sheet([draw(r, boxes) for r in spread], OUT / "sheet_spread.jpg")

    # summary
    total = Counter()
    for r in rows:
        for c in COLOURS:
            total[c] += r[c]
    per_split = {s: sum(1 for r in rows if r["split"] == s) for s in SPLITS}
    lines = ["# Dataset inspection: the numbers", "",
             f"- Images: {len(rows)} ({', '.join(f'{s} {n}' for s, n in per_split.items())}); sizes: {sorted({(r['width'], r['height']) for r in rows})}",
             f"- Labels: " + ", ".join(f"{c} {total[c]:,}" for c in COLOURS) + f"; other {sum(r['other_labels'] for r in rows)}",
             f"- Images with each label: " + ", ".join(f"{c} {sum(1 for r in rows if r[c])}" for c in COLOURS),
             f"- People per image: none in {int((people == 0).sum())}; median {np.median(people):.0f}; "
             f"90th percentile {np.percentile(people, 90):.0f}; most {people.max()}",
             f"- People bands: 0: {int((people == 0).sum())} · 1–5: {int(((people >= 1) & (people <= 5)).sum())} · "
             f"6–15: {int(((people >= 6) & (people <= 15)).sum())} · 16–30: {int(((people >= 16) & (people <= 30)).sum())} · 31+: {int((people > 30).sum())}",
             f"- Brightness: darkest {light.min():.0f}, median {np.median(light):.0f}, brightest {light.max():.0f}",
             f"- Same original photo in more than one file: {sum(1 for r in rows if r['same_original_elsewhere'])} files; "
             f"byte-identical files: {sum(1 for r in rows if r['identical_file_elsewhere'])}",
             f"- Original names starting 'sun_': {sum(1 for r in rows if r['original'].startswith('sun_'))} of {len(rows)}"]
    (OUT / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
