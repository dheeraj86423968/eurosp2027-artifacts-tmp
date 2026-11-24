# paper_v19: expected ADP under a random order within ties (paper_analysis/adp_random_ties.py, same curve and seed),
# per version, from evalp.py's per-node arrays (out/scores-*.npz). Triage order = alert tier x 1e6 + learned score.
# Usage: python3 adp_ties.py OUTDIR [PERMS]   (numpy only)
import glob, json, sys
import numpy as np


def adp_curve(lab, att, order):
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
        xs = xs[1:]; ys = ys[1:]; ys[0] = max(ys[0], 0)
    return float(np.trapz(ys, xs) / 100)


def rand_adp(key, lab, att, n, rng):
    v = []
    for _ in range(n):
        o = np.lexsort((rng.random(len(key)), -key)); v.append(adp_curve(lab, att, o))
    v = np.array(v); return float(v.mean()), float(v.std() / np.sqrt(n))


D = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 500
rng = np.random.default_rng(0); out = {}
for f in sorted(glob.glob(f"{D}/scores-*.npz")):
    z = np.load(f); lab = z["labels"].astype(bool); att = z["attacks"]
    if not lab.any():
        continue
    k = f.split("scores-")[1][:-4]; out[k] = {}
    for v in ("V10", "V19", "V19id"):
        tri = z[f"tier_{v}"] * 1e6 + np.clip(z["learned"], 0, 1e5)
        m, se = rand_adp(tri, lab, att, N, rng)
        out[k][v] = {"stable": adp_curve(lab, att, np.argsort(-tri, kind="stable")), "rand": m, "se": se}
    print(f"{k:34s} " + "  ".join(f"{v} {out[k][v]['rand']:.3f}" for v in out[k]), flush=True)
json.dump(out, open(f"{D}/adp_rand.json", "w"), indent=1)
