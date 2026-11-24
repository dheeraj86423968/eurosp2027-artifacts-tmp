# Detection by baseline length (paper Appendix D, Table 13)

Protocol (`PROTOCOL.md`, part B; committed 2026-11-15 17:53:16 UTC; the run was launched by the same script right after the commit, its first
model fit started 17:53:18): on the seven original DARPA hosts (E3 CADETS, THEIA, ClearScope, FiveDirections; OpTC
201, 501, 051; ORTHRUS ground truth) train a model on only the first 1 h / 6 h / 1 d / 3 d of the recorded baseline
(the last quarter calibrates, as for the engine's early models) and on the whole baseline; score the same attack days
with each. Configuration: 0.10 plus one change (an untrusted file alerts once per content version). Reported per level:
attacks detected and TP/FP nodes of what the engine would alert at that age (layer-2 rules only below one day, all
layers from one day: `product`), of the rules alone (`rules_only`) and of all layers (`product` from 1 d; for 1 h and
6 h the all-layer figures are `product` too, computed but not alerted by the engine at that age), plus per layer.
Per-host alerting only: no fleet prevalence, no incident grouping, so FP is not comparable to Table 5. These are
development hosts: the result is how detection grows with baseline time, not generalisation. Results committed
2026-11-16 03:56:42 UTC.

Files: `<host>-early.json` (levels 1h, 6h, 1d, 3d) and `<host>-full.json` (full baseline); `summary.json` (Table 13
totals). `CADETS_E3-early.json` holds the four level rows the tool printed in its log (its own JSON could not be
written on that first run: the output directory was not writable; fixed before the next host).

Table 13 from these files: for each level sum `attacks_detected` and `FP` over the seven hosts, of `rules_only`
("Layer-2 rules only") and of `product` ("All layers"; at 1 h and 6 h `product` is the all-layer result).
