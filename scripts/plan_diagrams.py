"""Draws the two diagrams in docs/plan.md: how the system works, and the build order.

    python scripts/plan_diagrams.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "docs" / "diagrams"
NAVY, BLUE, PALE, GREY, AMBER, PALE_AMBER = "#1f3b57", "#2e75b6", "#eaf2fb", "#6b7280", "#b26b00", "#fdf3e1"


def box(ax, x, y, w, h, title, sub="", fill=PALE, edge=BLUE):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fill, ec=edge, lw=1.4))
    ax.text(x + w / 2, y + h / 2 + (0.13 if sub else 0), title, ha="center", va="center", fontsize=10.5, color=NAVY, weight="bold")
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.2, sub, ha="center", va="center", fontsize=8.3, color=GREY, linespacing=1.3)


def arrow(ax, a, b, colour=BLUE):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=13, lw=1.4, color=colour))


def how_it_works():
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.4); ax.axis("off")
    w, h, y = 2.0, 1.15, 2.6
    steps = [("Casino image", "from the dataset\n(later: video frames)"),
             ("Vision model", "reads the image,\nfollowing our prompt"),
             ("Structured result", "same fields every time:\ncount, crowd level, areas"),
             ("Checks and scores", "crowd level, congestion,\nheatmap, utilisation"),
             ("Dashboard", "what the operations\nsupervisor sees")]
    xs = [0.05 + i * 2.2 for i in range(5)]
    for x, (t, s) in zip(xs, steps):
        box(ax, x, y, w, h, t, s)
    for i in range(4):
        arrow(ax, (xs[i] + w, y + h / 2), (xs[i + 1], y + h / 2))
    # human review branch
    box(ax, xs[3], 0.55, w, 1.05, "Human review", "low confidence or\nunusual result", fill=PALE_AMBER, edge=AMBER)
    arrow(ax, (xs[3] + w / 2, y), (xs[3] + w / 2, 1.6), AMBER)
    arrow(ax, (xs[3] + w, 1.08), (xs[4] + w / 2, y), AMBER)
    ax.text(xs[3] + w / 2 + 0.08, 2.1, "if unsure", fontsize=8, color=AMBER, va="center")
    # monitoring log
    box(ax, xs[0], 0.55, 4.2, 1.05, "Monitoring log", "every run: model and prompt version, time,\ncost, errors, confidence, review outcome", fill="#f3f4f6", edge=GREY)
    ax.plot([xs[1] + w / 2, xs[1] + w / 2], [y, 1.6], color=GREY, lw=1.2, ls=(0, (3, 3)))
    ax.text(5.5, 4.15, "How the system works", ha="center", fontsize=13, color=NAVY, weight="bold")
    ax.text(5.5, 3.88, "The model helps people decide. It never makes the staffing decision itself.", ha="center", fontsize=9, color=GREY)
    fig.savefig(OUT / "1_how_it_works.png", dpi=170, bbox_inches="tight"); plt.close(fig)


def build_order():
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.6); ax.axis("off")
    phases = [("1. Understand", "the dataset and\nthe use case", "Steps 1–2"),
              ("2. First pipeline", "one model, structured\noutput, a few images", "Steps 3–4"),
              ("3. Measure counting", "manual counts against\nthe model; prompt versions", "Steps 5, 12"),
              ("4. Operations insights", "crowd level, heatmap, space\nuse, congestion, summary", "Steps 6–10"),
              ("5. Compare and learn", "second model;\nwhere it goes wrong", "Steps 11, 13"),
              ("6. Make it a product", "human review, dashboard,\nmonitoring", "Steps 14, 15, 17"),
              ("7. Write it up", "video design, decisions, risks,\nprivacy, limits, GitHub", "Steps 16, 18–22")]
    w, h = 2.4, 1.25
    pos = [(0.2 + i * 2.7, 2.7) for i in range(4)] + [(0.2 + 0.2 + i * 2.7 + 1.35, 0.55) for i in range(3)]
    for (x, y), (t, s, steps) in zip(pos, phases):
        box(ax, x, y, w, h, t, s)
        ax.text(x + w / 2, y - 0.17, steps, ha="center", fontsize=8.3, color=BLUE)
    for i in range(3):
        arrow(ax, (pos[i][0] + w, pos[i][1] + h / 2), (pos[i + 1][0], pos[i + 1][1] + h / 2))
    arrow(ax, (pos[3][0] + w / 2, pos[3][1] - 0.3), (pos[4][0] + w / 2 + 0.6, pos[4][1] + h))
    for i in range(4, 6):
        arrow(ax, (pos[i][0] + w, pos[i][1] + h / 2), (pos[i + 1][0], pos[i + 1][1] + h / 2))
    ax.text(5.5, 4.4, "The build order", ha="center", fontsize=13, color=NAVY, weight="bold")
    ax.text(5.5, 4.13, "One phase at a time. Each ends with a short recap and your sign-off.", ha="center", fontsize=9, color=GREY)
    fig.savefig(OUT / "2_build_order.png", dpi=170, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    how_it_works()
    build_order()
    print("written:", *sorted(p.name for p in OUT.glob("*.png")))
