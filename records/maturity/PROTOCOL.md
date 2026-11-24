# Detection over time from the start (written 2026-11-15, before any run)

Question (user, 2026-11-15): how effective is the detector as time progresses from installation? Two parts:

## A. Live client endpoint (false alarms over time)
A fresh Ubuntu 24.04 server `livehost` (VM vm-A, 4 vCPU / 6 GB), set up like a small client's web server
before the agent: nginx -> Python orders API -> PostgreSQL, cron (nightly pg_dump, 10-minute health check, hourly
stats), Ubuntu's unattended upgrades left on. Customer traffic from outside (busier 08-20 UTC). Agent installed
with the console's one-line installer into a new organisation "Client Simulation (livehost)" on the production
service, default settings (agent 0.14.1, server v16). Enrolled 2026-11-15 17:51:45 UTC.
Scheduled benign admin activity (host timers, logged in /var/lib/pdp-live/journal.txt): a routine check once a
day at varying hours; app deploy 1.1.0 (11-17 14:00), new package + new cron job (11-18 09:30), deploy 1.2.0 with an
nginx change (11-20 15:00), a debugging session calling an outside API (11-21 11:20, again 11-24 10:00), deploy
1.3.0 after protection (11-24 14:00).
**No attacks are run on this host** (the user ruled out attack simulation). Every alert is a false alarm; alerts
during a logged admin action are reported as "caused by a real change", the rest as "unexplained".
Reported per day and per model (early 1 h / 6 h / daily, final): alerts, incidents, by layer and rule; agent health
(event loss, CPU/memory), install time. Snapshots hourly in /var/lib/pdp-live/snapshots.jsonl; alerts from the
platform database at the end.

## B. Recorded attacks (detection over time)
Attacks cannot be run live, so detection over time is measured on the seven original DARPA benchmark hosts
(CADETS_E3, THEIA_E3, CLEARSCOPE_E3, FIVEDIRECTIONS_E3, OPTC_H201, OPTC_H501, OPTC_H051) with
`pdp_server.tools.maturity_eval darpa`: a model is trained on only the first 1 h / 6 h / 1 d / 3 d of the recorded
baseline (the product's early-model split: last quarter calibrates), and with the full baseline; the same attack
days are scored with each (ORTHRUS ground truth). Code: server v16 (= detection 0.13 defaults) plus two additions to
the tool made before any run: the endpoint's own training settings are passed (as the worker does) and a
`rules_only` result is reported, because below one day the product alerts from the data-flow rules only
(pdp_server.early). Reported per level: attacks detected, TP / FP of what the product would alert at that maturity
(rules only below 1 d; all layers from 1 d), and of every layer.
Scope limits, stated in advance: per-host runtime alerting only (no fleet prevalence, no incident grouping, unlike
the lab harness), so absolute FP numbers are not comparable to the paper's 1,051; the curve across levels is the
result. These hosts are development sets (seen), so this measures how detection grows with baseline time, not
generalisation. Measurement only: no product change is made because of these results.
