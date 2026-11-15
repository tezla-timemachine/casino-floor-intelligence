# Evaluation results: moondream (14 Nov 2026)

True counts: Tez's hand counts (D3, D10). "Within" = misses by no more than 1 person or 20% of the true count, whichever is larger. "In range" = inside Tez's low-high range. "Lean" = average (model minus true): positive counts too high.

## Overall, by model and prompt

| model | prompt | counted | avg_miss | median_miss | within_pct | in_range_pct | lean | crowd_level_agree_pct | busiest_third_pct | form_ok_pct | avg_cost | avg_seconds | total_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| moondream | m-count | 22 | 2.9 | 1.0 | 64 | 41 | -2.4 | 82 | 0 | 73 | 0.0 | 7.5 | 0.0 |
| moondream | v3.1 | 2 | 7.5 | 7.5 | 50 | 0 | -7.5 | 50 | 0 | 0 | 0.0 | 69.3 | 0.0 |

## By true number of people (prompts v2 and v3)

| model | prompt | band | images | avg_miss | within_pct | lean |
|---|---|---|---|---|---|---|
| moondream | m-count | 0 | 5 | 0.4 | 80.0 | 0.4 |
| moondream | m-count | 1-5 | 8 | 0.8 | 100.0 | 0.0 |
| moondream | m-count | 16-50 | 5 | 16.0 | 0.0 | -16.0 |
| moondream | m-count | 6-15 | 8 | 3.3 | 29.0 | -3.3 |
| moondream | m-count | over 50 | 4 |  |  |  |
| moondream | v3.1 | 0 | 1 |  |  |  |
| moondream | v3.1 | 1-5 | 1 |  |  |  |
| moondream | v3.1 | 16-50 | 1 | 14.0 | 0.0 | -14.0 |
| moondream | v3.1 | 6-15 | 1 | 1.0 | 100.0 | -1.0 |
| moondream | v3.1 | over 50 | 1 |  |  |  |

## By group in the evaluation set (prompts v2 and v3)

| model | prompt | chosen_as | images | avg_miss | within_pct | lean |
|---|---|---|---|---|---|---|
| moondream | m-count | busy | 8 | 3.4 | 20.0 | -3.4 |
| moondream | m-count | close-up | 2 | 1.0 | 100.0 | -1.0 |
| moondream | m-count | crowded | 4 |  |  |  |
| moondream | m-count | dark | 4 | 3.8 | 75.0 | -3.8 |
| moondream | m-count | empty (labelled) | 4 | 0.8 | 75.0 | 0.8 |
| moondream | m-count | quiet | 8 | 3.7 | 71.0 | -3.1 |
| moondream | v3.1 | busy | 1 | 1.0 | 100.0 | -1.0 |
| moondream | v3.1 | close-up | 1 |  |  |  |
| moondream | v3.1 | crowded | 1 |  |  |  |
| moondream | v3.1 | dark | 1 | 14.0 | 0.0 | -14.0 |
| moondream | v3.1 | empty (labelled) | 1 |  |  |  |

## By lighting (prompts v2 and v3)

| model | prompt | lighting | images | avg_miss | within_pct | lean |
|---|---|---|---|---|---|---|
| moondream | m-count | bright | 2 |  |  |  |
| moondream | m-count | dark | 4 | 3.8 | 75.0 | -3.8 |
| moondream | m-count | normal | 24 | 2.7 | 61.0 | -2.1 |
| moondream | v3.1 | dark | 1 | 14.0 | 0.0 | -14.0 |
| moondream | v3.1 | normal | 4 | 1.0 | 100.0 | -1.0 |

## By camera angle (prompts v2 and v3)

| model | prompt | angle | images | avg_miss | within_pct | lean |
|---|---|---|---|---|---|---|
| moondream | m-count | close-up | 6 | 1.2 | 83.0 | -0.5 |
| moondream | m-count | elevated | 5 |  |  |  |
| moondream | m-count | eye-level | 19 | 3.5 | 56.0 | -3.1 |
| moondream | v3.1 | close-up | 1 |  |  |  |
| moondream | v3.1 | elevated | 1 |  |  |  |
| moondream | v3.1 | eye-level | 3 | 7.5 | 50.0 | -7.5 |

## By the model's confidence (prompts v2 and v3)

| model | prompt | confidence | images | avg_miss | within_pct | lean |
|---|---|---|---|---|---|---|
| moondream | m-count |  | 30 | 2.9 | 64.0 | -2.4 |
| moondream | v3.1 |  | 3 |  |  |  |
| moondream | v3.1 | low | 2 | 7.5 | 50.0 | -7.5 |

## The 10 biggest misses

| model | prompt | eval_id | chosen_as | actual | model_count | difference | confidence |
|---|---|---|---|---|---|---|---|
| moondream | m-count | E25 | quiet | 32 | 14.0 | -18.0 |  |
| moondream | m-count | E05 | dark | 20 | 6.0 | -14.0 |  |
| moondream | v3.1 | E05 | dark | 20 | 6.0 | -14.0 | low |
| moondream | m-count | E15 | busy | 12 | 6.0 | -6.0 |  |
| moondream | m-count | E30 | quiet | 12 | 6.0 | -6.0 |  |
| moondream | m-count | E19 | busy | 10 | 5.0 | -5.0 |  |
| moondream | m-count | E20 | busy | 8 | 5.0 | -3.0 |  |
| moondream | m-count | E17 | busy | 6 | 4.0 | -2.0 |  |
| moondream | m-count | E11 | empty (labelled) | 0 | 2.0 | 2.0 |  |
| moondream | m-count | E13 | close-up | 3 | 2.0 | -1.0 |  |
