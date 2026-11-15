"""Operations information from one structured answer (Phase 4, brief Steps 6-10).

All rules are written down and labelled prototype:
  crowd level   from the people count: Normal 0-10, Busy 11-30, Highly occupied 31+          (D14, CR-11)
  congestion    from the 3x3 grid: any square 6-14 people = Moderate, 15+ = High              (D16, CR-13)
  space use     each third's and square's share of the people; busiest and quietest square     (Step 8)
  heatmap       the 9 square counts, smoothed and laid over the image                          (D15, Step 7)
  summary       written from the fields above only, so it can't add anything unsupported      (FR-12, Step 10)

Every value carries a tag: "estimated" (from the model), "calculated" (our rule applied to an estimate).
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROWS, COLS = ("top", "middle", "bottom"), ("left", "centre", "right")
CROWD_LINES = [(10, "Normal"), (30, "Busy")]                      # above 30: Highly occupied
MODERATE, HIGH = 6, 15                                            # people in one square
WARM = np.array([[255, 255, 178], [254, 204, 92], [253, 141, 60], [240, 59, 32], [189, 0, 38]], dtype=float)  # yellow to red


def crowd_level(count: int) -> str:
    for limit, name in CROWD_LINES:
        if count <= limit:
            return name
    return "Highly occupied"


def grid(answer: dict) -> np.ndarray:
    g = answer["people_by_grid"]
    return np.array([[g[r][c] for c in COLS] for r in ROWS], dtype=float)


def square_name(r: int, c: int) -> str:
    return f"{ROWS[r]}-{COLS[c]}"


def congestion(g: np.ndarray) -> tuple[str, list[str]]:
    """Status, and the squares that caused it."""
    high = [square_name(r, c) for r in range(3) for c in range(3) if g[r, c] >= HIGH]
    if high:
        return "High concentration requiring review", high
    moderate = [square_name(r, c) for r in range(3) for c in range(3) if g[r, c] >= MODERATE]
    if moderate:
        return "Moderate congestion", moderate
    return "No visible congestion", []


def space_use(g: np.ndarray) -> dict:
    total = g.sum()
    shares = (g / total) if total else np.zeros_like(g)
    busiest = np.unravel_index(np.argmax(g), g.shape)
    quiet = np.argwhere(g == g.min())
    return {"third_shares_pct": {c: round(100 * shares[:, i].sum()) for i, c in enumerate(COLS)},
            "busiest_square": square_name(*busiest) if total else "none",
            "busiest_square_share_pct": round(100 * shares[busiest]) if total else 0,
            "quietest_squares": [square_name(*rc) for rc in quiet],
            "empty_squares": int((g == 0).sum())}


def insights(answer: dict) -> dict:
    g = grid(answer)
    count = int(answer["people_count"])
    status, squares = congestion(g)
    space = space_use(g)
    out = {"people_count": {"value": count, "tag": "estimated"},
           "crowd_level": {"value": crowd_level(count), "tag": "calculated (prototype rule D14)"},
           "congestion": {"value": status, "squares": squares, "tag": "calculated (prototype rule D16)"},
           "space_use": {"value": space, "tag": "calculated from estimated square counts"},
           "confidence": {"value": answer["confidence"], "tag": "estimated (the model's own claim)"},
           "model_crowd_level": answer.get("crowd_level"), "model_congestion": answer.get("congestion")}
    out["summary"] = {"value": summary(count, out, answer), "tag": "written from the fields above only"}
    return out


def summary(count: int, ins: dict, answer: dict) -> str:
    level, (status, squares), space = ins["crowd_level"]["value"], (ins["congestion"]["value"], ins["congestion"]["squares"]), ins["space_use"]["value"]
    if count == 0:
        return "No people are visible in this image. Crowd level: Normal (prototype). No visible congestion."
    s = [f"About {count} {'person is' if count == 1 else 'people are'} visible; crowd level {level} (prototype)."]
    s.append(f"Activity is highest in the {space['busiest_square']} of the image ({space['busiest_square_share_pct']}% of the people); "
             f"{space['empty_squares']} of the 9 squares appear empty." if space["empty_squares"] else
             f"Activity is highest in the {space['busiest_square']} of the image ({space['busiest_square_share_pct']}% of the people).")
    if squares:
        s.append(f"{status} in the {', '.join(squares)} square{'s' if len(squares) > 1 else ''}; operations staff may want to review {'these areas' if len(squares) > 1 else 'this area'}.")
    else:
        s.append("No visible congestion.")
    if answer["confidence"] == "low":
        s.append("The count is uncertain (low confidence), so these figures are approximate.")
    return " ".join(s)


def heatmap(image_path, answer: dict, size: int = 640) -> Image.Image:
    """The image with a warm overlay where people are. Colour is relative to this image's busiest square;
    the number in each square is the model's count."""
    original = Image.open(image_path).convert("RGB")
    width, height = size, max(1, round(size * original.height / original.width))   # keep the photo's shape
    base = original.resize((width, height))
    g = grid(answer)
    peak = g.max()
    if peak > 0:
        small = Image.fromarray((g / peak * 255).astype(np.uint8)).resize((width, height), Image.BICUBIC)
        level = np.clip(np.asarray(small, dtype=float) / 255, 0, 1)
        idx = level * (len(WARM) - 1)
        lo = np.floor(idx).astype(int); hi = np.minimum(lo + 1, len(WARM) - 1); f = (idx - lo)[..., None]
        colour = WARM[lo] * (1 - f) + WARM[hi] * f
        alpha = (0.15 + 0.5 * level)[..., None] * (level[..., None] > 0.03)
        out = np.asarray(base, dtype=float) * (1 - alpha) + colour * alpha
        base = Image.fromarray(out.astype(np.uint8))
    d = ImageDraw.Draw(base)
    try:
        font = ImageFont.truetype("Arial.ttf", 26)
    except OSError:
        font = ImageFont.load_default()
    sx, sy = width // 3, height // 3
    for k in (1, 2):
        d.line([(k * sx, 0), (k * sx, height)], fill=(255, 255, 255), width=1)
        d.line([(0, k * sy), (width, k * sy)], fill=(255, 255, 255), width=1)
    for r in range(3):
        for c in range(3):
            x, y = c * sx + 10, r * sy + 8
            d.rectangle([x - 4, y - 2, x + 46, y + 30], fill=(0, 0, 0))
            d.text((x, y), f"{int(g[r, c])}", fill=(255, 255, 255), font=font)
    return base


# ---- Human review (Decision G, D21) -------------------------------------------------------------
NOT_CASINO = ("not show a casino", "not a casino", "not a standard casino", "rather than a standard casino", "rather than a casino")
SPOT_CHECK_EVERY = 10


def review_reasons(record: dict) -> list[str]:
    """Why a result should go to a person. Empty list = no review needed. `record` is a pipeline record."""
    import hashlib
    reasons = []
    if record.get("status") != "ok":
        return [f"answer {record.get('status', 'missing')}: {record.get('problems', '')}".strip(": ")]
    a = record["answer"]
    if a.get("confidence") == "low":
        reasons.append("low confidence")
    if congestion(grid(a))[0].startswith("High"):
        reasons.append("high concentration")
    if any(p in a.get("operational_summary", "").lower() for p in NOT_CASINO):
        reasons.append("model says it isn't a casino floor")
    if int(hashlib.sha1((record["file"] + record["run"]).encode()).hexdigest(), 16) % SPOT_CHECK_EVERY == 0:
        reasons.append("random spot-check (1 in 10)")
    return reasons
