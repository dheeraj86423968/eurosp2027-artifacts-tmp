"""paper_v19 (artifacts/paper_v19/PROTOCOL.md): score a set once with the paper's 0.10 bundle and apply three
deterministic-layer versions to the same windows and learned scores - V10 (the bundle's own layers = the paper's
0.10), V19 (released 0.19 defaults, re-fitted: out/layers22-SET-RP2.json + exec_once) and V19id (V19 + the
program_identity option: out/layersp-SET-RP2id.json). Fleet prevalence K = 2 (drop) as 0.10, per version from the other
members' layers. Records, per version, node results, ADP inputs (alert tier, learned score; random-tie ADP in
adp_ties.py) and every alert row the agent would report with its one-hop context (incidents: lab_v10 inc13.py).
lab_v10 adp13.py + lab_v18 eval21.py combined. Usage: evalp.py SET --out res.json --rows rows.json.gz --npz scores.npz
[--gt-extra csv,...]"""
import argparse, copy, gzip, json, time
from collections import Counter
import numpy as np
from pdp_engine.runtime import Runtime, alert_tier
from pdp_engine.layers import ALWAYS_EVIDENCE, UNKNOWN_PROGRAM, DeterministicLayers, program_name
from pdp_engine.schema import EDGE_TYPES
from pdp_server.tools.darpa_eval import adp
from common8 import Set, log, at, load_gt

FLEETS = {"CARBANAKV2": [f"CARBANAKV2_EDR-h{i}" for i in range(1, 6)], "OPTC": ["OPTC_H201", "OPTC_H501", "OPTC_H051"],
          "ATLASV2": ["ATLASV2_EDR-h1", "ATLASV2_EDR-h2"],
          "E3": ["CADETS_E3", "THEIA_E3", "CLEARSCOPE_E3", "FIVEDIRECTIONS_E3", "TRACE_E3-trace"],
          "THEIA_E5": ["THEIA_E5-theia"], "CLEARSCOPE_E5": ["CLEARSCOPE_E5-clearscope"]}
BUNDLE = {s: "b07rel" for s in FLEETS["CARBANAKV2"] + ["THEIA_E5-theia", "CLEARSCOPE_E5-clearscope"]}
SPEC = {"V19": "layers22-{}-RP2.json", "V19id": "layersp-{}-RP2id.json"}
VARIANTS = ("V10", "V19", "V19id")
FLEET_K = 2
EARLY_NS = 2 * 3600 * 10**9
ORDER = {"novelty": 0, "rules": 1, "corroborated": 2, "learned": 3}

ap = argparse.ArgumentParser(); ap.add_argument("set"); ap.add_argument("--out", required=True); ap.add_argument("--rows", required=True)
ap.add_argument("--npz", required=True); ap.add_argument("--gt-extra", default="")
a = ap.parse_args()
S = Set(a.set)
if a.gt_extra:
    for k, v in load_gt(a.gt_extra.split(",")).items():
        S.gt[k] = v
    S.allgt = set().union(*S.gt.values())
bdir = lambda s: f"{Set(s).work}/{BUNDLE.get(s, 'v07rel')}"
st = S.eval_store(); reg = st.load_registry()
t0 = time.time()
rt = Runtime(bdir(a.set), reg, device="cuda", feat_device="cuda")


def spec_of(s, v):
    if v == "V10":
        return json.load(open(f"{bdir(s)}/layers.json"))
    sp = json.load(open("out/" + SPEC[v].format(s)))
    sp["config"]["exec_once"] = True                      # default since lab 0.16 (LayerConfig; prep re-fits keep the bundle's config)
    return sp


fleet = next(m for m in FLEETS.values() if a.set in m)
L, pols, cnt_key, cnt_name = {}, {}, {}, {}
for v in VARIANTS:
    L[v] = rt.layers if v == "V10" else DeterministicLayers(spec_of(a.set, v), rt.m["num_nodes"])
    nov = L[v].novelty
    ck, cn = Counter(), Counter()
    for o in fleet:
        if o != a.set:
            keys = {nov.key(k) for k in spec_of(o, v)["known_executables"] if k not in UNKNOWN_PROGRAM}
            ck.update(keys); cn.update({program_name(k) for k in keys})
    cnt_key[v], cnt_name[v] = ck, cn
    p = copy.copy(rt.policy); p.reset(); p.evidence_rules = set(p.evidence_rules)
    if v != "V10":
        p.layers = L[v]
        p.evidence_rules = set(L[v].spec["config"].get("evidence_rules", ())) | set(ALWAYS_EVIDENCE)
    pols[v] = p
log(f"fleet {fleet}: " + ", ".join(f"{v} {len(cnt_key[v])} keys" for v in VARIANTS))


def fleet_n(v, exe):
    k = L[v].novelty.key(exe)
    n = cnt_key[v].get(k, 0)
    if n == 0 and "/" not in k:            # recorded without a path: by name, as layer 1 matches its own baseline
        n = cnt_name[v].get(program_name(k), 0)
    return n


SC, TIER, cur = {}, {v: {} for v in VARIANTS}, {}


def apply_all(w, ids, fused, hits=None):
    own = getattr(rt, "_own", None)
    out = None
    for v in VARIANTS:
        if v == "V10":
            hs = hits if hits is not None else rt.layers.process(w, rt.reg, ids)
        else:
            hs = L[v].process(w, rt.reg, ids)
        hs = [h for h in hs if not (h.layer == "novelty" and fleet_n(v, h.key) >= FLEET_K)]
        al, rs, hh = pols[v].apply(w, rt.reg, ids, fused, hs, own=own)
        cur[v] = (al, rs)
        for n in al.tolist():
            TIER[v][n] = max(TIER[v].get(n, 0), alert_tier(rs[n]))
        if out is None:
            out = (al, rs, hh)
    for n, f in zip(ids.tolist(), np.asarray(fused, dtype=float).tolist()):
        if f > SC.get(n, -1e18):
            SC[n] = f
    return out


rt._alert_policy = apply_all


def context(w, node, cap=300):     # = pdp_agent.agent.Agent.context (hops=1), without edge losses
    src, dst = w.src, w.dst
    m = (src == node) | (dst == node)
    keep = {node} | set(src[m].tolist()) | set(dst[m].tolist())
    m = np.isin(src, list(keep)) & np.isin(dst, list(keep))
    idx = np.where(m)[0][:cap * 4]
    nodes = [{"uuid": reg[i].uuid, "ntype": reg[i].ntype, "label": reg[i].label} for i in sorted(keep)[:cap]]
    edges = [{"src": reg[int(src[i])].uuid, "dst": reg[int(dst[i])].uuid, "op": EDGE_TYPES[int(w.etype[i])], "ts_ns": int(w.t[i])} for i in idx]
    return {"nodes": nodes, "edges": edges}


alerted = {v: {} for v in VARIANTS}
rows = {v: [] for v in VARIANTS}
early = {v: {} for v in VARIANTS}
ctxs, seq = {}, 0
seen = np.zeros(0, bool)
for d in S.test_days:
    for w in st.windows(d):
        rt.score(w)
        wctx = {}
        for v, (al, rs) in cur.items():
            for n in al.tolist():
                rsn = rs[n]
                layer = min((x["layer"] for x in rsn), key=lambda x: ORDER.get(x, 9))
                main = next(x for x in rsn if x["layer"] == layer)
                if n not in alerted[v]:
                    alerted[v][n] = layer
                e = reg.entities[n]
                if layer in ("rules", "novelty"):
                    ek = (e.uuid, main.get("rule"))
                    if ek in early[v] and int(w.start_ns) - early[v][ek] < EARLY_NS:
                        continue
                    early[v][ek] = int(w.start_ns)
                if n not in wctx:
                    cid = f"{int(w.start_ns)}:{n}"
                    ctxs[cid] = context(w, n); wctx[n] = cid
                seq += 1
                rows[v].append({"id": seq, "endpoint_id": a.set, "endpoint_name": a.set, "window_start_ns": int(w.start_ns),
                                "node_uuid": e.uuid, "ntype": e.ntype, "label": e.label, "display": None, "layer": layer,
                                "rule": main.get("rule"), "reason": main.get("detail"), "status": "open", "ctx": wctx[n],
                                "gt": e.uuid in S.allgt, "attacks": sorted(x for x, vv in S.gt.items() if e.uuid in vv)})
        if len(seen) < len(reg):
            seen = np.concatenate([seen, np.zeros(len(reg) - len(seen), bool)])
        seen[w.src] = True; seen[w.dst] = True
log(f"scored {time.time()-t0:.0f}s")
ix = np.where(seen)[0]
uu = [reg.entities[int(i)].uuid for i in ix]
labels = np.array([u in S.allgt for u in uu]); na = [{k for k, vv in S.gt.items() if u in vv} for u in uu]
ATT = sorted(S.gt)
pos = {int(i): j for j, i in enumerate(ix)}
sc = np.array([SC.get(int(i), 0.0) for i in ix])
res = {"set": a.set, "bundle": bdir(a.set), "fleet": fleet, "n_attacks": len(S.gt), "gt_nodes": int(labels.sum()),
       "days": len(S.test_days), "attacks_all": ATT}
npz = {"labels": labels, "attacks": np.array([[x in s for x in ATT] for s in na], dtype=bool).reshape(len(na), len(ATT)),
       "learned": sc}
for v in VARIANTS:
    pred = np.zeros(len(ix), bool); lay = {}
    for n, l in alerted[v].items():
        if n in pos:
            pred[pos[n]] = True; lay[pos[n]] = l
    r0 = at(pred, labels, na); r0["FP/day"] = round(r0["FP"] / max(1, len(S.test_days)), 1)
    r0["by_layer"] = dict(Counter(lay.values()))
    r0["by_layer_tp"] = dict(Counter(l for j, l in lay.items() if labels[j]))
    r0["attacks_found"] = sorted({x for j in np.where(pred & labels)[0] for x in na[j]})
    r0["attacks_det"] = sorted({x for j, l in lay.items() if labels[j] and l in ("novelty", "rules") for x in na[j]})
    r0["rows"] = len(rows[v])
    tr = np.array([TIER[v].get(int(i), 0) for i in ix])
    npz[f"tier_{v}"] = tr
    r0["ADP_stable"] = round(adp(tr * 1e6 + np.clip(sc, 0, 1e5), labels, na), 3)
    r0["precision"] = round(r0["TP"] / max(1, r0["TP"] + r0["FP"]), 3)
    res[v] = r0
    log(f"{v}: attacks {r0['attacks']} det-alone {len(r0['attacks_det'])} TP {r0['TP']} FP {r0['FP']} rows {r0['rows']} ADP(stable) {r0['ADP_stable']}")
json.dump(res, open(a.out, "w"), indent=1)
np.savez_compressed(a.npz, **npz)
with gzip.open(a.rows, "wt") as f:
    json.dump({"set": a.set, "days": len(S.test_days), "attacks": ATT, "ctx": ctxs, "rows": rows}, f)
