# paper_v19_seeds results

Complete runs (all 16 development sets scored): [1, 2, 3, 4, 5]. Partial: none. Host-days: 71.

## 16 development sets, per run

| run | version | attacks | det-alone | TP | FP | false incidents | ADP (8 hosts) | per host-day |
|---|---|---|---|---|---|---|---|---|
| 1 | V10 | 26 | 21 | 333 | 1,051 | 178 | 0.671 | 2.51 |
| 1 | V19 | 26 | 21 | 327 | 1,014 | 180 | 0.670 | 2.54 |
| 1 | V19id | 27 | 26 | 330 | 1,199 | 177 | 0.659 | 2.49 |
| 2 | V10 | 26 | 21 | 331 | 1,116 | 178 | 0.672 | 2.51 |
| 2 | V19 | 26 | 21 | 325 | 1,079 | 179 | 0.674 | 2.52 |
| 2 | V19id | 27 | 26 | 328 | 1,264 | 176 | 0.663 | 2.48 |
| 3 | V10 | 26 | 21 | 331 | 1,067 | 174 | 0.670 | 2.45 |
| 3 | V19 | 26 | 21 | 325 | 1,025 | 176 | 0.672 | 2.48 |
| 3 | V19id | 27 | 26 | 328 | 1,207 | 174 | 0.658 | 2.45 |
| 4 | V10 | 26 | 21 | 331 | 1,120 | 176 | 0.670 | 2.48 |
| 4 | V19 | 26 | 21 | 325 | 1,080 | 178 | 0.670 | 2.51 |
| 4 | V19id | 27 | 26 | 328 | 1,265 | 175 | 0.660 | 2.46 |
| 5 | V10 | 26 | 21 | 331 | 1,088 | 177 | 0.671 | 2.49 |
| 5 | V19 | 26 | 21 | 322 | 1,047 | 178 | 0.673 | 2.51 |
| 5 | V19id | 27 | 26 | 325 | 1,233 | 175 | 0.662 | 2.46 |

## Over the 5 complete runs: mean (sd) [min-max]

| version | attacks | det-alone | TP | FP | false incidents | ADP (8 hosts) |
|---|---|---|---|---|---|---|
| V10 | 26 (0.0) [26-26] | 21 (0.0) [21-21] | 331.4 (0.9) [331-333] | 1,088.4 (30.1) [1,051-1,120] | 176.6 (1.7) [174-178] | 0.671 (0.001) [0.670-0.672] |
| V19 | 26 (0.0) [26-26] | 21 (0.0) [21-21] | 324.8 (1.8) [322-327] | 1,049 (30.3) [1,014-1,080] | 178.2 (1.5) [176-180] | 0.672 (0.002) [0.670-0.674] |
| V19id | 27 (0.0) [27-27] | 26 (0.0) [26-26] | 327.8 (1.8) [325-330] | 1,233.6 (30.9) [1,199-1,265] | 175.4 (1.1) [174-177] | 0.660 (0.002) [0.658-0.663] |

## Paired differences per run (version - V10); 'same sign' = the sign is equal in every complete run

| difference | attacks | det-alone | TP | FP | false incidents | ADP (8 hosts) |
|---|---|---|---|---|---|---|
| V19 - V10 | +0, +0, +0, +0, +0 (same sign) | +0, +0, +0, +0, +0 (same sign) | -6, -6, -6, -6, -9 (same sign) | -37, -37, -42, -40, -41 (same sign) | +2, +1, +2, +2, +1 (same sign) | -0.001, +0.002, +0.003, +0.001, +0.002 (sign varies) |
| V19id - V10 | +1, +1, +1, +1, +1 (same sign) | +5, +5, +5, +5, +5 (same sign) | -3, -3, -3, -3, -6 (same sign) | +148, +148, +140, +145, +145 (same sign) | -1, -2, +0, -1, -2 (sign varies) | -0.013, -0.009, -0.012, -0.010, -0.009 (same sign) |

## Detected attack sets across runs (16 development sets)

- V10: 26 attacks found in every run, 26 in at least one
- V19: 26 attacks found in every run, 26 in at least one
- V19id: 27 attacks found in every run, 27 in at least one

## Per set: FP (and attacks) per run, runs 1..5 ('.' = not scored yet)

| set | V10 | V19 | V19id |
|---|---|---|---|
| CADETS_E3 | 16/3 15/3 15/3 15/3 15/3 | 16/3 15/3 15/3 15/3 15/3 | 16/3 15/3 15/3 15/3 15/3 |
| THEIA_E3 | 86/2 95/2 86/2 86/2 86/2 | 85/2 94/2 85/2 85/2 85/2 | 85/2 94/2 85/2 85/2 85/2 |
| CLEARSCOPE_E3 | 0/0 0/0 0/0 0/0 0/0 | 0/0 0/0 0/0 0/0 0/0 | 0/0 0/0 0/0 0/0 0/0 |
| FIVEDIRECTIONS_E3 | 166/2 159/2 166/2 163/2 167/2 | 166/2 159/2 166/2 163/2 167/2 | 166/2 159/2 166/2 163/2 167/2 |
| TRACE_E3-trace | 70/3 70/3 70/3 70/3 70/3 | 70/3 70/3 70/3 70/3 70/3 | 70/3 70/3 70/3 70/3 70/3 |
| THEIA_E5-theia | 97/0 96/0 114/0 103/0 98/0 | 77/0 76/0 89/0 80/0 74/0 | 77/0 76/0 89/0 80/0 74/0 |
| OPTC_H201 | 19/1 19/1 19/1 20/1 19/1 | 19/1 19/1 19/1 20/1 19/1 | 19/1 19/1 19/1 20/1 19/1 |
| OPTC_H501 | 70/1 76/1 70/1 70/1 70/1 | 70/1 76/1 70/1 70/1 70/1 | 70/1 76/1 70/1 70/1 70/1 |
| OPTC_H051 | 53/1 53/1 53/1 53/1 53/1 | 53/1 53/1 53/1 53/1 53/1 | 53/1 53/1 53/1 53/1 53/1 |
| ATLASV2_EDR-h1 | 49/8 49/8 49/8 49/8 49/8 | 49/8 49/8 49/8 49/8 49/8 | 63/9 63/9 63/9 63/9 63/9 |
| ATLASV2_EDR-h2 | 26/0 26/0 26/0 26/0 26/0 | 26/0 26/0 26/0 26/0 26/0 | 26/0 26/0 26/0 26/0 26/0 |
| CARBANAKV2_EDR-h1 | 83/1 83/1 83/1 81/1 84/1 | 69/1 69/1 69/1 67/1 70/1 | 122/1 122/1 122/1 120/1 123/1 |
| CARBANAKV2_EDR-h2 | 131/1 131/1 132/1 131/1 131/1 | 130/1 130/1 131/1 130/1 130/1 | 181/1 180/1 181/1 180/1 181/1 |
| CARBANAKV2_EDR-h3 | 72/1 132/1 72/1 141/1 108/1 | 71/1 131/1 71/1 140/1 107/1 | 131/1 191/1 128/1 200/1 167/1 |
| CARBANAKV2_EDR-h4 | 24/1 24/1 24/1 24/1 24/1 | 24/1 24/1 24/1 24/1 24/1 | 43/1 43/1 43/1 43/1 43/1 |
| CARBANAKV2_EDR-h5 | 89/1 88/1 88/1 88/1 88/1 | 89/1 88/1 88/1 88/1 88/1 | 77/1 77/1 77/1 77/1 77/1 |
| CLEARSCOPE_E5-clearscope | 15/2 13/2 15/2 15/2 13/2 | 15/2 13/2 15/2 15/2 13/2 | 15/2 13/2 15/2 15/2 13/2 |

## Held-out E5 ClearScope per run (held-out for 0.11-0.19; runs 2-5 are new trainings)

- run 1: V10 2/2 attacks, TP 4, FP 15, false incidents 6, ADP(3 att) 0.67; V19 2/2 attacks, TP 4, FP 15, false incidents 6, ADP(3 att) 0.67; V19id 2/2 attacks, TP 4, FP 15, false incidents 6, ADP(3 att) 0.67
- run 2: V10 2/2 attacks, TP 4, FP 13, false incidents 6, ADP(3 att) 0.70; V19 2/2 attacks, TP 4, FP 13, false incidents 6, ADP(3 att) 0.70; V19id 2/2 attacks, TP 4, FP 13, false incidents 6, ADP(3 att) 0.70
- run 3: V10 2/2 attacks, TP 4, FP 15, false incidents 6, ADP(3 att) 0.67; V19 2/2 attacks, TP 4, FP 15, false incidents 6, ADP(3 att) 0.67; V19id 2/2 attacks, TP 4, FP 15, false incidents 6, ADP(3 att) 0.67
- run 4: V10 2/2 attacks, TP 4, FP 15, false incidents 6, ADP(3 att) 0.67; V19 2/2 attacks, TP 4, FP 15, false incidents 6, ADP(3 att) 0.67; V19id 2/2 attacks, TP 4, FP 15, false incidents 6, ADP(3 att) 0.67
- run 5: V10 2/2 attacks, TP 4, FP 13, false incidents 6, ADP(3 att) 0.69; V19 2/2 attacks, TP 4, FP 13, false incidents 6, ADP(3 att) 0.69; V19id 2/2 attacks, TP 4, FP 13, false incidents 6, ADP(3 att) 0.69

## V10 of runs 2-5 vs lab_paper5's run r (same seeds; separate trainings, detector-2 GPU training is not bit-exact)

| run | this study: attacks / TP / FP / false incidents | lab_paper5 | sets differing in FP |
|---|---|---|---|
| 2 (16 sets) | 26 / 331 / 1116 / 178 | 26 / 331 / 1112 / 177 | THEIA_E3 88->95, FIVEDIRECTIONS_E3 164->159, THEIA_E5-theia 95->96, OPTC_H501 70->76, CARBANAKV2_EDR-h3 137->132 |
| 3 (16 sets) | 26 / 331 / 1067 / 174 | 26 / 331 / 1061 / 173 | FIVEDIRECTIONS_E3 159->166, CARBANAKV2_EDR-h2 133->132 |
| 4 (16 sets) | 26 / 331 / 1120 / 176 | 26 / 331 / 1136 / 178 | THEIA_E3 95->86, FIVEDIRECTIONS_E3 164->163, THEIA_E5-theia 109->103, OPTC_H201 19->20, CARBANAKV2_EDR-h1 85->81, CARBANAKV2_EDR-h3 138->141 |
| 5 (16 sets) | 26 / 331 / 1088 / 177 | 26 / 334 / 1089 / 176 | CADETS_E3 16->15, FIVEDIRECTIONS_E3 165->167, THEIA_E5-theia 100->98, CARBANAKV2_EDR-h1 83->84, CARBANAKV2_EDR-h2 132->131 |
