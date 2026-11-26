"""Draws the video design diagram for docs/video-design.md.

    .venv/bin/python scripts/video_diagram.py

Writes docs/diagrams/5_video_design.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "docs" / "diagrams"
NAVY, BLUE, PALE, GREY, TOOL = "#1f3b57", "#2e75b6", "#eaf2fb", "#6b7280", "#b26b00"
PURPLE, PALE_PURPLE, GREEN, PALE_GREEN, AMBER, PALE_AMBER = "#6a3fa0", "#f1ebf8", "#2e7d32", "#e8f5e9", "#b26b00", "#fdf3e1"


def box(ax, x, y, w, h, title, sub="", tool="", fill=PALE, edge=BLUE):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fill, ec=edge, lw=1.4))
    lines = [(title, 9.6, NAVY, "bold")] + [(s, 8.0, GREY, "normal") for s in sub.split("\n") if s] + [(t, 8.0, TOOL, "bold") for t in tool.split("\n") if t]
    top = y + h / 2 + 0.2 * (len(lines) - 1) / 2
    for i, (text, size, colour, weight) in enumerate(lines):
        ax.text(x + w / 2, top - i * 0.2, text, ha="center", va="center", fontsize=size, color=colour, weight=weight)


def arrow(ax, a, b, colour=BLUE):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=12, lw=1.3, color=colour))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12.5, 5.6))
    ax.set_xlim(0, 12.5); ax.set_ylim(0, 5.6); ax.axis("off")
    w, h = 2.1, 1.15
    box(ax, 0.2, 2.2, 1.9, h, "Camera feeds", "fixed CCTV,\neach with a name", "frames + time")
    # fast, cheap lane
    ax.text(2.6, 4.75, "Every few seconds, on site, cheap", fontsize=9.5, color=GREEN, weight="bold")
    box(ax, 2.6, 3.4, w, h, "Frame sampler", "e.g. 1 frame every\n5 seconds per camera", fill=PALE_GREEN, edge=GREEN)
    box(ax, 5.0, 3.4, w, h, "Person detector", "counts and positions;\nanonymous tracks", "local model", fill=PALE_GREEN, edge=GREEN)
    box(ax, 7.4, 3.4, w, h, "Counts per zone", "grid squares mapped\nto named floor areas", "time series", fill=PALE_GREEN, edge=GREEN)
    # slow, rich lane
    ax.text(2.6, 0.2, "Every 5–15 minutes, or when counts jump: Claude", fontsize=9.5, color=PURPLE, weight="bold")
    box(ax, 2.6, 0.55, w, h, "Pick key frames", "on a timer, or when the\ndetector sees a change", fill=PALE_PURPLE, edge=PURPLE)
    box(ax, 5.0, 0.55, w, h, "Today's pipeline", "prompt v3.1, answer form,\nrules, review triggers", "Claude Opus 5.5", fill=PALE_PURPLE, edge=PURPLE)
    box(ax, 7.4, 0.55, w, h, "Summaries and flags", "what's happening,\nwhat to review", fill=PALE_PURPLE, edge=PURPLE)
    # outputs
    box(ax, 9.95, 2.0, 2.35, 1.55, "Dashboard over time", "occupancy by hour, busy\nperiods, flow, repeated\ncongestion, before/after", fill=PALE_AMBER, edge=AMBER)
    arrow(ax, (2.1, 2.95), (2.6, 3.95), GREEN); arrow(ax, (2.1, 2.6), (2.6, 1.15), PURPLE)
    for a, b in [(4.7, 5.0), (7.1, 7.4)]:
        arrow(ax, (a, 3.97), (b, 3.97), GREEN); arrow(ax, (a, 1.12), (b, 1.12), PURPLE)
    arrow(ax, (9.5, 3.97), (9.95, 3.1), GREEN); arrow(ax, (9.5, 1.12), (9.95, 2.4), PURPLE)
    arrow(ax, (8.45, 3.4), (3.65, 1.7), GREY)
    ax.text(7.75, 2.55, "a jump in counts\ntriggers a key frame", fontsize=7.8, color=GREY, ha="center")
    ax.text(6.25, 5.4, "Extending to video: a cheap counter all the time, Claude when it matters", ha="center", fontsize=13, color=NAVY, weight="bold")
    ax.text(6.25, 5.1, "Each frame is just an image with a camera name and a time, which today's pipeline already accepts (FR-22).", ha="center", fontsize=8.8, color=GREY)
    fig.savefig(OUT / "5_video_design.png", dpi=170, bbox_inches="tight"); plt.close(fig)
    print("written: 5_video_design.png")


if __name__ == "__main__":
    main()
