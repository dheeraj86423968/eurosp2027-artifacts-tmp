# paper_v19_seeds progress log

- 2026-11-16 14:27 UTC: lanes 1-2 and the scorer started (68 trainings queued, run-major).
- 2026-11-16 17:30 UTC: harness fault, fixed: the work directory's 0.10 incident code (code010) was a symlink to a path
  outside the container mount, so the 0.10 grouping (inc010-*.json) failed with ModuleNotFoundError for the first scored
  bundle (THEIA_E5 run 2); the current-grouping file was fine. Replaced by a copy of the same tree (git archive 70b6a57)
  and re-ran the 0.10 grouping on THEIA_E5 run 2's stored rows (no re-scoring needed; result 28 false incidents for
  each version, as run 1). summ19s.py flags any empty incident file.
- 2026-11-16 21:47 UTC: run 2 complete (all 17 sets). 2026-11-17 06:30 UTC: run 3 complete.
- Note on ADP: adp_ties.py (paper_v19, unchanged) draws the random tie orders from one generator (seed 0) across all
  score files in name order, so an interim recomputation with more files present gives slightly different values for
  the same run (run 2 V10 0.675 at 2 runs, 0.673 at 3 runs: Monte Carlo error of the 500-permutation mean, ~0.002).
  The reported ADPs are the one computation over all completed runs' files at the end; interim values are superseded.
- 2026-11-17 12:3x UTC: run 4 complete; 19:47 UTC: run 5 complete; scorer finished. 68/68 trainings, no failure; every new
  bundle's layers.json equals run 1's; 52.0 GPU-hours of training. Final ADP (adp_ties.py over all runs' files) and
  SUMMARY.md computed 11-17 ~20:00-00:15 UTC.
- Corrections to PROTOCOL.md's text (the file itself is left as committed): (1) it says "Written 2026-11-16 ~14:45 UTC";
  that time was an estimate and is wrong - the commit (53261de) is 14:25:36 UTC, the harness commit (3cb32e5) 14:27:04,
  the first training start 14:27:04 (lane log). (2) The 23:30-00:45 UTC pause in starting trainings was meant to leave
  the GPU to livehost's daily model, assumed at ~00:05 UTC; livehost's models follow recorded hours (its 1-day model
  trained 11-16 18:15 alongside two of these trainings, in 152 s). The pause was kept as registered; it changes no result.
