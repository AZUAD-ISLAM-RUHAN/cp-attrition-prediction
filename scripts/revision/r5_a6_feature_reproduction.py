"""
r5_a6_feature_reproduction.py  (reviewer items A6 and B3)
Recomputes the released features of each cohort account from its submission and rating history retrieved again
from the public Codeforces API (cut at T_obs) with the feature code of r0_rebuild_from_raw_jsonl.py, and reports
the share of accounts whose recomputed value equals the released one (to the released rounding).
Inactive accounts made no submissions between their June retrieval and T_obs, so for them the comparison is exact;
active accounts can differ because they kept submitting after their own retrieval (22-23 June).
Usage: python scripts/revision/r5_a6_feature_reproduction.py --features-with-handles <private csv> --cohort-csv <private> --refetched <jsonl>
Writes results/r5_a6_feature_reproduction.json (counts only, no handles).
"""
import argparse, csv, json, os, sys
import pandas as pd
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r0_rebuild_from_raw_jsonl import features
ap = argparse.ArgumentParser()
ap.add_argument("--features-with-handles", required=True); ap.add_argument("--cohort-csv", required=True); ap.add_argument("--refetched", required=True)
a = ap.parse_args()
T = datetime(2026, 6, 23, 13, 44, 17, tzinfo=timezone.utc).timestamp()
lab = {r["handle"]: int(r["label"]) for r in csv.DictReader(open(a.cohort_csv))}
priv, pub = pd.read_csv(a.features_with_handles), pd.read_csv("data/cf_attrition_features.csv")
pub["real"] = priv.handle.values; P = pub.set_index("real")
TOL = {"acceptance_rate": 0.0006, "math_solve_rate": 0.0006, "ds_solve_rate": 0.0006, "upsolves_per_contest": 0.0006,
       "avg_struggle_minutes": 0.051, "post_drop_recovery": 0.051, "total_problems_solved": 0, "total_submissions": 0, "total_contests": 0}
res = {}
for grp, name in ((1, "attrition"), (0, "active")):
    ok = {c: 0 for c in TOL}; n = 0; seen = set()
    for line in open(a.refetched, encoding="utf-8"):
        try: o = json.loads(line)
        except Exception: continue
        if o.get("status") != "ok" or lab.get(o["handle"]) != grp or o["handle"] in seen: continue
        seen.add(o["handle"])                                                  # a resumed retrieval can repeat a record
        f = features(o["submissions"], o["rating"], T + 1)
        if f is None: continue
        r = P.loc[o["handle"]]; n += 1
        for c, tol in TOL.items():
            v = f[c] if f.get(c) is not None else f["acceptance_rate"]       # tag rate falls back to the overall rate, as released
            ok[c] += abs(v - r[c]) <= tol + 1e-9
    res[name] = {"accounts_compared": n, "share_reproducing_released_value": {c: round(ok[c] / n, 4) for c in TOL}}
os.makedirs("results", exist_ok=True); json.dump(res, open("results/r5_a6_feature_reproduction.json", "w"), indent=1); print(json.dumps(res, indent=1))
