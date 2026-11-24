# Review Artifact — *When Do Learned Provenance Detectors Help?*
### Lessons from Building and Evaluating a Layered Intrusion Detector

This is the anonymised artifact for the paper's **Data Availability** statement. Its purpose is narrow and checkable:
it lets a reviewer **recompute every number in the paper** — every table, the held-out negatives included — from the
system's own alert rows and the public ground truth, with one standalone script and **no access to our detection
engine**.

The system is called **STRATA** in the paper; here it is "the engine", and some file and module names keep the
internal prefix `pdp`. The artifact covers the evaluated versions (**0.2 through 0.10**) and the later-release
appendix experiments: their protocols and decision records, the alert rows and per-node rankings behind the tables,
the original-detector baselines, and the EDR-conversion manifests. **The detection engine itself is not included** —
the paper specifies it in enough detail to re-implement.

## At a glance

- **Verify in ~1 minute** — `python3 recompute/recompute.py --gt <PIDSMaker GT> --perms 5` reproduces every
  *deterministic* number: TP/FP, attacks found, incidents, analyst workload, and the five-run ranges.
- **Verify fully (~1 hour)** — add `--perms 500` for the random-tie ADP expectations. Last run: **128 of 133 checks
  match** the paper; the five differences are random-tie ADPs that agree within rounding (see *Result of the last run*).
- **Included** — protocols + decision records, held-out preparation logs, per-host results, alert rows with their
  one-hop provenance context, original-detector (ProvFusion / Velox / ORTHRUS) baselines, EDR-to-host conversion
  manifests, a self-contained reference scorer, and the version-control timeline.
- **Not included** — the detection engine/server and the EDR-to-host conversion *code* (see *Not included, or only
  partly reproducible without the engine*).

## Contents

| path | what |
|---|---|
| `recompute/recompute.py` | standalone recomputation (python3 + numpy; no engine) |
| `recompute/hosts.json` | the 17 hosts: test days, ground-truth CSVs (PIDSMaker paths), attack counts |
| `recompute/recompute_output.txt` | output of the last run — every check: recomputed value, paper value, MATCH/DIFF |
| `recompute/recomputed.json` | all recomputed values, machine-readable |
| `records/` | the evaluation records, one directory per experiment (see *What is in `records/`*) |
| `records/PREREGISTRATION_TIMELINE.tsv` | version-control times at which each record file was added or changed |
| `data/v0.10_nodes/nodes-*.npz` | version 0.10 per-node ranking arrays, one per test node of every host (for ADP) |
| `docs/` | design and benchmark notes written as each version was built (`DETECTION_LAYERS.md`, `BENCHMARK_*.md`) |
| `MANIFEST.sha256` | SHA-256 of every file |

## Quick start

```
# 1. Public ground truth (not redistributed here): PIDSMaker's Ground_Truth/orthrus directory
git clone https://github.com/ubc-provenance/PIDSMaker     # tested with commit 438a05a
# 2. Recompute (numpy only; about 1 hour on one CPU core with 500 random tie orders, about 1 minute with --perms 5;
#    everything except the random-tie ADPs is deterministic and independent of --perms)
python3 recompute/recompute.py --gt PIDSMaker/Ground_Truth/orthrus [--perms 500]
```

The script prints one line per check, showing the recomputed value, the value printed in the paper, and MATCH or
DIFF. It writes everything to `recompute/recomputed.json`. ADP values from random tie orders are expectations over
`--perms` random orders, so they vary by about 0.01 between seeds. Such checks count as MATCH when the recomputed value
rounds to the paper's two-decimal value (tolerance 0.005).

**Ground truth.** The node-level labels are ORTHRUS's labels for the DARPA hosts (E3 CADETS, THEIA, TRACE,
ClearScope, FiveDirections; E5 THEIA, ClearScope; OpTC hosts 201, 501 and 051) and the labels PIDSMaker ships for
ATLASv2 and CARBANAKv2. All of them come from PIDSMaker's `Ground_Truth/orthrus` directory. The datasets themselves
are available from their creators (DARPA TC E3/E5, DARPA OpTC, ATLASv2, CARBANAKv2) and through PIDSMaker. Nothing
from them is redistributed here except the node labels and one-hop context inside the alert rows. A node is a
ground-truth node of an attack when its id (field `node_uuid` of an alert row) equals column 3 (`index_id`) of a row
of that attack's CSV. `recompute/hosts.json` lists the CSVs used for each host. Every alert row also stores the label
the authors computed (`gt`, `attacks`); the script recomputes both from the public CSVs and counts any disagreement
(there are none).

## Result of the last run (`recompute/recompute_output.txt`, 500 random tie orders, seed 0)

128 of 133 checks match the paper. All deterministic numbers match exactly, among them:
- 0.10 on the 16 development sets: 26 of 30 attacks, TP 333, FP 1,051, 71 host-days, 220 incidents of which 178 false, 2.51 false incidents per host-day;
- 0.9: 26 / 337 / 1,189 and 354 / 284;
- tab:layers, tab:ablation, tab:evidence, the 0.10 held-out row, the bootstrap intervals, the LotL counterfactual, and the STRATA columns of tab:orig and tab:replay;
- the five-run ranges.

The five differences are all random-tie-order ADPs. They vary between random-order seeds by more than the paper's
second decimal:

| value | recomputed | authors' run (`paper_analysis/adp_random_ties.txt`) | paper |
|---|---|---|---|
| OpTC H051 learned | 0.798 | 0.808 +- 0.009 | 0.81 |
| OpTC H501 triage | 0.905 | 0.906 +- 0.006 | 0.91 |
| eight-host mean learned | 0.514 | 0.515 | 0.52 |
| FiveDirections triage (Sec. Metrics, tab:orig) | 0.183 / 0.186 | 0.200 +- 0.008 | 0.20 |

The eight-host mean triage ADP (0.669, paper 0.67) and every other ADP in tab:adp and tab:orig agree.

## What is in `records/`

Each directory is one experiment. Every directory holds its protocol (`PROTOCOL.md`, written before the run it
governs; decision records are appended there), its scripts, and its results.

| directory | version / experiment | paper |
|---|---|---|
| `benchmark_e3`, `benchmark_optc` | 0.2-0.5 on E3 CADETS/THEIA and OpTC (five runs each) | tab:versions, App. "Five-run results" |
| `lab_v04` ... `lab_v08` | development labs and decision records of 0.4-0.8 | tab:versions, tab:heldout |
| `benchmark_heldout` | held-out runs of 0.5/0.6 (E3 ClearScope, FiveDirections), 0.7 (TRACE, ATLASv2), 0.8 (CARBANAKv2, E5 THEIA) | tab:heldout |
| `heldout_v08`, `heldout_v09` | held-out preparation logs (CARBANAKv2 and E5 THEIA; E5 ClearScope) | Sec. Method |
| `heldout_prep_manifests` | per-host preparation manifests of the 9 hosts built by the preparation step (split rule, host partition key, event-type counts, ground-truth projection) | tab:datasets, EDR conversion |
| `lab_v09` | 0.8.1 and 0.9 grids and decision record (per-host results of 0.7 released, 0.8.1 and the 0.9 candidates) | tab:lab, tab:layers |
| `lab_v10` | 0.10: fleet prevalence and grouping grid, **alert rows of 0.9 and 0.10 on the 16 development sets** (`results/rows13-*.json.gz`), incidents, ADP, end-to-end replay | tab:lab, tab:layers, tab:ablation, tab:evidence, tab:adp, tab:replay |
| `heldout_v10` | 0.10 held-out run on E5 ClearScope (protocol committed before scoring; alert rows) | tab:heldout |
| `lab_paper5` | five training runs of 0.10 on all 17 sets (16 development sets and held-out E5 ClearScope; 85 runs) | Sec. RQ1 "Training runs" |
| `lotl_paper` | living-off-the-land counterfactual (renaming, laundering) and the bootstrap (alert rows per transformation) | Sec. RQ2 bootstrap, Sec. RQ4 |
| `baselines_paper` | original ProvFusion, Velox and ORTHRUS on the 8 hosts without published results, the store-to-PIDSMaker conversion, node scores, and anchoring of their alerts | tab:orig, Sec. RQ1/RQ4 |
| `paper_analysis` | ADP under random tie order (`adp_random_ties.*`), deterministic evidence per attack (`evidence13.*`) | tab:adp, tab:evidence |
| `maturity` | detection by baseline length: models trained on the first 1 h / 6 h / 1 d / 3 d and on the whole baseline of the seven original DARPA hosts (0.10 + one alert per file version; protocol committed before the run, see its README) | App. D, tab:maturity |
| `paper_v19` | the latest release (0.19) and the identity option on all 17 sets, with 0.10 re-scored in the same pass (protocol committed before the run; per-set results, alert rows, incidents with the 0.10 and current grouping, per-node ADP arrays) | App. E, tab:latest |
| `paper_v19_seeds` | 0.10, 0.19 and the identity option over five training runs: run 1 = `paper_v19`, runs 2-5 = 68 new trainings with the seeds of `lab_paper5` (protocol committed before them; per-run results, incidents with the 0.10 and current grouping, random-tie ADP, training records; alert rows are not included, the per-run totals are recomputable from `res-*.json` and `inc010-*.json`) | App. E, tab:latest |

**Alert row format** (`rows13-*.json.gz`, `rows5-*.json.gz`, `ho10rows-*.json.gz`, `lotl_paper/results/rows/*`):
`{"set", "days", "attacks", "rows": {variant: [row, ...]}, "ctx": {ctx_id: {"nodes": [...], "edges": [...]}}}`.
Each row is one alert the agent reports: node id, type, label, layer (`novelty` = layer 1, `rules` = layer 2,
`corroborated` = anchored learned corroboration, `learned` = learned-only), rule, reason, window, and a pointer into
`ctx`. `ctx` is the one-hop provenance context the agent stores with the alert: the alerted node, its neighbours in
the alert's window, and the edges between them (time, operation). Real-time duplicates of a layer-1/2 alert within 2 h
are not repeated. In `lab_v10`, variant `P0` is the 0.9 configuration and `P2` is 0.10 (fleet prevalence, drop mode,
k=2). In `heldout_v10`, `R` / `A` / `N` are 0.7 released / 0.8.1 / 0.9 = 0.10.

**Per-node ranking arrays** (`data/v0.10_nodes/nodes-<host>.npz`). There is one entry per test node of the host,
alerted or not: `tier` (alert severity of 0.10's triage order, 0 = not alerted), `sc` (final learned score, clipped as
in the triage key), `label` (ground-truth node), `att` (its attacks, `;`-separated). The triage key is
`tier * 1e6 + sc`. These arrays come from a re-scoring pass of version 0.10's run-1 bundles (`baselines_paper/scripts/anchor13.py`
with `--nodes`), which reproduced the run-1 operating point and ADP exactly on every host. They carry the labels but no
node ids. The script checks them against the alert rows: the alerted nodes and alerted ground-truth nodes agree with
the rows joined to the public ground truth on every host.

**Scripts that need the engine.** Many record scripts (`eval*.py`, `adp13.py`, `inc13.py`, `heldout*.py`,
`anchor13.py`, `lotl13.py`, `replay10.py`, ...) import `pdp_engine` or `pdp_server`. They are kept as records of
exactly what was run. They need the unreleased engine and cannot be run from this artifact. Paths in them and in the
logs were anonymised to placeholders: `<DATA>`, `<WORK>`, `<SCRATCH>`, `<ENGINE_REPO>`, `<PIDSMAKER>`,
`<PROVFUSION>`, `<HOME>`. The recomputation below needs none of them.

## Map: every table and figure

"Recompute" refers to the section number printed by `recompute/recompute.py`.

| label | what | files | how to recompute |
|---|---|---|---|
| fig:pipeline | architecture figure (agent layers 1-2, learned detectors, policy, server) | `docs/DETECTION_LAYERS.md` (design of each layer and version) | a diagram with no data |
| tab:sota | published results of other systems (Bilot et al. Tables 4-6, ProvFusion, cited papers) | none (numbers taken from the cited papers) | from the cited papers |
| tab:datasets | hosts, splits, attacks, ground-truth nodes | `recompute/hosts.json`, `records/heldout_prep_manifests/*/*/manifest.json` (splits and split rules of the prepared hosts), `records/lab_v10/results/res13-*.json` (`gt_nodes`, `days`), `docs/BENCHMARK_E3.md`, `docs/BENCHMARK_OPTC.md` (native PIDSMaker splits) | read off; the attack counts and host-days are checked in recompute [1] |
| tab:adp | STRATA columns: triage and learned-score ADP (random tie order), precision, TP / FP (attacks) | ADP: `data/v0.10_nodes/nodes-*.npz` (`paper_analysis/adp_random_ties.*` = the authors' run); TP / FP / attacks: `records/lab_v10/results/rows13-*.json.gz`, `records/heldout_v10/results/ho10rows-CLEARSCOPE_E5.json.gz`; ORTHRUS / Velox / best-of-nine / ProvFusion columns: the cited papers | recompute [4] (ADP, means 0.67 / 0.52) and [1], [6] (TP / FP) |
| tab:orig | original ProvFusion / Velox / ORTHRUS on 8 hosts; STRATA 0.10 columns | `records/baselines_paper/results/summary.{json,md}` (from the per-run `results/*.json` with `scripts/summarize.py`, numpy only), node scores `records/baselines_paper/scores/*.csv.gz`; STRATA: rows13 + `data/v0.10_nodes` | baseline columns: `python3 records/baselines_paper/scripts/summarize.py` (Python >= 3.12, standard library only; rewrites `results/summary.{json,md}` from the per-run `results/*.json`; verified byte-identical); STRATA columns: recompute [10] |
| tab:lab | 0.7 released, 0.8.1, 0.9, 0.10 on the 16 development sets | 0.9 / 0.10: `records/lab_v10/results/rows13-*.json.gz` (P0 / P2); 0.7 / 0.8.1: `records/lab_v09/res9-*.json` (variants R / A; per-host results only) | recompute [1], [2] (0.9 / 0.10 incl. incidents) and [7] (0.7 / 0.8.1) |
| tab:heldout | every held-out run | 0.4: `records/lab_v04/final-OPTC_H051.json`, `final-OPTC_H501.json`, `docs/BENCHMARK_OPTC.md` "0.4"; 0.6: `records/benchmark_heldout/eval-{clearscope,fivedirections}-v0{5,6}.json`, `docs/BENCHMARK_HELDOUT.md` "0.6"; 0.7: `records/benchmark_heldout/eval-TRACE_E3-trace-v07.json`, `eval-ATLASV2_EDR-h{1,2}-v07.json`, `records/lab_v07/PROTOCOL.md`; 0.8: `records/benchmark_heldout/eval-CARBANAKV2_EDR-h*-v08.json`, `eval-THEIA_E5-theia-v08.json`, `records/lab_v08/PROTOCOL.md`, `docs/BENCHMARK_HELDOUT.md` "0.8"; 0.10: `records/heldout_v10/` (rows) | 0.10 row: recompute [6]; earlier rows: per-host results only (read off the JSON files) |
| tab:ablation | what each layer adds | rows13 (layer 1, + fleet prevalence, 0.10); layers 1-2: `records/lab_paper5/results/res5-*-r1.json` (`layers12_only`, a separately run configuration) | recompute [1] and [5] |
| tab:layers | alerted nodes by first layer | 0.9 / 0.10: rows13; 0.7 / 0.8.1: `records/lab_v09/res9-*.json` (`by_layer`, `by_layer_tp`) | recompute [1] and [7] |
| tab:evidence | strongest deterministic evidence per attack | rows13 (P2) with their one-hop context; `records/paper_analysis/evidence13.py` is the authors' script (no engine needed: `python3 evidence13.py ../lab_v10/results`) | recompute [3] |
| tab:replay | end-to-end replay through the deployed agent vs. the lab | `records/lab_v10/results/replay/compare10.json`, `README.md`, `logs/`; lab side = rows13 | recompute [11] (per-host results; see "Not included") |
| tab:versions | versions, changes and reasons | decision records in `records/lab_v0*/PROTOCOL.md`, `records/lab_v10/PROTOCOL.md`, `docs/DETECTION_LAYERS.md`; reasons: 0.2 THEIA 0.73-1.00 and the 25,378-FP run: `records/benchmark_e3/eval-theia-default.json`, `docs/BENCHMARK_E3.md`; 251 `PING.EXE` alerts: `docs/BENCHMARK_OPTC.md`, `docs/DETECTION_LAYERS.md` "0.4"; detector-1 CADETS ADP 0.008: `docs/DETECTION_LAYERS.md` "0.5", `records/lab_v05`; 3,511 corroborated FPs: `records/benchmark_heldout/eval-CARBANAKV2_EDR-h1-v08.json`, `records/lab_v09/anat-CARBANAKV2_EDR-h1.json`; learned-only 0.6 %: `records/lab_v09/PROTOCOL.md` grid 1 (`res10-*.json`) | read off |
| tab:prereg | order of protocol and results in version control | `records/PREREGISTRATION_TIMELINE.tsv` (UTC commit time, A(dded)/M(odified), path), e.g. `records/lab_v08/PROTOCOL.md` added 2026-11-08 10:39, `records/heldout_v10/PROTOCOL.md` 2026-11-09 10:49 and its results 13:00 | read off (see note below) |
| tab:maturity | attacks and FP nodes by baseline length (7 DARPA hosts) | `records/maturity/*-early.json`, `*-full.json`, `summary.json` | sum `rules_only` and `product` over the seven hosts per level (`records/maturity/README.md`) |
| tab:latest | 0.10 / 0.19 / identity option over five training runs on 16 development sets, 8 ADP hosts, E5 ClearScope | `records/paper_v19_seeds/results/SUMMARY.md` from `res-*-rR.json`, `inc010-*-rR.json` (0.10 grouping), `adp_rand.json`; run 1 from `records/paper_v19/results` | `python3 records/paper_v19_seeds/scripts/summ19s.py records/paper_v19_seeds/results records/paper_v19/results records/lab_paper5/results` (stdlib) |

Numbers in the text that are not in a table:
- **Five training runs** (Sec. RQ1): recompute [5] uses `records/lab_paper5/results/res5-*.json`, and recomputes TP / FP / attacks per run from `rows/rows5-*.json.gz`, and the 16-set totals per run (attacks, FP, incidents and false incidents with the incident re-implementation) quoted after tab:lab. The summary written during the experiment is `records/lab_paper5/results/SUMMARY.md`.
- **Bootstrap intervals** (Sec. RQ2): recompute [8] (the authors' version is `records/lotl_paper/scripts/bootstrap.py`, `results/bootstrap.md`).
- **Living off the land** (Sec. RQ4): recompute [9] from `records/lotl_paper/results/rows/`. The protocol is `records/lotl_paper/PROTOCOL.md` and the authors' summary is `results/lotl.md`.
- **Anchoring the original detectors** (Sec. RQ4): `records/baselines_paper/results/anchoring_summary.{json,md}` and `anchoring/`. These were produced with the engine (`anchor13.py`) and are per-host results.
- **Re-running ProvFusion and its tie order** (Sec. RQ1): `records/baselines_paper/results/provfusion_*.json`, `*_printed.txt`, `strata_ties.md`, `PROGRESS.md`.
- **App. "Five-run results of earlier versions"**: `records/benchmark_e3/eval-*-v04.json`, `records/benchmark_optc/eval-optc-*-v04.json`, `docs/BENCHMARK_E3.md`, `docs/BENCHMARK_OPTC.md`.

## The items promised in the Data Availability statement

1. **Protocols and decision records of every version.** Versions 0.4-0.10: `records/lab_v04` ... `lab_v10`, `records/heldout_v10`, `records/lab_paper5`, `records/lotl_paper` and `records/baselines_paper`, each in its `PROTOCOL.md`, with the decision record appended after the results. Versions 0.2-0.3 have no separate record directory; their methods (including what was fixed before test results) and results are in `docs/BENCHMARK_E3.md` and `docs/BENCHMARK_OPTC.md` ("fusion calibration by simulation, method fixed before any test result", "0.3 layered detection") and in `docs/DETECTION_LAYERS.md` ("Pre-registration and the one revision"). The order of protocol and results in version control is in `records/PREREGISTRATION_TIMELINE.tsv`.
2. **Held-out preparation logs.** `records/heldout_v08/PREP_LOG.md` (CARBANAKv2, E5 THEIA), `records/heldout_v09/PREP_LOG.md` (E5 ClearScope), their scripts and surveys, `records/heldout_prep_manifests/` and `docs/BENCHMARK_HELDOUT.md` (TRACE, ATLASv2, E3 ClearScope, FiveDirections). The preparation step ran no detector.
3. **Scoring scripts.**
   - ADP implementation: `adp_curve` in `recompute/recompute.py` (PIDSMaker's ADP, Bilot et al. Eq. 1), also in `records/paper_analysis/adp_random_ties.py`.
   - Incident analysis: `incidents()` / `group()` in `recompute/recompute.py`. This re-implements the 0.10 incident grouping from its specification (paper, Sec. "Incidents"), with the parameters the deployed server uses: a 30-min gap; connectivity through the alerts' one-hop context, where a context node of degree > 8, a node without a recorded name, or a DNS flow (port 53) does not connect; unconnected parts without a rule alert are kept together by acting program; and, in 0.10, recurrence of the same finding within 7 days. It reproduces the lab's incident counts exactly (recompute [2], [6]).
   - Evidence analysis: recompute [3] and `records/paper_analysis/evidence13.py`.
   - Per-version node-level scoring: `node_level()` in `recompute/recompute.py`.
4. **Per-host results.** `res*.json` and `eval-*.json` in each record directory. Per set and variant they hold TP, FP, attacks found, FP per day, alerts by layer and ADP.
5. **Alert rows with their one-hop context.** These exist for 0.9 and 0.10 on the 16 development sets (`records/lab_v10/results/rows13-*`), for 0.7 released / 0.8.1 / 0.10 on held-out E5 ClearScope (`records/heldout_v10/results/ho10rows-*`), for all 85 runs of the five-run experiment (`records/lab_paper5/results/rows/`), and for the four LotL transformations (`records/lotl_paper/results/rows/`). See "Not included" for the tables without rows.
6. **Conversion of the EDR datasets into hosts.** The method is in the paper (Sec. Datasets). The prepared hosts are documented in `records/heldout_prep_manifests/` (host partition key = dominant local address of the component's flows, event-type counts per day, ground-truth nodes found per host and why the others were not found). The commands that built each host are in `records/heldout_v08/scripts/build_carb.sh`, and `records/heldout_v08/PREP_LOG.md` lists the 5 attributed components and 18,834 unattributed ones. The mapping of the 33 Carbon Black event types is described in `build_carb.sh` (NOTES) and `records/baselines_paper/CONVERSION.md`. `records/baselines_paper/scripts/conv_store.py` converts the prepared hosts into PIDSMaker's database schema (for the baselines). See "Not included" for the conversion code itself.

## Not included, or only partly reproducible without the engine

- **Detection engine and server** (agent, layers, learned detectors, alert policy, incident server, console): not released, as stated in the paper.
- **EDR-to-host conversion code.** The component partition and the Carbon Black event-type mapping are implemented in the unreleased engine/server tree (`pdp_server.tools.heldout_prep partition|build --edr`, called by `build_carb.sh`). This artifact documents the conversion and its outputs but does not contain runnable conversion code.
- **Alert rows for 0.7 released, 0.8 and 0.8.1** on the development sets, and for the held-out runs of 0.4-0.8. Only per-host results were kept (`records/lab_v09/res9-*.json`, `records/benchmark_heldout/*.json`, `records/lab_v04`, `records/benchmark_optc`). The tab:lab rows 0.7 / 0.8.1, the tab:layers columns 0.7 / 0.8.1 and the first five rows of tab:heldout therefore cannot be recomputed from alert rows, only re-summed from per-host results.
- **Replay-side alert rows** (tab:replay). The replay's alerts live in the deployed system's database. Only the per-host comparison (`compare10.json`, with the Jaccard values in `README.md`) is included.
- **Per-node rankings of five-run runs 2-5.** These were not kept, so the five-run ADP ranges use the recorded per-host ADP values (node-id tie order), as the paper states.
- **Per-node rankings of the authors' 500-order random-tie run.** The authors' arrays (`scores5-*.npz`) were not preserved. The artifact's `data/v0.10_nodes` arrays come from an equivalent re-scoring pass of the same bundles and give the same values within random-order noise (recompute [4]).
- **Layers 1-2 alone** (tab:ablation, 21 / 290 / 791). This is a separately run configuration. It is re-summed from per-host results (`res5-*-r1.json`, `layers12_only`).
- **One redaction.** A process command line in the public CARBANAKv2 data (host h3, a `git clone` on the emulated victim) contains a GitHub-token-shaped string. It is replaced by `ghp_REDACTED` in `records/lab_paper5/results/rows/rows5-CARBANAKV2_EDR-h3-r2.json.gz`; it is part of a node label and affects no number.
- **Client attack suite** files (`benchmark_e3/client-suite-*`). Product acceptance tests not used in the paper; omitted.
- **Later product versions (0.11-0.13)**, which the paper does not cover; omitted.

**Version-control history.** The repository history (author names, e-mails, commit messages) was removed for
anonymity. `records/PREREGISTRATION_TIMELINE.tsv` keeps, for every record file, the UTC commit time at which it was
added or modified. Paths were rewritten from `artifacts/` to `records/`. The full history can be made available to
the program chairs.
