# Paper evaluation of the latest release (0.19) on every available set

Written 2026-11-16 ~10:15 UTC, before the evaluation script is written and before any run. Requested by the user for
the IEEE S&P paper ("test the most latest and most promising version on all the datasets present"), with the
condition that the live client simulation (livehost, production) is not disturbed.

## Versions

- **V19** = the released detection defaults at commit 500eaa3 (detection 0.19, in production since 11-16 09:58 UTC):
  0.10 + one alert per file version (`exec_once`, lab_v16) + no data flow through content-less files and
  confidentiality ending at exec (`pseudo_files`, `exec_declassify`, lab_v19). The learned detectors are those of the
  paper's 0.10 run (the same bundles, `v07rel` / `b07rel`), so V10 and V19 differ only in the deterministic layers,
  which are re-fitted on the same fit days (lab_v19's harness, Sigma off as in the paper). Alert policy, fleet
  prevalence (K = 2, drop) and incident grouping as 0.10.
- **V10** = the paper's 0.10 run, re-scored in the same pass (the bundle's own layers), as a reproduction check: it
  must give the published 26 attacks / 21 deterministic-alone / TP 333 / FP 1,051 on the 16 development sets and 2/2
  attacks / FP 15 on E5 ClearScope. If it does not, the difference is reported and V19 is compared with the V10 of
  this pass.
- **V19id** (secondary, an endpoint option, not a default) = V19 + `program_identity` (layer 2 keyed by program
  identity, backslash paths parsed, versions collapsed). lab_v16 rejected it as a default (FP +14 %) although it found
  one more attack; reported as "option", never as the headline.

"Most promising" is V19: the newest configuration that passed every pre-registered decision rule.

## Sets

All 17 sets with recorded data and ground truth on this machine: the 16 development sets of the paper (DARPA E3
CADETS, THEIA, ClearScope, FiveDirections, TRACE; E5 THEIA; OpTC 201, 501, 051; ATLASv2 h1, h2; CARBANAKv2 h1-h5) and
E5 ClearScope. Not available: E5 CADETS, FiveDirections and TRACE (not downloaded; ~38 GB for CADETS alone).

**E5 ClearScope's status, stated plainly.** It was the held-out host of 0.10, scored once on 11-09. Everything after
0.10 (labs v11-v19) was decided on the development sets and on livehost only; nobody looked at E5 ClearScope's alerts
or scores for those decisions. V19 is frozen (commit 500eaa3) before this run, and E5 ClearScope is scored once with
it. It is unseen for every change since 0.10, but its 0.10 result was seen, so it is reported as "held-out for 0.11-0.19,
second scoring of the host".

## Metrics (as the paper reports 0.10; scripts from artifacts/lab_v10 and paper_analysis, unchanged where possible)

Per set and in total: attacks detected, attacks detected by the deterministic layers alone, TP / FP nodes, precision,
alert rows, incidents and false incidents per host-day (pdp_server.incidents grouping of the code at 500eaa3, applied
to V10 and V19 alike), ADP of the triage order under random tie order (500 permutations, paper_analysis
adp_random_ties.py) on the eight DARPA hosts with published baselines and on all sets.

## Reporting

No decision rule: this is a measurement. Every number of every version is reported, including any loss. The paper
keeps 0.10 as its pre-registered system; V19 is added as a later release evaluated the same way, labelled as such.

## Not disturbing the live client

Read-only access to the benchmark data (volume pdp_pdp_data mounted read-only except the scratch output directory);
containers at reduced CPU priority with a memory cap and the OOM killer preferring them; at most two sets at a time
on the GPU; nothing touches the production database, API, agents or livehost. The production training worker keeps its
GPU slots (livehost's next model is due ~00:05 UTC; this run finishes before). The daily production backup (~17:30
UTC, needs ~40 GB free) is checked for disk before starting.
