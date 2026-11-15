"""Build the UAT workbook (document 08), same layout as Week 1: Overview, Business UAT, System & AI tests,
Summary, Defects.

    .venv/bin/python scripts/make_uat.py

Writes docs/casino-floor-intelligence-08-user-acceptance-testing.xlsx. The Summary sheet uses formulas, so it
updates when statuses are changed in Excel. Business UAT rows are for Tez to run on the dashboard (status Pending).
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

OUT = Path(__file__).resolve().parents[1] / "docs" / "casino-floor-intelligence-08-user-acceptance-testing.xlsx"
F, BOLD, HEAD = Font(name="Arial", size=10), Font(name="Arial", size=10, bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F4E79")
WRAP, THIN = Alignment(wrap_text=True, vertical="top"), Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
STATUSES = ["Pass", "Fail", "Partly", "Pending", "Not run"]
DATE, ME = "14 Nov 2026", "Claude (delivery)"

BUSINESS = [  # id, business question, scenario and data, what the tester does, pass criteria, outcome it proves
    ("BU-01", "How many people are present in different areas?", "Floor view, image E04 (a table area)", "Open Floor view, choose E04. Read the people count and the numbers on the heatmap squares",
     "A count labelled 'estimated'; a number in each of the 9 squares; the squares add up to the count", "The supervisor can see how many people are where"),
    ("BU-02", "Which parts of the floor are highly occupied?", "Floor view, image E01 (packed hall)", "Look at the heatmap and the 'Busiest square'",
     "Warm colour sits on the crowd in the photo; busiest square named in plain words", "Busy areas are visible at a glance"),
    ("BU-03", "Which areas appear underused?", "Floor view, image E15 (slot aisle)", "Read the summary and look for cool or empty squares",
     "Empty or quiet parts are shown cool and named in the summary (e.g. '3 of 9 squares appear empty')", "Underused space is visible"),
    ("BU-04", "Where are people gathering?", "Floor view, image E03 (standing crowd)", "Read the summary",
     "Summary names where people are concentrated, matching the photo", "Gathering points are identified"),
    ("BU-05", "Do certain areas appear congested?", "Floor view, images E02 and E09", "Compare the congestion badge on a crowded image (E02) and an empty one (E09)",
     "E02 shows High concentration requiring review with the squares named; E09 shows No visible congestion; the word 'unsafe' never appears", "Congestion is flagged without overstating it"),
    ("BU-06", "How does occupancy change between images?", "History page", "Look at the chart and table of all images",
     "Every analysed image listed with its count, level and congestion; the chart shows the differences", "Images can be compared"),
    ("BU-07", "Which areas may need attention?", "Review queue page", "Open the Review queue; read the reason on the first item",
     "Flagged results show why (e.g. 'low confidence; high concentration'); wording says 'may want to review', never an instruction", "Attention is directed, not decided"),
    ("BU-08", "Does it support, not replace, the supervisor?", "Any 5 images, Floor view", "Read the summaries and badges of 5 images",
     "No staffing instruction or automatic action anywhere; levels marked 'prototype'", "Human decision-making is kept (use case D4)"),
    ("BU-09", "Can a reviewer correct the system?", "Review queue, first 3 items", "Mark each Correct or Incorrect, add a note to one, then open Monitoring",
     "Each decision is saved, appears under 'Decisions so far', and Monitoring shows the review count", "Feedback is captured for improvement"),
    ("BU-10", "Can a new image be analysed end to end?", "Floor view, 'Analyse a new image', any casino photo (about $0.02)", "Upload a photo and press Analyse",
     "Result within about 20 seconds; appears in History; time and cost shown", "The product works on new images, not only the test set"),
    ("BU-11", "Can I tell when the model needs investigating?", "Monitoring page", "Read the alerts and the measures",
     "Alerts are shown in plain words with their limits; today: failed requests and the average-miss pass mark", "Problems are caught early (Step 17)"),
    ("BU-12", "Is privacy respected?", "Any 10 images, Floor view and Review queue", "Read summaries and model observations",
     "No appearance, age, gender, clothing or identity of anyone mentioned", "Occupancy only, no individuals (Step 20)"),
]

SYSTEM = [  # id, type, area, scenario, test data, steps, expected, pass criteria, actual result, status
    ("ST-01", "Functional", "FR-01 Load images", "Analyse a set from the dataset folder", "30 evaluation images", "run_eval.py on the evaluation set", "All 30 analysed", "30 of 30 processed", "30 of 30 (X16)", "Pass"),
    ("ST-02", "Functional", "FR-02 Check image", "Unreadable file and oversized file", "broken.jpg (text), huge.jpg (6 MB)", "check_image on both", "Both rejected before any call", "No call made; reason logged", "Rejected: 'not a readable image'; 'file too large (6,000,000 bytes)'", "Pass"),
    ("ST-03", "Functional", "FR-03 Multimodal model", "Image + prompt to Claude and to Moondream", "30 images", "Run both models", "Both return answers", "Answers returned", "Claude 30 of 30 (X16); Moondream 30 of 30 (X17)", "Pass"),
    ("ST-04", "AI", "FR-04 Structured output", "Every answer fills the fixed form", "30 images, prompt v3.1", "Check every answer against form v2", "All fields present and valid", "100% after one retry", "30 of 30 first time (X16)", "Pass"),
    ("ST-05", "Functional", "FR-05 Reject bad answers", "Answers that don't fit, and impossible counts", "Moondream answers; count 1,439,646,464,646,464", "Run the answer check", "Rejected with a reason; never guessed", "Rejected and logged", "5 of 5 full-form answers rejected (X18); impossible count rejected (CR-15)", "Pass"),
    ("ST-06", "AI", "FR-06 People count", "Count shown, labelled estimate", "Floor view", "Open any image", "Count labelled 'estimated'", "Label present", "'People (estimated)' on every image", "Pass"),
    ("ST-07", "Functional", "FR-07 Crowd level", "Rule 0–10 / 11–30 / 31+", "Counts 10, 11, 30, 31", "insights.crowd_level", "Normal, Busy, Busy, Highly occupied", "All four correct", "Correct for all four boundaries", "Pass"),
    ("ST-08", "Functional", "FR-08 Space use", "Busiest and quietest parts; shares only", "30 images", "Compare busiest third with hand counts", "Busiest third named; no % of capacity", "Matches hand count on most images", "80% match; no capacity % anywhere", "Pass"),
    ("ST-09", "AI", "FR-09 Heatmap", "Heatmap matches the photo", "30 images, side by side", "Tez's visual check", "Warm where people are", "All match", "All 30 match (Tez, D18)", "Pass"),
    ("ST-10", "Functional", "FR-10 Congestion", "Rule: any square 6–14 Moderate, 15+ High; never 'unsafe'", "30 images", "Run the rule; search outputs for 'unsafe'", "3 statuses only; no safety words", "Rule applied; 0 safety words", "19 none, 6 moderate, 5 high; 0 safety words", "Pass"),
    ("ST-11", "AI", "FR-11 Floor objects", "Objects listed", "30 images", "Read visible_floor_objects", "Relevant casino objects", "Present on every answer", "Listed on all 30", "Pass"),
    ("ST-12", "AI", "FR-12 Summary from fields only", "Summary uses only the structured fields", "30 images", "Compare summaries with fields", "Nothing beyond the fields", "No unsupported statement", "Built from fields by rule; 0 unsupported (D20)", "Pass"),
    ("ST-13", "Functional", "FR-13 Confidence and review flag", "Triggers D21", "30 images", "Run review rules", "Flag with reason", "Low-confidence and unusual images flagged", "10 of 30 flagged, reasons shown", "Pass"),
    ("ST-14", "Functional", "FR-14 Human review", "Mark correct or incorrect, saved", "Review queue", "Tez marks items (BU-09)", "Decision saved with note", "Saved to reviews.csv", "10 decisions saved (15 Nov); shown in Monitoring", "Pass"),
    ("ST-15", "Functional", "FR-15 Dashboard", "All 8 items and history", "Dashboard", "Open all 4 pages", "Image, count, status, heatmap, congestion, summary, confidence, review flag, history", "All present, no errors", "All present; no server errors (14 Nov)", "Pass"),
    ("ST-16", "Functional", "FR-16 Monitoring log", "Every call logged", "call_log.csv", "Inspect the log", "Model, prompt, time, cost, status, confidence", "Every call present", "406 calls logged (to 15 Nov), including 30 failures with the API's message", "Pass"),
    ("ST-17", "Functional", "FR-17 Monitoring alerts", "Alerts against D22 limits", "Last 50 calls", "Open Monitoring", "Alerts fire when limits are passed", "Real problems flagged", "2 alerts: failed requests 40% (credit outage); average miss 3.8", "Pass"),
    ("ST-18", "Functional", "FR-18 Prompt versions", "Numbered prompts recorded with every result", "prompts/ folder", "Inspect results", "v1–v3.1 kept; version on every record", "Present", "v1, v2, v3, v3.1 (+ trial-1, m-count); version on every record", "Pass"),
    ("ST-19", "Functional", "FR-19 Counting evaluation", "The brief's counting table", "30 images", "score_eval.py", "Actual, model, difference, result; average error", "Table produced", "Phase 3 summary, section 5", "Pass"),
    ("ST-20", "Functional", "FR-20 Model comparison", "Two models on the same images", "30 images", "Compare Claude and Moondream", "Comparison table", "Produced", "Model comparison (Step 11)", "Pass"),
    ("ST-21", "Functional", "FR-21 Measured or estimated", "Every value tagged", "Dashboard and insights", "Inspect labels", "Tags shown", "All values tagged", "Estimated, calculated or prototype on every value", "Pass"),
    ("ST-22", "Functional", "FR-22 Video-ready input", "Optional time and camera name per analysis", "CAM-07, 2026-11-15 21:30", "analyse() with camera and time", "Accepted and stored", "Fields stored", "Both stored on the result (15 Nov); dashboard upload asks for them", "Pass"),
    ("AQ-01", "AI", "Counting accuracy (pass marks D13)", "Hand counts", "30 images, v3.1", "score_eval.py", "Within ≥85%; average miss ≤3; small 100%; crowds ≥75%", "All four marks", "93%; 3.8 ✗; 100%; 89%: average miss fails because of E01 (DF-01)", "Fail"),
    ("AQ-02", "AI", "Format reliability", "All answers usable", "30 images", "Check statuses", "100% after one retry", "100%", "30 of 30", "Pass"),
    ("AQ-03", "AI", "No unsupported statements", "Read every summary", "30 summaries", "Hand check", "None", "None", "None; 2 borderline accepted (D20)", "Pass"),
    ("AQ-04", "AI", "Consistency (pass mark ≥85%)", "Same image 3 times", "30 images × 3", "Repeat runs", "≥85% of images agree", "≥85%", "87% on prompt v3; v3.1 not yet repeated", "Partly"),
    ("AQ-05", "AI", "Crowd-level agreement (pass mark ≥85%)", "Rule on model count against hand count", "30 images", "score_eval.py", "≥85%", "≥85%", "93%", "Pass"),
    ("AQ-06", "AI", "Honest confidence", "Low confidence misses more", "90 answers", "Group by confidence", "Low > medium > high error", "Order holds", "High: 0 misses; low: all the big misses", "Pass"),
    ("AQ-07", "AI", "Privacy in outputs", "No individuals described", "30 summaries", "Hand check", "None", "None", "None (D20)", "Pass"),
    ("AQ-08", "AI", "Declines handled", "A declined image is recorded, not guessed", "-", "-", "Recorded as declined", "Recorded", "Code path built; no decline happened in testing", "Partly"),
    ("NF-01", "Non-functional", "Cost (BRD v1.1)", "Under $0.025 per image", "30 images", "Call log", "Under $0.025", "Average and every image", "Average $0.023; highest $0.040 (DF-02)", "Partly"),
    ("NF-02", "Non-functional", "Speed", "Claude under 10 s per image", "30 images", "Call log", "Under 10 s", "Average and every image", "Average 9.0 s; 10 of 30 over 10 s, slowest 17.9 s (DF-03)", "Partly"),
    ("NF-03", "Non-functional", "Runs locally; keys safe", "Only Claude calls leave the computer; key never shown", "-", "Inspect setup", "Local dashboard; key in .env; .env not in Git", "All true", "True", "Pass"),
    ("NF-04", "Non-functional", "Reproducible", "Versions pinned; dataset fingerprinted; prompts versioned", "-", "Inspect files", "requirements.txt, MANIFEST.md, prompts/", "All present", "Present", "Pass"),
]

# Business UAT results as Tez reports them: id -> (actual result, status, date)
BUSINESS_RESULTS = {
    "BU-01": ("E04: count shown as 'estimated'; square numbers add up to it", "Pass", "15 Nov 2026"),
    "BU-02": ("E01: warm colour on the crowd; busiest square named", "Pass", "15 Nov 2026"),
    "BU-03": ("E15: quiet parts uncoloured; summary names empty squares", "Pass", "15 Nov 2026"),
    "BU-04": ("E03: summary says where people are concentrated, matching the photo", "Pass", "15 Nov 2026"),
    "BU-05": ("E02 High concentration requiring review; E09 No visible congestion; no 'unsafe'", "Pass", "15 Nov 2026"),
    "BU-06": ("History: all 30 images listed with count, level and congestion; chart shows differences", "Pass", "15 Nov 2026"),
    "BU-07": ("Review queue: E03 shows 'low confidence; high concentration'; wording 'may want to review'", "Pass", "15 Nov 2026"),
    "BU-08": ("5 images checked: no staffing orders or automatic actions; levels marked prototype", "Pass", "15 Nov 2026"),
    "BU-09": ("All 10 queued results reviewed (all Correct), saved and shown in Monitoring. No notes added; later reviews took about 2 s each (see risk: rubber-stamping)", "Pass", "15 Nov 2026"),
    "BU-12": ("About 10 images: no appearance, age, gender, clothing or identity mentioned", "Pass", "15 Nov 2026"),
    "BU-11": ("Monitoring: 'Needs investigation' lists failed requests and the average-miss pass mark with their limits; 10 reviewed, 0% incorrect", "Pass", "15 Nov 2026"),
    "BU-10": ("New photo analysed in 11.5 s for $0.028: 5 people, Normal, high confidence; shown in History. First try showed an error (DF-09) and a squashed heatmap (DF-10); both fixed and re-checked", "Pass", "15 Nov 2026"),
}

DEFECTS = [  # id, found in, severity, description, suggested fix, status
    ("DF-01", "AQ-01", "Medium", "Average counting miss 3.8 people, above the pass mark of 3; caused mainly by E01 (200 people, counted 160)", "Count very large crowds in zoomed tiles; keep low confidence as a review trigger; accepted for the prototype (D17)", "Accepted"),
    ("DF-02", "NF-01", "Low", "Cost of the busiest images up to $0.040, above the $0.025 limit (average $0.023 is within)", "Treat the limit as an average (as monitoring does), or cap answer length", "Open"),
    ("DF-03", "NF-02", "Low", "10 of 30 images took over 10 s (slowest 17.9 s); average 9.0 s", "Treat the limit as an average, or lower effort for quiet scenes", "Open"),
    ("DF-04", "Error analysis", "Low", "Claude's own observations can use different crowd words from our rule-based level", "Dashboard shows our summary first, the model's observations as secondary (done)", "Fixed"),
    ("DF-05", "X17", "High", "Impossible counts (e.g. 1,439,646,464,646,464) passed the answer check", "Sense check rejects counts over 500 (CR-15)", "Fixed"),
    ("DF-06", "X15", "Medium", "Account ran out of API credit: 30 calls failed", "Failures logged with the API's message; monitoring alert on failed requests (D22)", "Fixed"),
    ("DF-07", "ST-22", "Low", "Video-ready input (time, camera name) not built", "Built with the video design (15 Nov)", "Fixed"),
    ("DF-09", "BU-10", "High", "An uploaded image couldn't be shown after analysis: its saved result didn't keep the image's location", "Results now keep the full image path; the saved result repaired", "Fixed"),
    ("DF-10", "BU-10", "Low", "Heatmap squashed a wide photo into a square (the dataset images are all square)", "Heatmap keeps the photo's shape", "Fixed"),
    ("DF-08", "BU-09", "Medium", "Review can become rubber-stamping: 10 of 10 marked Correct, later ones in about 2 s each, no notes", "Show the reviewer what to check; require a note when confirming a low-confidence result; track time per review in monitoring; risk register (Step 19)", "Open")
]


def sheet(wb, title, headers, rows, widths):
    ws = wb.create_sheet(title)
    ws.append(headers)
    for c in ws[1]:
        c.font, c.fill, c.alignment, c.border = BOLD, HEAD, WRAP, BOX
    for r in rows:
        ws.append(list(r))
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font, c.alignment, c.border = F, WRAP, BOX
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    ws.freeze_panes = "B2"
    return ws


def main():
    wb = Workbook()
    ov = wb.active; ov.title = "Overview"
    lines = [("Casino Floor Operations Intelligence System: Testing and User Acceptance (document 08)", True), ("", False),
             ("What is tested: the prototype built in Week 5, Phases 1–6, against the business requirements (02, v1.1) and the AI quality requirements.", False),
             ("Business UAT: Tez, as the floor supervisor, runs each test on the dashboard (http://localhost:8505) and fills in Actual result, Status, Tester and Date.", False),
             ("System & AI tests: run by Claude (delivery) with evidence from the evaluation runs (evals/experiment-log.md); signed off by Tez.", False),
             ("Status values: Pass, Fail, Partly, Pending, Not run. Failures and partial passes are logged on the Defects sheet.", False),
             ("Prototype: crowd and congestion levels are prototype values; real thresholds would be agreed with operations.", False),
             (f"Prepared {DATE}.", False)]
    for i, (t, b) in enumerate(lines, 1):
        ov.cell(row=i, column=1, value=t).font = Font(name="Arial", size=12 if b else 10, bold=b)
    ov.column_dimensions["A"].width = 140

    bu = sheet(wb, "Business UAT", ["ID", "Business question", "Tested by", "Scenario and data", "What the tester does", "Pass criteria", "Business outcome it proves",
                                    "Actual result", "Status", "Tester", "Date", "Notes"],
               [(i, q, "Tez (floor supervisor)", s, d, p, o, *(lambda r: (r[0], r[1], "Tez", r[2]))(BUSINESS_RESULTS.get(i, ("", "Pending", ""))), "")
                for i, q, s, d, p, o in BUSINESS],
               [7, 30, 14, 28, 36, 40, 28, 30, 10, 10, 10, 20])
    st = sheet(wb, "System & AI tests", ["ID", "Type", "Area", "Scenario", "Test data", "Steps", "Expected result", "Pass criteria", "Actual result", "Status", "Tester", "Date"],
               [(*r, ME, DATE) for r in SYSTEM], [7, 13, 26, 30, 22, 22, 28, 22, 40, 9, 15, 11])
    for ws, col, n in [(bu, "I", len(BUSINESS)), (st, "J", len(SYSTEM))]:
        dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=True)
        ws.add_data_validation(dv); dv.add(f"{col}2:{col}{n + 1}")

    sm = wb.create_sheet("Summary")
    sm.append(["Status", "Business UAT", "System & AI tests", "Total"])
    for i, s in enumerate(STATUSES, 2):
        sm.append([s, f"=COUNTIF('Business UAT'!I:I,A{i})", f"=COUNTIF('System & AI tests'!J:J,A{i})", f"=B{i}+C{i}"])
    sm.append(["Total", "=SUM(B2:B6)", "=SUM(C2:C6)", "=SUM(D2:D6)"])
    for row in sm.iter_rows():
        for c in row:
            c.font, c.border = (BOLD if c.row == 1 else Font(name="Arial", size=10, bold=c.row == 7)), BOX
            if c.row == 1:
                c.fill = HEAD
    for col in "ABCD":
        sm.column_dimensions[col].width = 20

    sheet(wb, "Defects", ["ID", "Found in", "Severity", "Description", "Suggested fix", "Status"], DEFECTS, [7, 14, 10, 60, 55, 11])
    wb.save(OUT)
    print(f"written {OUT.name}: {len(BUSINESS)} business tests, {len(SYSTEM)} system and AI tests, {len(DEFECTS)} defects")


if __name__ == "__main__":
    main()
