## Per set (attacks found / deterministic-alone, TP, FP, false incidents)

| set | V10 | V19 | V19id |
|---|---|---|---|
| CADETS_E3 | 3/3, 31, 16, 10 | 3/3, 30, 16, 10 | 3/3, 30, 16, 10 |
| THEIA_E3 | 2/2, 109, 86, 6 | 2/2, 104, 85, 6 | 2/2, 104, 85, 6 |
| CLEARSCOPE_E3 | 0/0, 0, 0, 0 | 0/0, 0, 0, 0 | 0/0, 0, 0, 0 |
| FIVEDIRECTIONS_E3 | 2/1, 11, 166, 6 | 2/1, 11, 166, 6 | 2/1, 11, 166, 6 |
| TRACE_E3-trace | 3/3, 9, 70, 25 | 3/3, 9, 70, 25 | 3/3, 9, 70, 25 |
| THEIA_E5-theia | 0/0, 0, 97, 28 | 0/0, 0, 77, 28 | 0/0, 0, 77, 28 |
| OPTC_H201 | 1/1, 6, 19, 10 | 1/1, 6, 19, 10 | 1/1, 4, 19, 11 |
| OPTC_H501 | 1/1, 17, 70, 10 | 1/1, 17, 70, 10 | 1/1, 17, 70, 10 |
| OPTC_H051 | 1/1, 75, 53, 3 | 1/1, 75, 53, 3 | 1/1, 75, 53, 3 |
| ATLASV2_EDR-h1 | 8/4, 12, 49, 3 | 8/4, 12, 49, 3 | 9/9, 16, 63, 3 |
| ATLASV2_EDR-h2 | 0/0, 0, 26, 2 | 0/0, 0, 26, 2 | 0/0, 0, 26, 2 |
| CARBANAKV2_EDR-h1 | 1/1, 5, 83, 24 | 1/1, 5, 69, 24 | 1/1, 5, 122, 28 |
| CARBANAKV2_EDR-h2 | 1/1, 39, 131, 19 | 1/1, 39, 130, 21 | 1/1, 40, 181, 21 |
| CARBANAKV2_EDR-h3 | 1/1, 2, 72, 8 | 1/1, 2, 71, 8 | 1/1, 2, 131, 9 |
| CARBANAKV2_EDR-h4 | 1/1, 3, 24, 10 | 1/1, 3, 24, 10 | 1/1, 3, 43, 10 |
| CARBANAKV2_EDR-h5 | 1/1, 14, 89, 14 | 1/1, 14, 89, 14 | 1/1, 14, 77, 5 |
| CLEARSCOPE_E5-clearscope | 2/2, 4, 15, 6 | 2/2, 4, 15, 6 | 2/2, 4, 15, 6 |

## 16 development sets

| version | attacks | det-alone | TP | FP | precision | alert rows | false incidents | per host-day | buried |
|---|---|---|---|---|---|---|---|---|---|
| V10 | 26 | 21 | 333 | 1,051 | 0.241 | 1,469 | 178 | 2.51 | 1 |
| V19 | 26 | 21 | 327 | 1,014 | 0.244 | 1,411 | 180 | 2.54 | 1 |
| V19id | 27 | 26 | 330 | 1,199 | 0.216 | 1,603 | 177 | 2.49 | 2 |

False items under the current product grouping (0.11 digest): V10 100 (1.41/day), V19 101 (1.42/day), V19id 99 (1.39/day)

host-days: 71. Published 0.10 (paper tab:lab): 26 attacks, 21 deterministic-alone, TP 333, FP 1,051, 178 false incidents (2.51/day).
V19: attacks lost vs V10 []; gained []
V19id: attacks lost vs V10 []; gained [('ATLASV2_EDR-h1', 'atlasv2_edr_m1')]

## Held-out E5 ClearScope (second scoring of the host; held-out for 0.11-0.19)

- V10: attacks 2/2, TP 4, FP 15, false incidents 6 (2.0/day)
- V19: attacks 2/2, TP 4, FP 15, false incidents 6 (2.0/day)
- V19id: attacks 2/2, TP 4, FP 15, false incidents 6 (2.0/day)
Published 0.10 held-out: 2/2 attacks, TP 4, FP 15, 6 false incidents.

## ADP of the triage order, random tie order (500 permutations)

| set | V10 | V19 | V19id |
|---|---|---|---|
| CADETS_E3 | 1.00 | 1.00 | 1.00 |
| THEIA_E3 | 1.00 | 1.00 | 1.00 |
| CLEARSCOPE_E3 | 0.18 | 0.18 | 0.18 |
| THEIA_E5-theia | 0.00 | 0.00 | 0.00 |
| CLEARSCOPE_E5-clearscope-3att | 0.67 | 0.67 | 0.67 |
| OPTC_H051 | 0.87 | 0.86 | 0.85 |
| OPTC_H201 | 0.75 | 0.75 | 0.67 |
| OPTC_H501 | 0.90 | 0.90 | 0.90 |
| FIVEDIRECTIONS_E3 | 0.19 | 0.19 | 0.19 |
| TRACE_E3-trace | 0.13 | 0.13 | 0.13 |
mean over the eight published DARPA hosts, V10: 0.671
mean over the eight published DARPA hosts, V19: 0.670
mean over the eight published DARPA hosts, V19id: 0.659
Published 0.10 (paper tab:adp): eight-host mean 0.67.
