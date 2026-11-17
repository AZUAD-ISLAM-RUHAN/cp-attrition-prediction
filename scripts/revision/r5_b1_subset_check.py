"""
r5_b1_subset_check.py  (reviewer item B1)
The window analysis uses the accounts whose histories were retrieved again (all attrition accounts and part of the
active ones). This script fits the whole-history models of the paper (released features, same CV) on exactly those
accounts and on the full cohort, so that any effect of the subset on the result is visible. Adds the result to
results/r5_b1_results.json (no handles).
Usage: python scripts/revision/r5_b1_subset_check.py --features-with-handles <private csv> --cohort-csv <private> --refetched <jsonl>
"""
import argparse, csv, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r5_b1_pre_inactivity import cv_models, FEAT
ap = argparse.ArgumentParser(); ap.add_argument("--features-with-handles", required=True); ap.add_argument("--cohort-csv", required=True); ap.add_argument("--refetched", required=True)
a = ap.parse_args()
lab = {r["handle"]: int(r["label"]) for r in csv.DictReader(open(a.cohort_csv))}
got = set()
for line in open(a.refetched, encoding="utf-8"):
    try:
        o = json.loads(line)
        if o.get("status") == "ok": got.add(o["handle"])
    except Exception: pass
priv, pub = pd.read_csv(a.features_with_handles), pd.read_csv("data/cf_attrition_features.csv")
pub["real"] = priv.handle.values
pub["editorial_dependency_index"] = pub.upsolves_per_contest * pub.avg_struggle_minutes
pub["solved_per_contest"] = pub.total_problems_solved / pub.total_contests
# the cohort in exactly the order of r4_revision_analyses.py (active block, then attrition block), so the full-cohort
# result equals the paper's Table III
q1 = pub.total_submissions < pub.total_contests; q2 = (~q1) & (pub.contests_per_month > 15); cl = pub[~(q1 | q2)]
A = cl[(cl.status_proxy == "Active") & (cl.max_rating < 1500)].assign(label=0)
S = cl[(cl.status_proxy == "Stopped") & (cl.months_since_last_submission >= 3.0) & (cl.max_rating < 1500)].assign(label=1)
C = pd.concat([A, S], ignore_index=True); assert set(C.real) == set(lab)
out = {}
for name, d in (("full cohort", C), ("accounts retrieved again", C[C.real.isin(got)])):
    m = cv_models(d[FEAT].values.astype(float), d.label.values, 5)
    out[name] = {"active": int((d.label == 0).sum()), "attrition": int(d.label.sum()),
                 "LR_auc": m["LR"]["auc"], "LR_ci95": m["LR"]["auc_ci95"], "RF_auc": m["RF"]["auc"], "RF_ci95": m["RF"]["auc_ci95"]}
R = json.load(open("results/r5_b1_results.json")); R["subset_whole_history_check"] = out
json.dump(R, open("results/r5_b1_results.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1))
