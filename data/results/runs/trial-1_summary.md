# Pipeline v1 trial: 20261113_claude-opus-5-5_trial-1_trial

5 train images (not in the evaluation set), prompt `trial-1`, Claude Opus 5.5 at medium effort.

| Image | Labelled | Claude count | By third (L/C/R) | Crowd level | Congestion | Confidence | Seconds | Output tokens | Cost |
|---|---|---|---|---|---|---|---|---|---|
| empty | 0 | 24 | 7/14/3 | Normal | No visible congestion | low | 6.39 | 340 | $0.0134 |
| quiet | 3 | 3 | 0/2/1 | Normal | No visible congestion | high | 4.1 | 257 | $0.0117 |
| busy | 9 | 24 | 5/9/10 | Highly occupied | High concentration requiring review | medium | 9.66 | 755 | $0.0217 |
| dark | 2 | 7 | 3/2/2 | Normal | No visible congestion | low | 6.98 | 519 | $0.0170 |
| crowded | 15 | 40 | 17/11/12 | Busy | Moderate congestion | low | 9.48 | 737 | $0.0213 |

**Total:** 5/5 answers fit the form first time; $0.0851; average 7.3 s per image.

Accuracy is not judged here: true counts come from the hand-counted evaluation set (07).
