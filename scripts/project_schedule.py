"""The Week 5 task schedule and Gantt chart (project plan, 04 and 05).

    .venv/bin/python scripts/project_schedule.py

Writes docs/casino-floor-intelligence-05-project-schedule.csv and docs/casino-floor-intelligence-05-gantt-chart.png.
Dates after today are a proposal; edit TASKS and re-run.
"""
import csv
import datetime as dt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

DOCS = Path(__file__).resolve().parents[1] / "docs"
TODAY = dt.date(2026, 11, 13)
COLOURS = {"Done": "#2e7d32", "In progress": "#2e75b6", "Planned": "#9fb8d0"}

# (id, phase, task, start, end, status, depends on, brief steps / documents)
TASKS = [
    ("T01", "1 Understand", "Inspect the dataset; fact sheet", "2026-11-13", "2026-11-13", "Done", "", "Step 1"),
    ("T02", "1 Understand", "Use case approved", "2026-11-13", "2026-11-13", "Done", "T01", "Step 2"),
    ("T03", "2 First pipeline", "Choose models; environment; connection test", "2026-11-13", "2026-11-13", "Done", "T02", "Step 3; D5, D6"),
    ("T04", "2 First pipeline", "Brief and requirements (01, 02)", "2026-11-13", "2026-11-13", "Done", "T02", "01, 02"),
    ("T05", "2 First pipeline", "Architecture, plan, Gantt (03, 04, 05)", "2026-11-13", "2026-11-13", "Done", "T04", "03, 04, 05"),
    ("T06", "2 First pipeline", "Evaluation plan, labelling guide, change log (07, 10)", "2026-11-13", "2026-11-13", "Done", "T04", "07, 10"),
    ("T07", "2 First pipeline", "Pipeline v1 with structured output; 5 test images", "2026-11-13", "2026-11-13", "Done", "T05", "Steps 3, 4"),
    ("T08", "3 Measure counting", "Select ~30 evaluation images; hand counts", "2026-11-13", "2026-11-13", "Done", "T06", "Step 5"),
    ("T09", "3 Measure counting", "Counting evaluation; prompts v1-v3 compared", "2026-11-13", "2026-11-14", "Done", "T07 T08", "Steps 5, 12"),
    ("T10", "4 Operations insights", "Crowd levels, heatmap, space use, congestion, summary", "2026-11-14", "2026-11-14", "Done", "T09", "Steps 6-10"),
    ("T11", "5 Compare and learn", "Install Moondream; model comparison", "2026-11-14", "2026-11-14", "Done", "T09", "Step 11"),
    ("T12", "5 Compare and learn", "Error analysis", "2026-11-14", "2026-11-14", "Done", "T09 T11", "Step 13"),
    ("T13", "6 Make it a product", "Human review, dashboard, monitoring", "2026-11-14", "2026-11-14", "Done", "T10 T12", "Steps 14, 15, 17"),
    ("T14", "6 Make it a product", "User acceptance testing (08)", "2026-11-15", "2026-11-15", "Done", "T13", "08"),
    ("T15", "7 Write it up", "Video design, privacy, limitations, risks (06)", "2026-11-21", "2026-11-21", "Planned", "T13", "Steps 16, 19-21; 06"),
    ("T16", "7 Write it up", "Case study (09), README, handover, GitHub", "2026-11-21", "2026-11-22", "Planned", "T14 T15", "Step 22; 09"),
]


def main():
    with (DOCS / "casino-floor-intelligence-05-project-schedule.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "phase", "task", "start", "end", "status", "depends_on", "covers"])
        w.writerows(TASKS)
    fig, ax = plt.subplots(figsize=(12, 6.2))
    for i, (tid, phase, task, start, end, status, *_ ) in enumerate(TASKS):
        s, e = dt.date.fromisoformat(start), dt.date.fromisoformat(end) + dt.timedelta(days=1)
        ax.barh(i, (e - s).days, left=mdates.date2num(s), color=COLOURS[status], height=0.6, edgecolor="white")
        ax.text(mdates.date2num(e) + 0.08, i, task, va="center", fontsize=8.2, color="#1f3b57")
    ax.set_yticks(range(len(TASKS)))
    ax.set_yticklabels([f"{t[0]}  {t[1]}" for t in TASKS], fontsize=8.2)
    ax.invert_yaxis()
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d"))
    ax.set_xlim(mdates.date2num(dt.date(2026, 11, 13)) - 0.2, mdates.date2num(dt.date(2026, 11, 27)))
    ax.axvline(mdates.date2num(TODAY) + 0.5, color="#b26b00", lw=1.2, ls="--")
    ax.text(mdates.date2num(TODAY) + 0.55, -0.9, "today", color="#b26b00", fontsize=8)
    ax.grid(axis="x", alpha=0.25); ax.spines[["top", "right"]].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COLOURS.values()]
    ax.legend(handles, COLOURS.keys(), loc="upper right", frameon=False, fontsize=8.5)
    ax.set_title("Week 5 schedule (dates after today are proposed)", fontsize=12, color="#1f3b57", loc="left")
    fig.tight_layout()
    fig.savefig(DOCS / "casino-floor-intelligence-05-gantt-chart.png", dpi=160); plt.close(fig)
    print("written: schedule CSV and Gantt chart")


if __name__ == "__main__":
    main()
