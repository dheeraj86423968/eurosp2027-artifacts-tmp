"""paper_v19 summary (artifacts/paper_v19/PROTOCOL.md): per-set and total results of V10 / V19 / V19id from
evalp.py (res-*.json), inc13.py (inc.json) and adp_ties.py (adp_rand.json). Usage: summp.py OUTDIR > SUMMARY.md"""
import json, os, sys
D = sys.argv[1]
DEV = ["CADETS_E3", "THEIA_E3", "CLEARSCOPE_E3", "FIVEDIRECTIONS_E3", "TRACE_E3-trace", "THEIA_E5-theia", "OPTC_H201", "OPTC_H501",
       "OPTC_H051", "ATLASV2_EDR-h1", "ATLASV2_EDR-h2", "CARBANAKV2_EDR-h1", "CARBANAKV2_EDR-h2", "CARBANAKV2_EDR-h3",
       "CARBANAKV2_EDR-h4", "CARBANAKV2_EDR-h5"]
PUB8 = ["CADETS_E3", "THEIA_E3", "CLEARSCOPE_E3", "THEIA_E5-theia", "CLEARSCOPE_E5-clearscope-3att", "OPTC_H051", "OPTC_H201", "OPTC_H501"]   # paper tab:adp
HO = "CLEARSCOPE_E5-clearscope"
V = ["V10", "V19", "V19id"]
res = {s: json.load(open(f"{D}/res-{s}.json")) for s in DEV + [HO]}
inc = json.load(open(f"{D}/inc010.json"))           # the paper's grouping (pdp_server.incidents at 70b6a57, 0.10)
inc_now = json.load(open(f"{D}/inc.json"))         # the grouping of the code at 500eaa3 (0.11 review digest)
adpr = json.load(open(f"{D}/adp_rand.json")) if os.path.exists(f"{D}/adp_rand.json") else {}
key = lambda v: f"{v}/G0"

print("## Per set (attacks found / deterministic-alone, TP, FP, false incidents)\n")
print("| set | " + " | ".join(V) + " |\n|---|" + "---|" * len(V))
for s in DEV + [HO]:
    cells = []
    for v in V:
        r = res[s][v]; i = inc[s][key(v)]
        cells.append(f"{r['attacks']}/{len(r['attacks_det'])}, {r['TP']}, {r['FP']}, {i['fp_incidents']}")
    print(f"| {s} | " + " | ".join(cells) + " |")

print("\n## 16 development sets\n")
print("| version | attacks | det-alone | TP | FP | precision | alert rows | false incidents | per host-day | buried |\n|---|---|---|---|---|---|---|---|---|---|")
days = sum(inc[s]["days"] for s in DEV)
tot = {}
for v in V:
    att = sum(res[s][v]["attacks"] for s in DEV); det = sum(len(res[s][v]["attacks_det"]) for s in DEV)
    tp = sum(res[s][v]["TP"] for s in DEV); fp = sum(res[s][v]["FP"] for s in DEV); rows = sum(res[s][v]["rows"] for s in DEV)
    fi = sum(inc[s][key(v)]["fp_incidents"] for s in DEV); bur = sum(len(inc[s][key(v)]["buried"]) for s in DEV)
    tot[v] = dict(attacks=att, det=det, TP=tp, FP=fp, rows=rows, fi=fi)
    print(f"| {v} | {att} | {det} | {tp} | {fp:,} | {tp / max(1, tp + fp):.3f} | {rows:,} | {fi} | {fi / days:.2f} | {bur} |")
print("\nFalse items under the current product grouping (0.11 digest): " + ", ".join(f"{v} {sum(inc_now[s][key(v)]['fp_incidents'] for s in DEV)} ({sum(inc_now[s][key(v)]['fp_incidents'] for s in DEV) / days:.2f}/day)" for v in V))
print(f"\nhost-days: {days}. Published 0.10 (paper tab:lab): 26 attacks, 21 deterministic-alone, TP 333, FP 1,051, 178 false incidents (2.51/day).")
lost = {v: sorted({(s, x) for s in DEV for x in res[s]["V10"]["attacks_found"]} - {(s, x) for s in DEV for x in res[s][v]["attacks_found"]}) for v in V}
gain = {v: sorted({(s, x) for s in DEV for x in res[s][v]["attacks_found"]} - {(s, x) for s in DEV for x in res[s]["V10"]["attacks_found"]}) for v in V}
for v in V[1:]:
    print(f"{v}: attacks lost vs V10 {lost[v]}; gained {gain[v]}")

print(f"\n## Held-out E5 ClearScope (second scoring of the host; held-out for 0.11-0.19)\n")
for v in V:
    r = res[HO][v]; i = inc[HO][key(v)]
    print(f"- {v}: attacks {r['attacks']}/{res[HO]['n_attacks']}, TP {r['TP']}, FP {r['FP']}, false incidents {i['fp_incidents']} ({i['fp_inc_per_day']}/day)")
print("Published 0.10 held-out: 2/2 attacks, TP 4, FP 15, 6 false incidents.")

if adpr:
    print("\n## ADP of the triage order, random tie order (500 permutations)\n")
    print("| set | " + " | ".join(V) + " |\n|---|" + "---|" * len(V))
    for s in PUB8 + ["FIVEDIRECTIONS_E3", "TRACE_E3-trace"]:
        if s in adpr:
            print(f"| {s} | " + " | ".join(f"{adpr[s][v]['rand']:.2f}" for v in V) + " |")
    for v in V:
        m = sum(adpr[s][v]["rand"] for s in PUB8 if s in adpr) / len([s for s in PUB8 if s in adpr])
        print(f"mean over the eight published DARPA hosts, {v}: {m:.3f}")
    print("Published 0.10 (paper tab:adp): eight-host mean 0.67.")
