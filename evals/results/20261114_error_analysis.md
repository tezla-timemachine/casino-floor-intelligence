# Step 13: error analysis (14 Nov 2026)

Where the product model (Claude Opus 5.5, prompt v3.1) goes wrong, looked at by eye, with likely reasons and possible improvements. Also covers the second model's failures (Moondream) and a check of every summary for unsupported statements. Images: `20261114_worst_images.jpg`; every variant tested: `evals/experiment-log.md`.

## 1. Claude's six biggest counting misses

*The picture sheets (`20261114_worst_images.jpg`, `heatmaps/`) show people's faces, so they are kept on the project computer and not published (privacy note, D25).*

| Image | Expected (hand count, range) | Model result | Difference | Likely reason | Possible improvement |
|---|---|---|---|---|---|
| **E01** | 200 (180–250) | 160 (earlier v3 runs: 200–230) | −40 | **Very dense crowd**, high wide angle; distant people are a few pixels; heads overlap; motion blur | Count the image in zoomed tiles and add them up; a person detector for very large crowds; low confidence sends it to review |
| **E03** | 60 (40–75) | 75 (v3: 65–75) | +15 | **Dense standing crowd at the back**; people and dark suits merge; the hand count itself is uncertain (wide range). The model's count is inside Tez's range | Score against the range as well as the best count; re-count this image (labelling log) |
| **E02** | 100 (90–200) | 85 (v3: 70–90) | −15 | **Distance, low light and pillars blocking the view**; people among slot banks | Tiles; brighten dark images before sending; flag "partly blocked view" |
| **E18** | 50 (45–60) | 42 (v3: 34–45) | −8 | **Busy background**: patterned carpet and many dark chairs look like seated people at a distance; bright, elevated view. Consistently low | Tiles; a prompt rule on chairs against people |
| **E24** | 32 (30–35) | 27 (v3: 30–35) | −5 | **Not a casino floor** (computer workstations); people hidden behind monitors | The model already flags it as not a casino; the product could route such images straight to review |
| **E25** | 32 (25–40) | 27 (v3: 24–27) | −5 | **Eye-level view: people behind people**, crowded around one table and in the background | Within Tez's range; eye-level views will always hide people. A higher camera fixes it in real use |

## 2. Patterns

| Brief's suspected cause | Seen here? | Evidence |
|---|---|---|
| Crowded scenes | **Yes, the main cause** | All 6 biggest misses have 32 or more people |
| People partly hidden | Yes | E02 (pillars), E24 (monitors), E25 (people behind people) |
| Poor lighting | Partly | E02 is dim. But the 4 darkest images were all counted well (average miss 1) |
| Distant people | Yes | E01, E02, E18: small figures at the back |
| Reflections | Not seen | No count error traced to a reflection; the model also mentioned the risk itself (E05 in Phase 2) |
| Objects blocking people | Yes | Pillars (E02), monitors (E24), chairs (E18) |
| Unusual camera angles | **Yes** | 4 of 6 are elevated views, the CCTV-like angle; misses grow with distance |
| Complex backgrounds | Yes | E18's patterned carpet and rows of chairs |

- **The model knows when it's unsure:** 5 of the 6 misses were marked **low** confidence, and the sixth medium. Sending low-confidence results to a person (Step 14) would catch all of the big misses.
- **It leans low in big crowds** (E01, E02, E18), and slightly high in one dense standing crowd (E03).
- **Small and empty scenes are reliable:** every image with 0–5 people was counted within ±1.

## 3. The second model's failures (Moondream)

| Failure | Example | Likely reason | Improvement |
|---|---|---|---|
| Gets stuck repeating itself | "table.4.4.4.4…" in the object list; counts like 1,439,646,464,646,464 | A very small model (about 2 billion parameters) losing its place in long or crowded answers | Not fixable by prompting; would need a larger local model. Our sense check now rejects impossible counts (CR-15) |
| Can't fill the full answer form | 0 of 5 | The form is too complex for it | Ask it one simple question at a time, or use a larger model |
| Undercounts crowds badly | E25: 14 against 32; E05: 6 against 20 | Limited detail at this model size | Not suitable for crowds |

## 4. Summaries: unsupported statements and privacy

All 30 of Claude's own summaries (prompt v3.1) were read against the rules in the labelling guide.

| Check | Result |
|---|---|
| Descriptions of individuals (appearance, age, gender, clothing, identity) | **None** |
| Safety or staffing claims | **None** |
| Clearly unsupported statements | **None** |
| Borderline | 2: E30 *"event-style gaming setup … not a standard casino floor"* (a reasonable inference from the hall and pillars); E29 *"holding a dealer stick"* (an action, not an appearance) |
| Non-casino scenes flagged | Yes: E19 (restaurant) and E24 (computer area) both said so, as prompt v3.1 asks |

**One product issue found:** Claude's own summary sometimes uses **its own** crowd and congestion words ("busy", "moderate congestion"), which can differ from **our** rule-based levels on the same screen. **Improvement:** the dashboard shows our rule-based summary as the main text, with Claude's observations as a secondary note, or a prompt change stops Claude naming levels.

## 5. What this means

1. **Use low confidence as a review trigger:** it catches every big miss in this set (Decision G, Step 14).
2. **Crowds of 50+ in elevated views are the weak spot.** For real CCTV, test counting in zoomed tiles before relying on counts of large crowds.
3. **Non-casino or unusual images** should go to review, because the model flags them itself.
4. **Re-count E03 and E01** (already on the re-count list), since the hand counts there are uncertain too.
