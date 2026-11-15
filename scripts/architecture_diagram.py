"""Draws the architecture diagram for docs/casino-floor-intelligence-03-ai-architecture-and-decision-log.md.

    .venv/bin/python scripts/architecture_diagram.py

Writes docs/diagrams/3_architecture.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parents[1] / "docs" / "diagrams"
NAVY, BLUE, PALE, GREY, TOOL = "#1f3b57", "#2e75b6", "#eaf2fb", "#6b7280", "#b26b00"
AMBER, PALE_AMBER, GREEN, PALE_GREEN, PURPLE, PALE_PURPLE = "#b26b00", "#fdf3e1", "#2e7d32", "#e8f5e9", "#6a3fa0", "#f1ebf8"


def box(ax, x, y, w, h, title, sub="", tool="", fill=PALE, edge=BLUE):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fill, ec=edge, lw=1.4))
    lines = [(title, 9.4, NAVY, "bold")] + [(s, 7.9, GREY, "normal") for s in sub.split("\n") if s] + \
            [(t, 7.9, TOOL, "bold") for t in tool.split("\n") if t]
    step = 0.2
    top = y + h / 2 + step * (len(lines) - 1) / 2
    for i, (text, size, colour, weight) in enumerate(lines):
        ax.text(x + w / 2, top - i * step, text, ha="center", va="center", fontsize=size, color=colour, weight=weight)


def arrow(ax, a, b, colour=BLUE, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=12, lw=1.3, color=colour, linestyle=ls))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12.5, 7.6))
    ax.set_xlim(0, 12.5); ax.set_ylim(0, 7.6); ax.axis("off")
    # boundary of this computer
    ax.add_patch(Rectangle((0.1, 0.15), 10.0, 6.75, fill=False, ec=GREY, lw=1.2, ls=(0, (5, 4))))
    ax.text(0.25, 6.7, "On this computer", fontsize=9, color=GREY, style="italic")
    ax.text(10.35, 6.7, "Online", fontsize=9, color=PURPLE, style="italic")

    w, h = 1.8, 1.15
    # row 1: the pipeline
    y1 = 4.95
    box(ax, 0.3, y1, w, h, "Image", "dataset now;\nvideo frame later", "data/raw/casino-v3")
    box(ax, 2.35, y1, w, h, "Check image", "opens? right type\nand size? (FR-02)", "Python, Pillow")
    box(ax, 4.4, y1, w, h, "Prompt", "numbered versions\nv1, v2, v3 (FR-18)", "prompts/ folder")
    box(ax, 6.45, y1, w, h, "Model adapter", "same request either\nway; times and costs it", "Python")
    box(ax, 10.45, 5.55, 1.85, 1.0, "Claude Opus 5.5", "main model", "Anthropic API", fill=PALE_PURPLE, edge=PURPLE)
    box(ax, 8.35, 3.65, 1.6, 0.95, "Moondream", "comparison model", "runs locally", fill=PALE_PURPLE, edge=PURPLE)
    for a, b in [(0.3 + w, 2.35), (2.35 + w, 4.4), (4.4 + w, 6.45)]:
        arrow(ax, (a, y1 + h / 2), (b, y1 + h / 2))
    arrow(ax, (6.45 + w, y1 + 0.85), (10.45, 6.05), PURPLE, "<|-|>")
    arrow(ax, (6.45 + w, y1 + 0.25), (8.35 + 0.8, 3.65 + 0.95), PURPLE, "<|-|>")
    ax.text(9.0, 6.25, "image + prompt out,\nanswer back (approved\nbatches only)", fontsize=7.4, color=PURPLE, ha="center")

    # row 2: checking and rules
    y2 = 2.55
    box(ax, 6.45, y2, w, h, "Check the answer", "fixed form filled? retry\nonce, else log (FR-05)", "JSON schema", fill=PALE_GREEN, edge=GREEN)
    box(ax, 4.4, y2, w, h, "Operations rules", "crowd level, congestion,\nspace use (FR-07–10)", "Python, written rules")
    box(ax, 2.35, y2, w, h, "Heatmap", "where people are,\nwarm to cool (FR-09)", "Pillow, numpy")
    box(ax, 0.3, y2, w, h, "Review rules", "low confidence or\nunusual? (FR-13)", "Python", fill=PALE_AMBER, edge=AMBER)
    arrow(ax, (6.45 + w / 2, y1), (6.45 + w / 2, y2 + h))
    for a, b in [(6.45, 4.4 + w), (4.4, 2.35 + w), (2.35, 0.3 + w)]:
        arrow(ax, (a, y2 + h / 2), (b, y2 + h / 2))

    # row 3: storage, dashboard, people
    y3 = 0.4
    box(ax, 0.3, y3, 2.6, 1.3, "Results and logs", "every answer; every call's\nmodel, prompt, time, cost,\nerrors; review decisions (FR-16)", "CSV / JSON files")
    box(ax, 3.35, y3, 2.6, 1.3, "Dashboard", "image, heatmap, count, levels,\nsummary, confidence, review\nqueue, history, monitoring", "Streamlit", )
    box(ax, 6.4, y3 + 0.15, 1.5, 1.0, "People", "supervisor decides;\nreviewer marks", fill=PALE_AMBER, edge=AMBER)
    box(ax, 8.2, y3, 1.75, 1.3, "Evaluation", "hand counts, prompt\nand model comparison", "evals/ folder", fill=PALE_GREEN, edge=GREEN)
    arrow(ax, (0.3 + w / 2, y2), (0.3 + 1.0, y3 + 1.3))
    arrow(ax, (0.3 + 2.6, y3 + 0.65), (3.35, y3 + 0.65))
    arrow(ax, (3.35 + 2.6, y3 + 0.65), (6.4, y3 + 0.65), AMBER, "<|-|>")
    arrow(ax, (8.2 + 0.9, y3 + 1.3), (6.45 + 1.3, y2), GREEN, "<|-", ls="--")

    ax.text(6.25, 7.42, "Architecture: from image to supervisor", ha="center", fontsize=13, color=NAVY, weight="bold")
    ax.text(6.25, 7.12, "Only the call to Claude leaves this computer. Green: checks. Amber: where people come in. Tools in orange.",
            ha="center", fontsize=8.8, color=GREY)
    fig.savefig(OUT / "3_architecture.png", dpi=170, bbox_inches="tight"); plt.close(fig)
    print("written: 3_architecture.png")


if __name__ == "__main__":
    main()
