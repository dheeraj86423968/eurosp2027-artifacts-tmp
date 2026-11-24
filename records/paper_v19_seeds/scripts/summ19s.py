"""paper_v19_seeds summary (PROTOCOL.md "Reporting"). Run 1 = artifacts/paper_v19 results; runs 2-5 = OUT (score19.sh,
adp_ties.py). V10 of runs 2-5 is also compared with lab_paper5's run-r P2/G2 numbers (same seeds, earlier trainings).
Usage: summ19s.py OUT RUN1_RESULTS LAB_PAPER5_RESULTS > SUMMARY.md   (stdlib only)"""
import json, os, statistics as st, sys
OUT, R1, P5 = sys.argv[1:4]
DEV = ["CADETS_E3", "THEIA_E3", "CLEARSCOPE_E3", "FIVEDIRECTIONS_E3", "TRACE_E3-trace", "THEIA_E5-theia", "OPTC_H201", "OPTC_H501",
       "OPTC_H051", "ATLASV2_EDR-h1", "ATLASV2_EDR-h2", "CARBANAKV2_EDR-h1", "CARBANAKV2_EDR-h2", "CARBANAKV2_EDR-h3",
       "CARBANAKV2_EDR-h4", "CARBANAKV2_EDR-h5"]
PUB8 = ["CADETS_E3", "THEIA_E3", "CLEARSCOPE_E3", "THEIA_E5-theia", "CLEARSCOPE_E5-clearscope-3att", "OPTC_H051", "OPTC_H201", "OPTC_H501"]
HO = "CLEARSCOPE_E5-clearscope"
V = ["V10", "V19", "V19id"]
RUNS = [1, 2, 3, 4, 5]
J = lambda p: json.load(open(p)) if os.path.exists(p) and os.path.getsize(p) > 0 else None

r1_res = {s: J(f"{R1}/res-{s}.json") for s in DEV + [HO]}
r1_inc = J(f"{R1}/inc010.json"); r1_adp = J(f"{R1}/adp_rand.json") or {}
adp_n = J(f"{OUT}/adp_rand.json") or {}


def res(s, r):
    return r1_res[s] if r == 1 else J(f"{OUT}/res-{s}-r{r}.json")


def inc(s, r):
    if r == 1:
        return r1_inc.get(s)
    d = J(f"{OUT}/inc010-{s}-r{r}.json")
    return d.get(s) if d else None


def adp(s, r, v):
    d = r1_adp.get(s) if r == 1 else adp_n.get(f"{s}-r{r}")
    return d[v]["rand"] if d and v in d else None


def complete(r):
    return all(res(s, r) and inc(s, r) for s in DEV)


done = [r for r in RUNS if complete(r)]
partial = {r: sum(1 for s in DEV + [HO] if res(s, r) and inc(s, r)) for r in RUNS if r not in done}
days = sum(inc(s, 1)["days"] for s in DEV)
print(f"# paper_v19_seeds results\n\nComplete runs (all 16 development sets scored): {done}. Partial: "
      + (", ".join(f"run {r}: {n}/17 sets" for r, n in partial.items()) or "none") + f". Host-days: {days}.\n")
empty = [f for f in os.listdir(OUT) if f.startswith("inc") and os.path.getsize(f"{OUT}/{f}") == 0]
if empty:
    print(f"**Empty incident files (re-run needed): {empty}**\n")


def totals(r, v):
    t = dict(attacks=0, det=0, TP=0, FP=0, fi=0)
    for s in DEV:
        x = res(s, r)[v]; i = inc(s, r)[f"{v}/G0"]
        t["attacks"] += x["attacks"]; t["det"] += len(x["attacks_det"]); t["TP"] += x["TP"]; t["FP"] += x["FP"]; t["fi"] += i["fp_incidents"]
    a = [adp(s, r, v) for s in PUB8]
    t["adp8"] = sum(a) / 8 if all(x is not None for x in a) else None
    return t


K = [("attacks", "attacks"), ("det", "det-alone"), ("TP", "TP"), ("FP", "FP"), ("fi", "false incidents"), ("adp8", "ADP (8 hosts)")]
f = lambda x, k: "-" if x is None else (f"{x:.3f}" if k == "adp8" else f"{x:,}")
T = {(r, v): totals(r, v) for r in done for v in V}
print("## 16 development sets, per run\n\n| run | version | " + " | ".join(n for _, n in K) + " | per host-day |\n|---|---|" + "---|" * (len(K) + 1))
for r in done:
    for v in V:
        t = T[(r, v)]
        print(f"| {r} | {v} | " + " | ".join(f(t[k], k) for k, _ in K) + f" | {t['fi'] / days:.2f} |")

print(f"\n## Over the {len(done)} complete runs: mean (sd) [min-max]\n\n| version | " + " | ".join(n for _, n in K) + " |\n|---|" + "---|" * len(K))
for v in V:
    cells = []
    for k, _ in K:
        xs = [T[(r, v)][k] for r in done if T[(r, v)][k] is not None]
        if not xs:
            cells.append("-"); continue
        sd = st.stdev(xs) if len(xs) > 1 else 0.0
        fm = (lambda y: f"{y:.3f}") if k == "adp8" else (lambda y: f"{y:,.1f}" if y != int(y) else f"{int(y):,}")
        cells.append(f"{fm(st.mean(xs))} ({fm(sd) if k == 'adp8' else f'{sd:.1f}'}) [{fm(min(xs))}-{fm(max(xs))}]")
    print(f"| {v} | " + " | ".join(cells) + " |")

print("\n## Paired differences per run (version - V10); 'same sign' = the sign is equal in every complete run\n")
print("| difference | " + " | ".join(n for _, n in K) + " |\n|---|" + "---|" * len(K))
for v in V[1:]:
    cells = []
    for k, _ in K:
        ds = [T[(r, v)][k] - T[(r, "V10")][k] for r in done if T[(r, v)][k] is not None and T[(r, "V10")][k] is not None]
        if not ds:
            cells.append("-"); continue
        sg = {(d > 0) - (d < 0) for d in ds}
        fm = (lambda y: f"{y:+.3f}") if k == "adp8" else (lambda y: f"{y:+,}")
        cells.append(", ".join(fm(d) for d in ds) + (" (same sign)" if len(sg) == 1 else " (sign varies)"))
    print(f"| {v} - V10 | " + " | ".join(cells) + " |")

print("\n## Detected attack sets across runs (16 development sets)\n")
for v in V:
    sets = {r: frozenset((s, a) for s in DEV for a in res(s, r)[v]["attacks_found"]) for r in done}
    u = set().union(*sets.values()) if sets else set(); c = set.intersection(*map(set, sets.values())) if sets else set()
    print(f"- {v}: {len(c)} attacks found in every run, {len(u)} in at least one" + (f"; varying: {sorted(u - c)}" if u != c else ""))

print("\n## Per set: FP (and attacks) per run, runs 1..5 ('.' = not scored yet)\n")
print("| set | " + " | ".join(V) + " |\n|---|" + "---|" * len(V))
for s in DEV + [HO]:
    cells = []
    for v in V:
        cells.append(" ".join(f"{res(s, r)[v]['FP']}/{res(s, r)[v]['attacks']}" if res(s, r) else "." for r in RUNS))
    print(f"| {s} | " + " | ".join(cells) + " |")

print(f"\n## Held-out E5 ClearScope per run (held-out for 0.11-0.19; runs 2-5 are new trainings)\n")
for r in RUNS:
    x = res(HO, r); i = inc(HO, r)
    if x and i:
        print(f"- run {r}: " + "; ".join(f"{v} {x[v]['attacks']}/{x['n_attacks']} attacks, TP {x[v]['TP']}, FP {x[v]['FP']}, false incidents {i[f'{v}/G0']['fp_incidents']}, ADP(3 att) "
                                          + (f"{adp('CLEARSCOPE_E5-clearscope-3att', r, v):.2f}" if adp('CLEARSCOPE_E5-clearscope-3att', r, v) is not None else "-") for v in V))

print("\n## V10 of runs 2-5 vs lab_paper5's run r (same seeds; separate trainings, detector-2 GPU training is not bit-exact)\n")
print("| run | this study: attacks / TP / FP / false incidents | lab_paper5 | sets differing in FP |\n|---|---|---|---|")
for r in RUNS[1:]:
    ss = [s for s in DEV if res(s, r) and inc(s, r) and J(f"{P5}/res5-{s}-r{r}.json")]
    if not ss:
        continue
    a = [sum(res(s, r)["V10"][k] for s in ss) for k in ("attacks", "TP", "FP")] + [sum(inc(s, r)["V10/G0"]["fp_incidents"] for s in ss)]
    b = [sum(J(f"{P5}/res5-{s}-r{r}.json")["P2"][k] for s in ss) for k in ("attacks", "TP", "FP")] + \
        [sum(J(f"{P5}/inc5-{s}-r{r}.json")[s]["P2/G2"]["fp_incidents"] for s in ss)]
    dif = [f"{s} {J(f'{P5}/res5-{s}-r{r}.json')['P2']['FP']}->{res(s, r)['V10']['FP']}" for s in ss
           if J(f"{P5}/res5-{s}-r{r}.json")["P2"]["FP"] != res(s, r)["V10"]["FP"]]
    print(f"| {r} ({len(ss)} sets) | {' / '.join(map(str, a))} | {' / '.join(map(str, b))} | {', '.join(dif) or 'none'} |")
