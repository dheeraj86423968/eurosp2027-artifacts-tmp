#!/usr/bin/env python3
"""Recompute the paper's headline numbers from the released alert rows, per-node ranking arrays and per-host results,
joined with the PUBLIC node-level ground truth (PIDSMaker's Ground_Truth/orthrus CSVs). Needs python3 + numpy only;
does not need (and does not contain) the detection engine.

Usage:
  python3 recompute/recompute.py --gt <PIDSMaker>/Ground_Truth/orthrus [--perms 500] [--out recompute/recomputed.json]

Sections (each prints the recomputed value next to the value printed in the paper, and MATCH / DIFF):
  1. tab:lab, tab:layers, tab:ablation (rows-derivable parts): 16 development sets, 0.9 (variant P0) and 0.10 (P2),
     node level at the operating point, from records/lab_v10/results/rows13-*.json.gz + public ground truth.
  2. Incidents (tab:lab, 0.9: grouping G0; 0.10: grouping G2) from the same rows, with the incident grouping
     re-implemented below from its specification (paper, Sec. "Incidents"; parameters in README).
  3. tab:evidence from the same rows (one-hop context of each alert).
  4. tab:adp, STRATA columns: ADP of the triage order and of the learned score on the eight hosts with published results,
     expected value under a random order within ties, from data/v0.10_nodes/nodes-*.npz (per-node arrays).
  5. Five training runs (Sec. RQ1 "Training runs"): from records/lab_paper5/results/res5-*.json and rows5-*.json.gz.
  6. tab:heldout, last row (0.10 on held-out E5 ClearScope) from records/heldout_v10/results/ho10rows-*.json.gz.
  7. tab:lab rows 0.7 / 0.8.1 and tab:layers columns 0.7 / 0.8.1: no alert rows were kept for these versions; summed
     from per-host results (records/lab_v09/res9-*.json), reported as such.
"""
import argparse, csv, glob, gzip, json, os, re, sys
from collections import Counter, defaultdict

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)
CHECKS = []


def check(name, got, paper, tol=0.0):
    ok = (abs(got - paper) <= tol + 1e-12) if isinstance(paper, (int, float)) and isinstance(got, (int, float)) else got == paper
    CHECKS.append({"check": name, "recomputed": got, "paper": paper, "match": bool(ok)})
    print(f"  {'MATCH' if ok else 'DIFF '}  {name}: recomputed {got}  paper {paper}")


# ------------------------------------------------------------------------------------------------ ground truth
def load_hosts():
    return json.load(open(R("recompute", "hosts.json")))["sets"]


def load_gt(gt_dir, files):
    """{attack: set(node ids)}; a node id is column 3 (index_id) of the ORTHRUS/PIDSMaker CSV (as PIDSMaker reads it)."""
    gt = {}
    for name, rel in files.items():
        ids = set()
        with open(os.path.join(gt_dir, rel), newline="") as f:
            for row in csv.reader(f):
                if len(row) >= 3 and row[2].strip():
                    ids.add(row[2].strip())
        gt[name] = ids
    return gt


def label_rows(rows, gt):
    allgt = set().union(*gt.values()) if gt else set()
    inv = defaultdict(set)
    for a, ids in gt.items():
        for u in ids:
            inv[u].add(a)
    mism = 0
    out = []
    for r in rows:
        g = r["node_uuid"] in allgt
        att = sorted(inv.get(r["node_uuid"], ()))
        if "gt" in r and (bool(r["gt"]) != g or sorted(r.get("attacks", [])) != att):
            mism += 1
        out.append(dict(r, gt=g, attacks=att))
    return out, mism


# ------------------------------------------------------------------------------------------------ node level
def node_level(rows):
    """Alerted nodes = distinct node ids of the rows; each attributed to the layer of its first row (time, id)."""
    first = {}
    for r in sorted(rows, key=lambda r: (r["window_start_ns"], r["id"])):
        first.setdefault(r["node_uuid"], r)
    tp = sum(r["gt"] for r in first.values())
    fp = len(first) - tp
    found = sorted({a for r in first.values() for a in r["attacks"]})
    lay, lay_tp = Counter(), Counter()
    for r in first.values():
        lay[r["layer"]] += 1
        lay_tp[r["layer"]] += r["gt"]
    nov_found = sorted({a for r in first.values() if r["layer"] == "novelty" for a in r["attacks"]})
    nr_found = sorted({a for r in first.values() if r["layer"] in ("novelty", "rules") for a in r["attacks"]})
    return {"TP": tp, "FP": fp, "attacks_found": found, "by_layer": dict(lay), "by_layer_tp": dict(lay_tp),
            "novelty_attacks": nov_found, "novelty_rules_attacks": nr_found}


# ------------------------------------------------------------------------------------------------ incidents
# Re-implementation of the 0.10 incident grouping from its specification (paper Sec. "Incidents"):
# a run of alerts on one endpoint with no gap > 30 min between consecutive alert windows, split into parts that are not
# connected in the alerts' one-hop provenance context (alerted - alerted, or alerted - non-hub context node - alerted;
# a hub is a context node with degree > 8 in the merged context, a node without a recorded name, or a DNS flow (port 53));
# unconnected parts with the same acting program and no rule alert stay together; 0.10 (G2): a part whose finding
# (acting program of its top alert, or the address / name of its node) recurs within 7 days of the last alert of an
# earlier incident on the same endpoint joins that incident; findings without a name never merge.
GAP_NS = 30 * 60 * 10**9
RECUR_7D = 7 * 24 * 3600 * 10**9
HUB_DEGREE = 8
TYPE_RANK = {"rules": 0, "novelty": 1, "corroborated": 2, "evidence": 3, "learned": 4}
RULE_RANK = {"exfiltration": 0, "untrusted_code_network": 1, "untrusted_exec": 2, "novel_executable": 3,
             "tainted_modify": 4, "tainted_spawn": 5, "novel_executable_repeat": 6, "fleet_known_executable": 7}
UNKNOWN = (None, "", "None", "null")
_ACTOR = re.compile(r"^\s*([^,(]+?)(?:, which| \(loaded from)")
_SUBJECT = re.compile(r"^\s*(?:runs\s+)?([^,(]+?)(?:, which|, new on this endpoint| \(loaded from)")


def det_key(a):
    return (TYPE_RANK.get(a["layer"], 9), RULE_RANK.get(a["rule"] or "", 9), a["window_start_ns"])


def short_label(ntype, label, uuid):
    label = label or uuid
    body = label.split(" ", 1)[1] if " " in label else label
    if ntype == "subject":
        parts = body.split(" ", 1)
        exe = parts[0] if parts and parts[0] not in UNKNOWN else None
        cmd = parts[1] if len(parts) > 1 and parts[1] not in UNKNOWN else ""
        m = re.match(r"^proc:[^:]*:(\d+)", uuid)
        pid = m.group(1) if m else None
        return os.path.basename(exe) if exe else (os.path.basename(cmd.split(" ", 1)[0]) if cmd else (f"process {pid}" if pid else "process"))
    if ntype == "netflow":
        p = body.split()
        return f"{p[0]}:{p[1]}" if len(p) >= 2 else body
    if body in UNKNOWN or body == uuid:
        return "unnamed file"
    return os.path.basename(body.rstrip("/")) or body


def actor(reason):
    m = _ACTOR.match(reason or "")
    return os.path.basename(m.group(1).strip()) if m and m.group(1).strip() not in UNKNOWN else None


def finding(g):
    top = min(g, key=det_key)
    m = _SUBJECT.match(top.get("reason") or "")
    if m:
        a = m.group(1).strip().replace("\\", "/").casefold()
        return "process" if a in ("none", "null", "") else a
    return short_label(top["ntype"], top["label"], top["node_uuid"])


def split_connected(g):
    ids = {a["node_uuid"] for a in g}
    adj, lab = defaultdict(set), {}
    for a in g:
        ctx = a.get("context") or {}
        for n in ctx.get("nodes", []):
            lab[n["uuid"]] = n.get("label") or ""
        for e in ctx.get("edges", []):
            adj[e["src"]].add(e["dst"]); adj[e["dst"]].add(e["src"])

    def hub(u):
        l = lab.get(u, "")
        return len(adj.get(u, ())) > HUB_DEGREE or l.split(" ", 1)[-1] in UNKNOWN or l == "file" or l.endswith(" 53")

    parent = {u: u for u in ids}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]; u = parent[u]
        return u

    for u in ids:
        for v in adj.get(u, ()):
            if v in ids:
                parent[find(u)] = find(v)
            elif not hub(v):
                for w in adj.get(v, ()):
                    if w in ids:
                        parent[find(u)] = find(w)
    comps = defaultdict(list)
    for a in g:
        comps[find(a["node_uuid"])].append(a)
    merged = {}
    for c in comps.values():
        if any(a["layer"] == "rules" for a in c):
            key = ("chain", find(c[0]["node_uuid"]))
        else:
            top = min(c, key=det_key)
            key = ("program", actor(top["reason"]) or short_label(top["ntype"], top["label"], top["node_uuid"]))
        merged.setdefault(key, []).extend(c)
    return [sorted(c, key=lambda a: (a["window_start_ns"], a["id"])) for c in merged.values()]


def merge_recurring(groups, horizon):
    out, last = [], {}
    for g in groups:
        sub = finding(g)
        if not sub or sub in ("process", "unnamed file") or re.fullmatch(r"process \d+", sub):
            out.append(list(g)); continue
        k = (str(g[0]["endpoint_id"]), sub)
        j = last.get(k)
        if j is not None and g[0]["window_start_ns"] - out[j][-1]["window_start_ns"] <= horizon:
            out[j] = sorted(out[j] + g, key=lambda a: (a["window_start_ns"], a["id"]))
        else:
            out.append(list(g)); last[k] = len(out) - 1
    out.sort(key=lambda g: (str(g[0]["endpoint_id"]), g[0]["window_start_ns"], g[0]["id"]))
    return out


def group(rows, recur_ns):
    runs, cur = [], []
    for r in rows:
        if cur and (r["endpoint_id"] != cur[-1]["endpoint_id"] or r["window_start_ns"] - cur[-1]["window_start_ns"] > GAP_NS):
            runs.append(cur); cur = []
        cur.append(r)
    if cur:
        runs.append(cur)
    final = []
    for g in runs:
        final.extend(split_connected(g))
    final.sort(key=lambda g: (str(g[0]["endpoint_id"]), g[0]["window_start_ns"], g[0]["id"]))
    return merge_recurring(final, recur_ns) if recur_ns else final


def incidents(rows, ctx, recur_ns):
    rows = sorted((dict(r, context=ctx.get(r["ctx"], {})) for r in rows), key=lambda r: (r["window_start_ns"], r["id"]))
    groups = group(rows, recur_ns)
    fp = sum(not any(r["gt"] for r in g) for g in groups)
    share = defaultdict(list)
    for g in groups:
        s = sum(r["gt"] for r in g) / len(g)
        for a in {a for r in g for a in r["attacks"]}:
            share[a].append(s >= 0.10)
    buried = sorted(a for a, v in share.items() if not any(v))
    return {"incidents": len(groups), "false_incidents": fp, "buried": buried}


# ------------------------------------------------------------------------------------------------ ADP
def adp_curve(lab, att, order):
    """PIDSMaker's ADP (Bilot et al. Eq. 1): area under attack-detection (%) vs precision as the ranking is read."""
    l = lab[order]; a = att[order]
    tp = np.cumsum(l); fp = np.cumsum(~l); p = tp / (tp + fp)
    tot = att.any(0).sum() or 1
    first = np.where(a.any(0), np.argmax(a, axis=0), len(l))
    det = np.zeros(len(l))
    for f in first[first < len(l)]:
        det[f:] += 1
    det = 100 * det / tot
    xs, inv = np.unique(p, return_inverse=True); ys = np.zeros(len(xs)); np.maximum.at(ys, inv, det)
    xs = np.concatenate([[0.0], xs]); ys = np.concatenate([[0.0], ys])
    if xs[1] == 0.0:
        xs = xs[1:]; ys = ys[1:]
    trap = getattr(np, "trapezoid", None) or np.trapz
    return float(trap(ys, xs) / 100)


def adp_random(key, lab, att, n, rng):
    return float(np.mean([adp_curve(lab, att, np.lexsort((rng.random(len(key)), -key))) for _ in range(n)]))


def load_nodes(path):
    z = np.load(path, allow_pickle=False)
    lab = z["label"].astype(bool)
    names = sorted({x for s in z["att"] for x in s.split(";") if x})
    att = np.zeros((len(lab), max(1, len(names))), bool)
    ix = {a: i for i, a in enumerate(names)}
    for j, s in enumerate(z["att"]):
        for x in s.split(";"):
            if x:
                att[j, ix[x]] = True
    return z["tier"], z["sc"], lab, att, names


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True, help="PIDSMaker Ground_Truth/orthrus directory")
    ap.add_argument("--perms", type=int, default=500)
    ap.add_argument("--out", default=R("recompute", "recomputed.json"))
    a = ap.parse_args()
    H = load_hosts()
    GT = {s: load_gt(a.gt, h["ground_truth"]) for s, h in H.items()}
    out = {}

    # 1-3: the 16 development sets ----------------------------------------------------------------------
    print("\n[1] 16 development sets, node level at the operating point (rows13 + public ground truth)")
    dev = {}
    for f in sorted(glob.glob(R("records", "lab_v10", "results", "rows13-*.json.gz"))):
        d = json.load(gzip.open(f, "rt"))
        dev[d["set"]] = d
    assert len(dev) == 16, len(dev)
    days = sum(d["days"] for d in dev.values())
    n_att = sum(H[s]["attacks_counted"] for s in dev)
    tot = {}
    for v in ("P0", "P2"):
        T = Counter(); lay = Counter(); lay_tp = Counter(); inc = Counter(); att_nov = att_nr = att = 0; mism = 0
        per = {}
        for s, d in dev.items():
            rows, m = label_rows(d["rows"][v], GT[s]); mism += m
            nl = node_level(rows)
            cnt = H[s]["attacks_counted"]
            k_att = min(len(nl["attacks_found"]), cnt)
            att += k_att; att_nov += min(len(nl["novelty_attacks"]), cnt); att_nr += min(len(nl["novelty_rules_attacks"]), cnt)
            T["TP"] += nl["TP"]; T["FP"] += nl["FP"]
            lay.update(nl["by_layer"]); lay_tp.update(nl["by_layer_tp"])
            ic = incidents(rows, d["ctx"], RECUR_7D if v == "P2" else 0)
            inc["incidents"] += ic["incidents"]; inc["false"] += ic["false_incidents"]; inc["buried"] += len(ic["buried"])
            per[s] = {"attacks": k_att, "TP": nl["TP"], "FP": nl["FP"], **ic}
        tot[v] = {"attacks": att, "of": n_att, "TP": T["TP"], "FP": T["FP"], "host_days": days, "FP_per_day": round(T["FP"] / days, 1),
                  "precision": round(T["TP"] / (T["TP"] + T["FP"]), 3), "by_layer": dict(lay), "by_layer_tp": dict(lay_tp),
                  "novelty_attacks": att_nov, "novelty_rules_attacks": att_nr, "incidents": inc["incidents"], "false_incidents": inc["false"],
                  "false_incidents_per_day": round(inc["false"] / days, 2), "buried_attacks": inc["buried"],
                  "rows_where_recorded_gt_differs_from_public_gt": mism, "per_set": per}
    out["dev16"] = tot
    t9, t10 = tot["P0"], tot["P2"]
    print(" 0.10 (P2):")
    check("tab:lab 0.10 attacks", t10["attacks"], 26); check("attacks denominator", t10["of"], 30)
    check("tab:lab 0.10 TP", t10["TP"], 333); check("tab:lab 0.10 FP", t10["FP"], 1051)
    check("host-days", days, 71); check("tab:lab 0.10 FP/day", t10["FP_per_day"], 14.8)
    check("tab:lab 0.10 incidents (G2)", t10["incidents"], 220); check("tab:lab 0.10 false incidents (G2)", t10["false_incidents"], 178)
    check("tab:lab 0.10 false incidents per host-day", t10["false_incidents_per_day"], 2.51)
    check("Sec. RQ2 precision 0.10", t10["precision"], 0.241)
    print(" 0.9 (P0):")
    check("tab:lab 0.9 attacks", t9["attacks"], 26); check("tab:lab 0.9 TP", t9["TP"], 337); check("tab:lab 0.9 FP", t9["FP"], 1189)
    check("tab:lab 0.9 FP/day", t9["FP_per_day"], 16.7)
    check("tab:lab 0.9 incidents (G0)", t9["incidents"], 354); check("tab:lab 0.9 false incidents (G0)", t9["false_incidents"], 284)
    check("tab:lab 0.9 false incidents per host-day", t9["false_incidents_per_day"], 4.00)
    print(" tab:layers (first-alert attribution), 0.9 and 0.10 columns:")
    for v, col in (("P0", "0.9"), ("P2", "0.10")):
        exp = {"P0": {"novelty": (644, 88), "rules": (536, 203), "corroborated": (346, 46)},
               "P2": {"novelty": (544, 87), "rules": (536, 203), "corroborated": (304, 43)}}[v]
        for l, (n, t) in exp.items():
            check(f"tab:layers {col} {l}", f"{tot[v]['by_layer'].get(l, 0)} ({tot[v]['by_layer_tp'].get(l, 0)})", f"{n} ({t})")
    print(" tab:ablation (parts derivable from the 0.9 / 0.10 rows):")
    check("tab:ablation layer 1 (0.9 rows, novelty-attributed) attacks", t9["novelty_attacks"], 20)
    check("tab:ablation layer 1 TP / FP", (t9["by_layer_tp"].get("novelty", 0), t9["by_layer"].get("novelty", 0) - t9["by_layer_tp"].get("novelty", 0)), (88, 556))
    check("tab:ablation + fleet prevalence (0.10 rows) attacks", t10["novelty_attacks"], 20)
    check("tab:ablation + fleet prevalence TP / FP", (t10["by_layer_tp"].get("novelty", 0), t10["by_layer"].get("novelty", 0) - t10["by_layer_tp"].get("novelty", 0)), (87, 457))
    check("tab:ablation 0.10 attacks / TP / FP", (t10["attacks"], t10["TP"], t10["FP"]), (26, 333, 1051))
    print("  note: tab:ablation 'layers 1-2' (21 / 290 / 791) is a separately run configuration; see section [5] (per-host results).")

    print("\n[3] tab:evidence (0.10 rows, one-hop context)")
    classes, only_corr = Counter(), 0
    for s, d in dev.items():
        if H[s]["attacks_counted"] == 0:
            continue
        rows, _ = label_rows(d["rows"]["P2"], GT[s])
        det = defaultdict(list)
        for x in rows:
            if x["layer"] in ("novelty", "rules"):
                det[x["window_start_ns"]].append(x)
        gl, an, cg = defaultdict(set), defaultdict(set), defaultdict(bool)
        for x in rows:
            for at in x["attacks"]:
                if x["layer"] in ("novelty", "rules"):
                    gl[at].add(x["layer"])
                else:
                    cg[at] = True
                    if x["rule"] == "novel_executable_repeat":
                        gl[at].add("novelty")
                    c = d["ctx"].get(x["ctx"], {})
                    nb = {e["src"] for e in c.get("edges", [])} | {e["dst"] for e in c.get("edges", [])}
                    an[at] |= {y["layer"] for y in det[x["window_start_ns"]] if y["node_uuid"] in nb}
        for at in H[s]["ground_truth"]:
            g, n_ = gl.get(at, set()), an.get(at, set())
            c = ("rule_gt" if "rules" in g else "rule_anchor" if "rules" in n_ else "novelty_gt" if "novelty" in g else
                 "novelty_anchor" if "novelty" in n_ else "corroborated_unanchored" if cg[at] else "missed")
            classes[c] += 1; only_corr += bool(cg[at] and not g)
    out["evidence"] = dict(classes, only_corroboration_on_gt=only_corr)
    for c, n in (("rule_gt", 9), ("rule_anchor", 6), ("novelty_gt", 10), ("novelty_anchor", 1), ("missed", 4)):
        check(f"tab:evidence {c}", classes.get(c, 0), n)
    check("tab:evidence detected, only corroboration on a labelled node", only_corr, 5)

    # 4: ADP --------------------------------------------------------------------------------------------
    print(f"\n[4] tab:adp, STRATA columns (data/v0.10_nodes, {a.perms} random tie orders, seed 0)")
    EIGHT = [("CADETS_E3", "E3 CADETS", 1.00, 0.73), ("THEIA_E3", "E3 THEIA", 1.00, 0.99), ("CLEARSCOPE_E3", "E3 ClearScope", 0.18, 0.18),
             ("THEIA_E5-theia", "E5 THEIA", 0.00, 0.00), ("CLEARSCOPE_E5-clearscope-3att", "E5 ClearScope (3 attacks)", 0.67, 0.13),
             ("OPTC_H051", "OpTC H051", 0.85, 0.81), ("OPTC_H201", "OpTC H201", 0.75, 1.00), ("OPTC_H501", "OpTC H501", 0.91, 0.29)]
    rng = np.random.default_rng(0)
    adp = {}
    for s, name, p_tri, p_learned in EIGHT:
        tier, sc, lab, att, _ = load_nodes(R("data", "v0.10_nodes", f"nodes-{s}.npz"))
        key = tier * 1e6 + sc
        st = adp_curve(lab, att, np.argsort(-key, kind="stable"))
        tri = adp_random(key, lab, att, a.perms, rng)
        lrn = adp_random(sc.astype(float), lab, att, a.perms, rng)
        adp[s] = {"triage_random": tri, "triage_node_id_order": st, "learned_random": lrn, "nodes": int(len(lab)), "gt_nodes": int(lab.sum()),
                  "alerted": int((tier > 0).sum()), "alerted_gt": int((lab & (tier > 0)).sum())}
        check(f"tab:adp {name} triage (paper rounded to 2 dp)", round(tri, 4), p_tri, tol=0.005)
        check(f"tab:adp {name} learned (paper rounded to 2 dp)", round(lrn, 4), p_learned, tol=0.005)
    m_tri = float(np.mean([v["triage_random"] for v in adp.values()])); m_l = float(np.mean([v["learned_random"] for v in adp.values()]))
    m_st = float(np.mean([v["triage_node_id_order"] for v in adp.values()]))
    check("tab:adp eight-host mean triage ADP (random ties; paper rounded to 2 dp)", round(m_tri, 4), 0.67, tol=0.005)
    check("tab:adp eight-host mean learned ADP (random ties; paper rounded to 2 dp)", round(m_l, 4), 0.52, tol=0.005)
    check("eight-host mean triage ADP, node-id tie order (Sec. Metrics: 'mean unchanged')", round(m_st, 4), 0.67, tol=0.005)
    adp["mean"] = {"triage_random": m_tri, "learned_random": m_l, "triage_node_id_order": m_st}
    for s, name in (("CLEARSCOPE_E5-clearscope", "E5 ClearScope, PIDSMaker's 2 attacks (footnote)"), ("FIVEDIRECTIONS_E3", "FiveDirections (Sec. Metrics)")):
        tier, sc, lab, att, _ = load_nodes(R("data", "v0.10_nodes", f"nodes-{s}.npz"))
        v = adp_random(tier * 1e6 + sc, lab, att, a.perms, rng); adp[s] = {"triage_random": v}
        check(f"{name} triage ADP (paper rounded to 2 dp)", round(v, 4), 1.00 if "CLEARSCOPE" in s else 0.20, tol=0.005)
    print("  cross-check of the per-node arrays against the alert rows (alerted nodes / alerted ground-truth nodes):")
    for s, *_ in EIGHT:
        base = s.replace("-3att", "")
        if base in dev:
            nl = out["dev16"]["P2"]["per_set"][base]
            check(f"  nodes-{s}: alerted = rows' alerted nodes", adp[s]["alerted"], nl["TP"] + nl["FP"])
            check(f"  nodes-{s}: alerted GT = TP from public GT", adp[s]["alerted_gt"], nl["TP"])
    out["adp"] = adp

    # 5: five runs --------------------------------------------------------------------------------------
    print("\n[5] Five training runs (records/lab_paper5, all 17 sets)")
    P5 = R("records", "lab_paper5", "results")
    hosts8 = ["CADETS_E3", "THEIA_E3", "CLEARSCOPE_E3", "THEIA_E5-theia", "CLEARSCOPE_E5-clearscope", "OPTC_H051", "OPTC_H201", "OPTC_H501"]
    runs = {}
    for h in hosts8:
        for r in range(1, 6):
            f = os.path.join(P5, f"res5-{h}-r{r}.json")
            if os.path.exists(f):
                runs[(h, r)] = json.load(open(f))
    five = {"per_run": {}, "per_host": {}}
    for r in range(1, 6):
        if not all((h, r) in runs for h in hosts8):
            continue
        def pick(h, fn):
            x = runs[(h, r)]
            return fn(x["with_extra_gt"]) if h.startswith("CLEARSCOPE_E5") else fn(x)
        five["per_run"][r] = {
            "mean_triage_ADP_node_id_order": float(np.mean([pick(h, lambda x: x["P2"]["ADP"]) for h in hosts8])),
            "mean_learned_ADP_node_id_order": float(np.mean([pick(h, lambda x: x["P2"]["ADP_learned_only"]) for h in hosts8])),
            "mean_d1_ADP": float(np.mean([pick(h, lambda x: x["detector-1"]["ADP"]) for h in hosts8])),
            "mean_d2_ADP": float(np.mean([pick(h, lambda x: x["detector-2"]["ADP"]) for h in hosts8])),
            "d2_attacks_CADETS": runs[("CADETS_E3", r)]["detector-2"]["val_max"]["attacks"]}
    for h in hosts8:
        rr = [r for r in range(1, 6) if (h, r) in runs]
        found, tpfp, adps = set(), [], []
        for r in rr:
            x = runs[(h, r)]
            fr = os.path.join(P5, "rows", f"rows5-{h}-r{r}.json.gz")
            if os.path.exists(fr):
                d = json.load(gzip.open(fr, "rt")); rows, _ = label_rows(d["rows"]["P2"], GT[h]); nl = node_level(rows)
                tpfp.append((nl["TP"], nl["FP"])); found.add(tuple(nl["attacks_found"]))
            adps.append(x["with_extra_gt"]["P2"]["ADP"] if h.startswith("CLEARSCOPE_E5") else x["P2"]["ADP"])
        five["per_host"][h] = {"runs": rr, "attack_sets_from_rows": [list(f) for f in found], "TP_FP_from_rows": tpfp,
                               "triage_ADP_node_id_order": [round(v, 3) for v in adps]}
    out["five_runs"] = five
    pr = five["per_run"]
    if pr:
        m = [v["mean_triage_ADP_node_id_order"] for v in pr.values()]
        check("five runs: eight-host mean triage ADP range (node-id order)", f"{min(m):.3f}-{max(m):.3f}", "0.666-0.669")
        for k, lo, hi in (("mean_learned_ADP_node_id_order", 0.44, 0.57), ("mean_d1_ADP", 0.27, 0.33), ("mean_d2_ADP", 0.25, 0.52)):
            m = [v[k] for v in pr.values()]
            check(f"five runs: {k} min (paper rounded to 2 dp)", round(min(m), 4), lo, tol=0.005)
            check(f"five runs: {k} max (paper rounded to 2 dp)", round(max(m), 4), hi, tol=0.005)
        check("five runs: detector-2 attacks found on E3 CADETS per run", [pr[r]["d2_attacks_CADETS"] for r in sorted(pr)], [3, 1, 0, 0, 3])
        same = all(len(v["attack_sets_from_rows"]) == 1 for v in five["per_host"].values())
        check("five runs: same attacks detected at the operating point in every run (8 hosts, from rows)", same, True)
        same_adp = [h for h, v in five["per_host"].items() if len({round(x, 2) for x in v["triage_ADP_node_id_order"]}) > 1]
        check("five runs: hosts whose triage ADP (2 decimals) varies across runs", same_adp, ["CLEARSCOPE_E5-clearscope"])
        cs = five["per_host"]["CLEARSCOPE_E5-clearscope"]["triage_ADP_node_id_order"]
        check("five runs: E5 ClearScope triage ADP range", f"{min(cs):.2f}-{max(cs):.2f}", "0.67-0.69")
        for h, lo, hi in (("THEIA_E3", 86, 95), ("THEIA_E5-theia", 95, 114)):
            fps = [fp for _, fp in five["per_host"][h]["TP_FP_from_rows"]]
            check(f"five runs: {h} FP range (from rows)", f"{min(fps)}-{max(fps)}", f"{lo}-{hi}")
    # 16 development sets per run, from the rows (Sec. RQ2 text after tab:lab: same 26 attacks, FP 1,051-1,136,
    # false incidents 173-178)
    tot16 = {}
    for r in range(1, 6):
        fs = {s: os.path.join(P5, "rows", f"rows5-{s}-r{r}.json.gz") for s in dev}
        if not all(os.path.exists(f) for f in fs.values()):
            continue
        t = Counter()
        for s, f in fs.items():
            d = json.load(gzip.open(f, "rt")); rows, _ = label_rows(d["rows"]["P2"], GT[s]); nl = node_level(rows)
            ic = incidents(rows, d["ctx"], RECUR_7D)
            t["attacks"] += min(len(nl["attacks_found"]), H[s]["attacks_counted"]); t["TP"] += nl["TP"]; t["FP"] += nl["FP"]
            t["incidents"] += ic["incidents"]; t["false_incidents"] += ic["false_incidents"]
        tot16[r] = dict(t)
    five["dev16_per_run_from_rows"] = tot16
    if len(tot16) == 5:
        check("five runs, 16 sets: attacks detected per run", [tot16[r]["attacks"] for r in sorted(tot16)], [26] * 5)
        fps = [v["FP"] for v in tot16.values()]; fis = [v["false_incidents"] for v in tot16.values()]
        check("five runs, 16 sets: FP range", f"{min(fps)}-{max(fps)}", "1051-1136")
        check("five runs, 16 sets: false incidents range (incident re-implementation)", f"{min(fis)}-{max(fis)}", "173-178")
        check("five runs, 16 sets: run 1 (reported) has the fewest FP", min(fps) == tot16[1]["FP"], True)
    l12 = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(P5, "res5-*-r1.json")))]
    l12 = [x for x in l12 if x["set"] in dev]
    if len(l12) == 16:
        s = (sum(min(len(x["P2"]["layers12_only"]["attacks_found"]), H[x["set"]]["attacks_counted"]) for x in l12),
             sum(x["P2"]["layers12_only"]["TP"] for x in l12), sum(x["P2"]["layers12_only"]["FP"] for x in l12))
        check("tab:ablation layers 1-2 (separate configuration; per-host results res5-*-r1, not rows)", s, (21, 290, 791))

    # 6: held-out E5 ClearScope ---------------------------------------------------------------------------
    print("\n[6] tab:heldout, 0.10 on held-out E5 ClearScope (ho10rows + public ground truth)")
    d = json.load(gzip.open(R("records", "heldout_v10", "results", "ho10rows-CLEARSCOPE_E5.json.gz"), "rt"))
    s = "CLEARSCOPE_E5-clearscope"; ho = {}
    for v, recur in (("A", 0), ("N", 0)):
        rows, _ = label_rows(d["rows"][v], GT[s]); nl = node_level(rows)
        ho[v] = {"attacks": len(nl["attacks_found"]), "TP": nl["TP"], "FP": nl["FP"],
                 "G0": incidents(rows, d["ctx"], 0), "G2": incidents(rows, d["ctx"], RECUR_7D)}
    out["heldout_E5_ClearScope"] = ho
    check("0.8.1 (A): attacks, TP / FP", (ho["A"]["attacks"], ho["A"]["TP"], ho["A"]["FP"]), (2, 9, 49))
    check("0.10 (N): attacks, TP / FP", (ho["N"]["attacks"], ho["N"]["TP"], ho["N"]["FP"]), (2, 4, 15))
    check("false incidents 0.8.1 -> 0.10 (G2)", (ho["A"]["G2"]["false_incidents"], ho["N"]["G2"]["false_incidents"]), (14, 6))
    check("false incidents 0.9 grouping -> 0.10 grouping (N)", (ho["N"]["G0"]["false_incidents"], ho["N"]["G2"]["false_incidents"]), (9, 6))

    # 7: 0.7 / 0.8.1 from per-host results ------------------------------------------------------------------
    print("\n[7] tab:lab / tab:layers, 0.7 released and 0.8.1 (per-host results; no alert rows exist for these versions)")
    res9 = [json.load(open(f)) for f in sorted(glob.glob(R("records", "lab_v09", "res9-*.json")))]
    for v, col, exp in (("R", "0.7 released", (26, 347, 5670)), ("A", "0.8.1", (26, 344, 2034))):
        t = (sum(min(x[v]["attacks"], H[x["set"]]["attacks_counted"]) for x in res9), sum(x[v]["TP"] for x in res9), sum(x[v]["FP"] for x in res9))
        check(f"tab:lab {col} attacks / TP / FP", t, exp)
        bl = Counter(); bt = Counter()
        for x in res9:
            bl.update(x[v]["by_layer"]); bt.update(x[v]["by_layer_tp"])
        out.setdefault("v07_v081_from_per_host_results", {})[col] = {"attacks_TP_FP": t, "by_layer": dict(bl), "by_layer_tp": dict(bt)}
        exp_l = {"R": {"novelty": "644 (88)", "rules": "536 (203)", "corroborated": "4062 (52)", "learned": "775 (4)"},
                 "A": {"novelty": "644 (88)", "rules": "536 (203)", "corroborated": "419 (48)", "learned": "779 (5)"}}[v]
        for l, e in exp_l.items():
            check(f"tab:layers {col} {l}", f"{bl.get(l, 0)} ({bt.get(l, 0)})", e)

    # 8: bootstrap ----------------------------------------------------------------------------------------
    print("\n[8] Sec. RQ2 bootstrap (16 development sets, 10,000 resamples; same procedure and seed as records/lotl_paper/scripts/bootstrap.py)")
    import random
    FAM = {"CADETS_E3": "DARPA E3", "THEIA_E3": "DARPA E3", "CLEARSCOPE_E3": "DARPA E3", "FIVEDIRECTIONS_E3": "DARPA E3",
           "TRACE_E3-trace": "DARPA E3", "THEIA_E5-theia": "DARPA E5", "OPTC_H051": "OpTC", "OPTC_H201": "OpTC", "OPTC_H501": "OpTC",
           "ATLASV2_EDR-h1": "ATLASv2", "ATLASV2_EDR-h2": "ATLASv2"}
    units = {}
    for st_ in sorted(dev):
        ps = out["dev16"]["P2"]["per_set"][st_]
        units[st_] = {"attacks": H[st_]["attacks_counted"], "found": ps["attacks"], "TP": ps["TP"], "FP": ps["FP"],
                      "days": dev[st_]["days"], "fp_inc": ps["false_incidents"], "family": FAM.get(st_, "CARBANAKv2")}

    def bstats(us):
        a_ = sum(u["attacks"] for u in us); d_ = sum(u["days"] for u in us); tp_ = sum(u["TP"] for u in us); fp_ = sum(u["FP"] for u in us)
        return {"detection_rate": sum(u["found"] for u in us) / a_ if a_ else float("nan"), "fp_per_host_day": fp_ / d_,
                "false_incidents_per_host_day": sum(u["fp_inc"] for u in us) / d_}

    def pct(xs, q):
        xs = sorted(x for x in xs if x == x); k = (len(xs) - 1) * q; lo = int(k); hi = min(lo + 1, len(xs) - 1)
        return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)

    fam = {}
    for u in units.values():
        fam.setdefault(u["family"], []).append(u)
    boot = {}
    for name, cl in (("host", [[u] for u in units.values()]), ("family", list(fam.values()))):
        rr = random.Random(20261112); dr = defaultdict(list)
        for _ in range(10000):
            us = [u for c in (rr.choice(cl) for _ in range(len(cl))) for u in c]
            for k, v in bstats(us).items():
                dr[k].append(v)
        boot[name] = {k: (pct(v, 0.025), pct(v, 0.975)) for k, v in dr.items()}
    out["bootstrap"] = boot
    bh, bf = boot["host"], boot["family"]
    check("bootstrap detection rate interval (host)", f"[{bh['detection_rate'][0]:.2f}, {bh['detection_rate'][1]:.2f}]", "[0.75, 1.00]")
    check("bootstrap FP per host-day interval (host)", f"[{bh['fp_per_host_day'][0]:.1f}, {bh['fp_per_host_day'][1]:.1f}]", "[10.2, 22.2]")
    check("bootstrap false incidents per host-day interval (host)", f"[{bh['false_incidents_per_host_day'][0]:.1f}, {bh['false_incidents_per_host_day'][1]:.1f}]", "[1.7, 3.7]")
    check("bootstrap false incidents per host-day interval (family)", f"[{bf['false_incidents_per_host_day'][0]:.1f}, {bf['false_incidents_per_host_day'][1]:.1f}]", "[1.9, 5.2]")

    # 9: LotL counterfactual ---------------------------------------------------------------------------------
    print("\n[9] Sec. RQ4 living-off-the-land counterfactual (records/lotl_paper/results/rows, variant P2, + public ground truth)")
    lotl = {}
    for tr in ("none", "lotl", "launder", "lotlall"):
        att = tp = fp = finc = 0; per = {}
        for f in sorted(glob.glob(R("records", "lotl_paper", "results", "rows", f"rows-{tr}-*.json.gz"))):
            d = json.load(gzip.open(f, "rt"))
            if d["set"] not in dev:
                continue
            rows, _ = label_rows(d["rows"]["P2"], GT[d["set"]]); nl = node_level(rows)
            k = min(len(nl["attacks_found"]), H[d["set"]]["attacks_counted"])
            ic = incidents(rows, d["ctx"], RECUR_7D)
            att += k; tp += nl["TP"]; fp += nl["FP"]; finc += ic["false_incidents"]; per[d["set"]] = {"attacks": k, "TP": nl["TP"], "FP": nl["FP"]}
        lotl[tr] = {"attacks": att, "TP": tp, "FP": fp, "false_incidents": finc, "false_incidents_per_day": round(finc / days, 2), "per_set": per}
    out["lotl"] = lotl
    check("LotL: attacks without transformation", lotl["none"]["attacks"], 26)
    check("LotL: attacks after renaming new programs", lotl["lotl"]["attacks"], 18)
    check("LotL: CADETS TP renaming -> renaming + laundering", (lotl["lotl"]["per_set"]["CADETS_E3"]["TP"], lotl["launder"]["per_set"]["CADETS_E3"]["TP"]), (32, 3))
    check("LotL: CADETS attacks after laundering (one of three lost)", lotl["launder"]["per_set"]["CADETS_E3"]["attacks"], 2)
    check("LotL post-hoc bound: attacks when every new program is renamed", lotl["lotlall"]["attacks"], 10)
    check("LotL post-hoc bound: false incidents per host-day", round(lotl["lotlall"]["false_incidents_per_day"], 1), 0.3)

    # 10: tab:orig, STRATA columns ----------------------------------------------------------------------------
    print("\n[10] tab:orig, STRATA 0.10 columns (rows13 + public ground truth; ADP from data/v0.10_nodes)")
    ORIG = [("TRACE_E3-trace", 0.13, 3, 17.5), ("FIVEDIRECTIONS_E3", 0.20, 2, 55.3), ("ATLASV2_EDR-h1", 0.21, 8, 49.0),
            ("CARBANAKV2_EDR-h1", 0.06, 1, 10.4), ("CARBANAKV2_EDR-h2", 0.48, 1, 14.6), ("CARBANAKV2_EDR-h3", 0.04, 1, 10.3),
            ("CARBANAKV2_EDR-h4", 0.13, 1, 3.4), ("CARBANAKV2_EDR-h5", 1.00, 1, 8.1)]
    ptp = pfp = 0; orig = {}
    for st_, p_adp, p_found, p_fpd in ORIG:
        ps = out["dev16"]["P2"]["per_set"][st_]
        tier, sc, lab, att_, _ = load_nodes(R("data", "v0.10_nodes", f"nodes-{st_}.npz"))
        v = adp_random(tier * 1e6 + sc, lab, att_, a.perms, rng)
        orig[st_] = {"ADP_random": v, "found": ps["attacks"], "FP_per_day": round(ps["FP"] / dev[st_]["days"], 1)}
        ptp += ps["TP"]; pfp += ps["FP"]
        check(f"tab:orig {st_} ADP (paper rounded to 2 dp)", round(v, 4), p_adp, tol=0.005)
        check(f"tab:orig {st_} found / FP per day", (ps["attacks"], orig[st_]["FP_per_day"]), (p_found, p_fpd))
    adps = [orig[s_]["ADP_random"] for s_, *_ in ORIG]
    check("Sec. RQ1 mean ADP over these eight hosts (paper rounded to 2 dp)", round(float(np.mean(adps)), 4), 0.28, tol=0.005)
    check("tab:orig STRATA pooled precision (TP / FP)", (f"{100 * ptp / (ptp + pfp):.1f}%", ptp, pfp), ("12.2%", 95, 684))
    out["orig_strata"] = orig

    # 11: tab:replay ---------------------------------------------------------------------------------------------
    print("\n[11] tab:replay (per-host results only: records/lab_v10/results/replay/compare10.json; replay alert rows not released)")
    c10 = json.load(open(R("records", "lab_v10", "results", "replay", "compare10.json")))
    RAW = ["CADETS_E3", "THEIA_E3", "CLEARSCOPE_E3", "FIVEDIRECTIONS_E3", "OPTC_H201", "OPTC_H501", "OPTC_H051", "ATLASV2_EDR-h1", "ATLASV2_EDR-h2"]
    for grp, sets, exp in (("9 raw", RAW, (18, 261, 485, 18, 261, 543)), ("7 stored", [s_ for s_ in dev if s_ not in RAW], (8, 72, 566, 8, 72, 612))):
        t = tuple(sum(c10[s_][k][m] for s_ in sets) for k, m in (("lab", "attacks"), ("lab", "TP"), ("lab", "FP"), ("replay10", "attacks"), ("replay10", "TP"), ("replay10", "FP")))
        check(f"tab:replay {grp}: lab att/TP/FP, replay att/TP/FP", t, exp)
    tt = c10["_totals"]
    check("tab:replay incidents (false), lab console vs replay", (tt["console_lab10"]["incidents"], tt["console_lab10"]["fp_incidents"], tt["replay10"]["incidents"], tt["replay10"]["fp_incidents"]), (220, 178, 222, 180))
    lab_tp_fp = sum(out["dev16"]["P2"]["per_set"][s_]["TP"] for s_ in dev), sum(out["dev16"]["P2"]["per_set"][s_]["FP"] for s_ in dev)
    check("tab:replay lab side equals the rows recomputation (TP, FP)", (tt["lab"]["TP"], tt["lab"]["FP"]), lab_tp_fp)

    out["checks"] = CHECKS
    json.dump(out, open(a.out, "w"), indent=1, default=lambda o: o if not isinstance(o, tuple) else list(o))
    n_ok = sum(c["match"] for c in CHECKS)
    print(f"\n{n_ok} of {len(CHECKS)} checks match the paper exactly; details in {os.path.relpath(a.out, ROOT)}")


if __name__ == "__main__":
    main()
