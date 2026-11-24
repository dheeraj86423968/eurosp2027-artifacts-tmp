# paper5 progress (updated 2026-11-15 13:18 UTC)

**Complete (2026-11-15 13:19 UTC): all 17 sets x 5 runs scored.** On the 16 development sets every run detected the
same 26 of 30 attacks (and the same attack on every host); FP 1,051-1,136 (run 1 = lab_v10, as published, is the
lowest; +8% at most), false incidents 173-178 (2.44-2.51 per host-day), incidents 216-221. Triage ADP is identical
across runs except FiveDirections E3 (0.14-0.22 random ties), CARBANAKv2 h2 / h3 (0.32-0.48 / 0.02-0.04) and E5
ClearScope's learned score. Detector-1 / detector-2 alone vary a lot (d2 found 0-3 E3 CADETS attacks). Paper text
updated accordingly (results 'development results', discussion 'training runs').

Status per host: runs trained (bundle present) / scored. Runs 2-5 are new seeds; run 1 = lab_v10 (re-scored for d1/d2).

| host | trained | scored | failed |
|---|---|---|---|
| CADETS_E3 | 2,3,4,5 | 1,2,3,4,5 | - |
| THEIA_E3 | 2,3,4,5 | 1,2,3,4,5 | - |
| CLEARSCOPE_E3 | 2,3,4,5 | 1,2,3,4,5 | - |
| THEIA_E5-theia | 2,3,4,5 | 1,2,3,4,5 | - |
| OPTC_H051 | 2,3,4,5 | 1,2,3,4,5 | - |
| OPTC_H201 | 2,3,4,5 | 1,2,3,4,5 | - |
| OPTC_H501 | 2,3,4,5 | 1,2,3,4,5 | - |
| CLEARSCOPE_E5-clearscope | 2,3,4,5 | 1,2,3,4,5 | - |
| TRACE_E3-trace | 2,3,4,5 | 1,2,3,4,5 | - |
| FIVEDIRECTIONS_E3 | 2,3,4,5 | 1,2,3,4,5 | - |
| ATLASV2_EDR-h1 | 2,3,4,5 | 1,2,3,4,5 | - |
| ATLASV2_EDR-h2 | 2,3,4,5 | 1,2,3,4,5 | - |
| CARBANAKV2_EDR-h1 | 2,3,4,5 | 1,2,3,4,5 | - |
| CARBANAKV2_EDR-h2 | 2,3,4,5 | 1,2,3,4,5 | - |
| CARBANAKV2_EDR-h3 | 2,3,4,5 | 1,2,3,4,5 | - |
| CARBANAKV2_EDR-h4 | 2,3,4,5 | 1,2,3,4,5 | - |
| CARBANAKV2_EDR-h5 | 2,3,4,5 | 1,2,3,4,5 | - |

Results: results/SUMMARY.md, results/summary.json.

