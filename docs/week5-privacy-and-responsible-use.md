# Week 5 privacy and responsible use (Step 20)

**Status:** 15 Nov 2026. How the prototype treats people in images, who can see what, how long data is kept, how it's secured, and what a real casino would need to approve. **This is a prototype on public photos: a real deployment needs the casino's privacy, security, legal and operations teams to approve it first.**

---

## 1. What the system is for, and what it isn't

| The system **does** | The system **does not**, by design |
|---|---|
| Count people and show **where** they are (a 3×3 grid) | Recognise faces, or compare a face with anything |
| Describe how **areas** are used (busy, quiet, congested) | Identify, name or track a known customer |
| Write a summary about **the floor** | Describe anyone's appearance, age, gender, ethnicity or clothing |
| Flag areas a supervisor **may want to review** | Make decisions about people, staffing or safety |

**How this is enforced:**
- **The prompt** (v3.1) tells the model never to describe or identify individuals.
- **The answer form** only has fields for counts, areas, objects, levels and a summary. There's nowhere to put personal information.
- **Our summary** is built by rule from those fields.
- **Checked:** all 30 of Claude's own summaries were read by hand, and **none** described an individual (D20). Tez checked again in UAT (BU-12, passed).

---

## 2. What data exists, and where

| Data | Where | Contains people? | Leaves this computer? |
|---|---|---|---|
| Dataset images (322 public web photos, CC BY 4.0) | `data/raw/` | **Yes, faces are visible** | Only the evaluation and trial images, sent to Anthropic for analysis, with approval for each batch |
| Uploaded images (dashboard) | `data/uploads/` (1 image so far) | Possibly | Sent to Anthropic when analysed |
| Results: counts, grid, levels, summaries | `data/results/` | No personal information | No |
| Call log: model, time, cost, status | `data/results/call_log.csv` | No | No |
| Review decisions | `data/results/reviews.csv` | No | No |
| API key | `.env` (only the Mac's user can read it; never in GitHub) | — | Only to Anthropic, to authenticate |

**Online processing:** images sent to Claude go to Anthropic over an encrypted connection, and are handled under Anthropic's terms for API customers. For real footage, the casino's legal team would review those terms and any data-retention arrangement before anything is sent. Or it would choose an on-premises model; our Moondream test shows today's small local models aren't good enough yet (D19).

---

## 3. Who can access images (for real use)

| Role | Sees | Why |
|---|---|---|
| Floor supervisor | Live analysis, heatmap, summary for their area | To decide where to look |
| Reviewer | Flagged images and their results | To mark correct or incorrect |
| Operations analyst | Counts, trends and monitoring, **not images** by default | Monitoring needs numbers, not faces |
| Product owner or administrator | Settings, thresholds, change log | To run the product |

**Today's prototype has no login:** it runs only on this Mac (`localhost`). A real deployment needs **sign-in, role-based access and an access log** (limitations, Step 21).

---

## 4. Data retention

| Data | Prototype (now) | Proposed for real use |
|---|---|---|
| Camera frames and images | Kept for the project; uploads deleted at the end | **Deleted straight after analysis**; flagged images kept for review for up to **7 days** |
| Results (counts, grid, levels) | Kept | Kept up to **90 days** for trends; no images attached |
| Review decisions and call log | Kept | Kept **1 year** for monitoring and audit; no images |
| Anything with a face | Not stored beyond the image itself | Never stored outside the short review window |

The exact periods would follow the casino's own CCTV retention policy and local law.

---

## 5. Security

| Area | Now | Real use would add |
|---|---|---|
| API key | Private `.env` file, kept out of GitHub, never shown | A secrets manager; separate keys per environment; key rotation |
| Where it runs | One Mac, `localhost` only, not online | Hosted inside the casino's network, behind sign-in |
| Data in transit | Encrypted connection to Anthropic | The same, plus network rules on what can leave the building |
| Spending | $10 budget, cost logged per call, cap in the run scripts | Budget alerts and per-camera limits (video design) |
| Text inside images | Signs or screens could contain instructions | The answer form limits what the model can return; outputs are checked; the summary is rebuilt by our rules |
| Software | Package versions pinned | Security updates and dependency scanning |

---

## 6. Approvals needed before any real use

1. **Privacy / data protection:** a privacy impact assessment for analysing CCTV with AI. Purpose: occupancy only. Retention as above.
2. **Legal:** the lawful basis for processing footage, signage for customers, and the AI provider's terms.
3. **Information security:** where the system runs, access control, sending images to an online model or not.
4. **Operations:** zones, thresholds, who reviews, and how alerts are handled.
5. **Surveillance / security team:** camera access and how frames are taken.

Until these are in place, the system stays a **prototype on public images**.
