# 0.10, 0.19 and the identity option across five training runs (seeds) on every available set

Written 2026-11-16 ~14:45 UTC, before any script of this experiment is written and before any training or run.
Requested by the user for the IEEE S&P paper ("retrain to add about what happens at different seeds"), after
artifacts/paper_v19 compared V10 / V19 / V19id with one training run (the paper's run 1 bundles).

## Question
paper_v19 measured the three versions on the learned models of one training run. Here the same comparison is repeated
on four more training runs per host, to report (a) how much each version's results move across training seeds and
(b) whether the V19 - V10 and V19id - V10 differences hold on every run or are within seed noise.
This is a measurement only: **no design, configuration, threshold or evaluation change may be made because of these
results**, on any host.

## Runs
- **Run 1** = artifacts/paper_v19 results (paper's run 1 bundles `v07rel` / `b07rel`), unchanged.
- **Runs 2-5** = new trainings, exactly the training path and seeds of artifacts/lab_paper5 (seed base 100 x (r - 1):
  word2vec b, detector-1 b..b+2, detector-2 b..b+4; the 0.10 code tree 9b1b23f, image pdp/server:v101rc, same endpoint
  overrides, same train / validation days, asserted against run 1's manifest). Script: lab_paper5 train5.py copied,
  the only change being the output directory (/data/paper19s/SET/rR; /data/paper5 still holds that study's manifests).
  lab_paper5's run 2-5 bundles were deleted after scoring and detector-2 GPU training is not bit-reproducible, so these
  are new trainings with the same seeds, not copies; their V10 numbers are compared with lab_paper5's run-r numbers and
  every difference is reported (not corrected).
- Layers 1-2 and detector-3 are fitted by counting and have no seed: each new bundle's layers.json must equal run 1's
  (checked by train5.py; any difference reported). The V19 and V19id layer specs are paper_v19's (out/layers22-SET-RP2.json,
  out/layersp-SET-RP2id.json, fitted on the same fit days), used unchanged for every run. Fleet prevalence uses the
  other members' run-1 specs for every run, as lab_paper5 and paper_v19.

## Scoring (paper_v19's pipeline, unchanged)
paper_v19 evalp.py; only addition: `--bundle DIR` (the scored set's bundle; default unchanged). Incidents: inc13.py
with the 0.10 grouping (git archive 70b6a57 engine server), as paper_v19's inc010.json; also the current product
grouping (as inc.json). ADP: paper_v19 adp_ties.py (random tie order, 500 permutations, seed 0) on each run's npz.
E5 ClearScope also with the lockwatch third attack (`-3att`), as paper_v19.

## Reporting
- Per run and version, totals on the 16 development sets: attacks, deterministic-alone attacks, TP, FP, false
  incidents (0.10 grouping) and per host-day; the eight-host random-tie ADP mean (paper tab:adp hosts).
- Over runs: mean, sample sd, min, max (n = completed runs; a total is computed only for runs where all 16 sets
  completed). Per run, the paired differences V19 - V10 and V19id - V10, and whether their sign is the same in every run.
- Whether the set of detected attacks changes across runs, per version.
- E5 ClearScope separately (held-out for 0.11-0.19, scored with run 1 in paper_v19; runs 2-5 are new trainings of it).
- A host / run that fails is reported as failed with its error; nothing is estimated or filled in.
- The paper gets what is complete at 2026-11-18 06:00 UTC (deadline 17 Nov AoE); anything later is added to the
  artifact only, and the paper text says how many runs it reports.

## Order and resources (live client and production first)
Run-major order (all hosts' run 2, then run 3, ...), so that partial results are whole runs; within a run, longest
trainings first. At most two trainings at once (lab_paper5 lane checks: >= 10 GB free GPU memory, >= 12 GB available
RAM, 32 GB for TRACE, disk free after the bundle >= 26 GB); no training starts between 23:30 and 00:45 UTC (the
production worker trains livehost's daily model ~00:05 UTC). One scoring at a time. Containers at nice 15, OOM score
800-900, memory limits; the benchmark data volume is read-only for scoring. Each bundle is deleted after scoring except
manifest.json, calibration.json, layers.json. Nothing touches the production database, API, agents or livehost.
