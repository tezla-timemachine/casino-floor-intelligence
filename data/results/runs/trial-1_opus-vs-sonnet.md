# Trial: Claude Opus 5.5 against Claude Sonnet 5.5 (same 5 images, prompt trial-1, medium effort)

| Image | Labelled | Opus count | Sonnet count | Opus cost | Sonnet cost | Opus s | Sonnet s | Crowd level (O/S) | Congestion (O/S) |
|---|---|---|---|---|---|---|---|---|---|
| empty | 0 | 24 | 14 | $0.0134 | $0.0066 | 6.4 | 4.1 | Normal / Normal | None / None |
| quiet | 3 | 3 | 3 | $0.0117 | $0.0063 | 4.1 | 3.9 | Normal / Normal | None / None |
| busy | 9 | 24 | 23 | $0.0217 | $0.0145 | 9.7 | 10.8 | Highly occupied / Busy | High, review / Moderate |
| dark | 2 | 7 | 5 | $0.0170 | $0.0066 | 7.0 | 4.3 | Normal / Normal | None / None |
| crowded | 15 | 40 | 28 | $0.0213 | $0.0070 | 9.5 | 4.4 | Busy / Busy | Moderate / Moderate |
| **Average** | | | | **$0.0170** | **$0.0082** | 7.3 | 5.5 | | |

- Both: 5 of 5 answers fit the form; no descriptions of individuals or safety/staffing claims in the summaries.
- They agree on the easy images and differ on the hard ones (Sonnet counts lower). Which is closer needs the hand counts (Phase 3).
- Sonnet meets the $0.01 cost limit; Opus doesn't. Sonnet's busy image took 10.8 s, just over the 10 s limit.
