"""
r5_b1_pre_inactivity.py  (reviewer item B1, with B3 and E4)
===========================================================
B1: "Redo the main model using only activity from a fixed period before quitting, for example the 6 or 12 months
ending 3 months before the last submission. For active users, use a matching period from their own history."

Works on the raw API records written by 01_collect_and_build_features.ipynb (users_info.jsonl, users_dynamic.jsonl).
Cohort and label exactly as in the paper (r4): viability gate, data-quality rule, peak rating < 1500, label =
no submission for >= 3 months of 30 days at T_obs (unrounded). For EVERY account (both groups) the window ends
3 months before that account's own last submission and covers the previous 6 or 12 months; the eight model
features are recomputed from that window only (r0_rebuild_from_raw_jsonl.features), and the two pre-specified
models (LR, RF) are evaluated with the same repeated 5-fold cross-validation as r4. Effect sizes (rank-biserial r,
bootstrap CI, Holm) are reported for every feature.

Also writes the B3 completeness audit for the attrition accounts and the E4 unrounded inactivity values.
Writes only aggregates (no handles): results/r5_b1_results.json and results/r5_b1_report.md
Usage: python scripts/revision/r5_b1_pre_inactivity.py --raw-dir <folder> [--t-obs 2026-06-20T00:00:00Z] [--fast]
"""
import argparse, json, os, sys, statistics
from datetime import datetime, timezone
import numpy as np
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r0_rebuild_from_raw_jsonl import load_jsonl, features            # same feature code as the fixed-window audit

MONTH, MAX_RATING, MIN_CONTESTS, SEED = 30 * 24 * 3600, 2400, 5, 42
FEAT = ["math_solve_rate", "ds_solve_rate", "acceptance_rate", "avg_struggle_minutes",
        "upsolves_per_contest", "post_drop_recovery", "editorial_dependency_index", "solved_per_contest"]

def window_features(subs, rating, t_start, t_end):
    s = [x for x in subs if x["creationTimeSeconds"] >= t_start]
    r = [c for c in rating if c["ratingUpdateTimeSeconds"] >= t_start]
    f = features(s, r, t_end)          # filters < t_end; None if < 5 rated contests or no accepted submission
    if f is not None:
        acc = f["acceptance_rate"]                                    # paper's rule: tag rate falls back to overall rate
        for k in ("math_solve_rate", "ds_solve_rate"):
            if f[k] is None: f[k] = acc
    return f

def cv_models(X, y, reps):
    out = {}
    for name, m in {"LR": LogisticRegression(max_iter=2000, random_state=SEED),
                    "RF": RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=-1)}.items():
        cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=reps, random_state=SEED)
        P = np.zeros((reps, len(y))); folds = []
        for k, (tr, te) in enumerate(cv.split(X, y)):
            p = Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler()), ("m", m)]).fit(X[tr], y[tr])
            P[k // 5, te] = p.predict_proba(X[te])[:, 1]; folds.append(roc_auc_score(y[te], P[k // 5, te]))
        rng = np.random.default_rng(SEED); per = []
        for p in P:
            bs = [roc_auc_score(y[ix], p[ix]) for ix in (rng.integers(0, len(y), len(y)) for _ in range(1000)) if y[ix].min() != y[ix].max()]
            per.append([roc_auc_score(y, p), np.percentile(bs, 2.5), np.percentile(bs, 97.5),
                        average_precision_score(y, p), brier_score_loss(y, p)])
        per = np.array(per).mean(0)
        out[name] = {"auc": round(per[0], 4), "auc_ci95": [round(per[1], 4), round(per[2], 4)], "fold_sd": round(float(np.std(folds)), 4),
                     "pr_auc": round(per[3], 4), "pr_auc_baseline": round(float(y.mean()), 4),
                     "brier": round(per[4], 4), "brier_baseline": round(float(y.mean() * (1 - y.mean())), 4)}
    return out

def effect_sizes(D, y):
    rows, rng = [], np.random.default_rng(SEED)
    for j, f in enumerate(FEAT):
        x1, x0 = D[y == 1, j], D[y == 0, j]
        U = stats.mannwhitneyu(x1, x0, alternative="two-sided")
        r = 2 * U.statistic / (len(x1) * len(x0)) - 1
        bs = []
        for _ in range(500):
            a, b = rng.choice(x1, len(x1)), rng.choice(x0, len(x0))
            bs.append(2 * stats.mannwhitneyu(a, b).statistic / (len(a) * len(b)) - 1)
        rows.append({"feature": f, "r": round(r, 4), "r_ci95": [round(np.percentile(bs, 2.5), 4), round(np.percentile(bs, 97.5), 4)],
                     "p": U.pvalue, "median_attrition": round(float(np.median(x1)), 3), "median_active": round(float(np.median(x0)), 3)})
    order = np.argsort([x["p"] for x in rows]); m = len(rows); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * rows[i]["p"])); rows[i]["p_holm"] = run
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", required=True); ap.add_argument("--t-obs", default=None); ap.add_argument("--fast", action="store_true")
    ap.add_argument("--dyn-file", default=None, help="submission/rating records (default: <raw-dir>/users_dynamic.jsonl)")
    ap.add_argument("--cohort-csv", default=None, help="handle,label of the published cohort; if given, cohort and labels are taken from it")
    a = ap.parse_args(); reps = 2 if a.fast else 5
    info = {h: o["info"] for h, o in load_jsonl(os.path.join(a.raw_dir, "users_info.jsonl")).items()}
    dyn = load_jsonl(a.dyn_file or os.path.join(a.raw_dir, "users_dynamic.jsonl"))
    fixed = None
    if a.cohort_csv:
        import csv
        fixed = {r["handle"]: int(r["label"]) for r in csv.DictReader(open(a.cohort_csv))}
    t_obs = (datetime.fromisoformat(a.t_obs.replace("Z", "+00:00")).timestamp() if a.t_obs
             else max(s["creationTimeSeconds"] for d in dyn.values() for s in (d.get("submissions") or [])))
    cohort, e4, b3 = [], [], {"attrition_accounts": 0, "fewer_submissions_than_rated_contests": 0,
                              "rated_contests_before_first_retrieved_submission": 0, "hit_10000_submission_cap": 0}
    missing = 0
    if fixed is not None:
        for h, y in fixed.items():
            d = dyn.get(h)
            if not d or not d.get("submissions") or not d.get("rating"): missing += 1; continue
            subs, rating = d["submissions"], d["rating"]; times = [s["creationTimeSeconds"] for s in subs]
            if y:
                b3["attrition_accounts"] += 1
                b3["fewer_submissions_than_rated_contests"] += int(len(subs) < len(rating))
                b3["rated_contests_before_first_retrieved_submission"] += int(min(c["ratingUpdateTimeSeconds"] for c in rating) < min(times))
            cohort.append((subs, rating, max(times), y))
    for h, d in (dyn.items() if fixed is None else []):
        inf = info.get(h); subs, rating = d.get("submissions") or [], d.get("rating") or []
        if inf is None or d.get("suspicious"): continue
        if not (0 < inf.get("rating", 0) < MAX_RATING) or len(rating) < MIN_CONTESTS: continue
        if not subs or not any(s.get("verdict") == "OK" for s in subs): continue
        times = [s["creationTimeSeconds"] for s in subs]; last = max(times)
        span = max((last - min(times)) / MONTH, 1)
        if len(subs) < len(rating) or len(rating) / span > 15: continue                  # data-quality rule
        if inf.get("maxRating", inf.get("rating", 0)) >= 1500: continue                  # peak < 1500
        idle = (t_obs - last) / MONTH; y = int(idle >= 3)
        if round(idle, 1) == 3.0: e4.append({"label": "attrition" if y else "active", "idle_months_unrounded": round(idle, 4)})
        if y:
            b3["attrition_accounts"] += 1
            b3["rated_contests_before_first_retrieved_submission"] += int(min(c["ratingUpdateTimeSeconds"] for c in rating) < min(times))
            b3["hit_10000_submission_cap"] += int(len(subs) >= 10000)
        cohort.append((subs, rating, last, y))
    res = {"T_obs_utc": datetime.fromtimestamp(t_obs, timezone.utc).isoformat(),
           "cohort": {"active": sum(1 - c[3] for c in cohort), "attrition": sum(c[3] for c in cohort),
                      "source": "published cohort and labels (--cohort-csv)" if fixed is not None else "paper rules applied to the raw records",
                      "cohort_accounts_without_records": missing},
           "b3_attrition_completeness": b3, "e4_accounts_rounding_to_3_0": sorted(e4, key=lambda x: x["idle_months_unrounded"]),
           "windows": {}}
    for W in (6, 12):
        X, Y = [], []
        for subs, rating, last, y in cohort:
            t_end = last - 3 * MONTH                     # 3 months before the account's own last submission
            f = window_features(subs, rating, t_end - W * MONTH, t_end)
            if f is not None: X.append([f[k] for k in FEAT]); Y.append(y)
        X, Y = np.array(X, float), np.array(Y)
        w = {"n_active": int((Y == 0).sum()), "n_attrition": int(Y.sum()),
             "note": "accounts with at least 5 rated contests and one accepted submission inside the window"}
        if Y.sum() >= 20 and (Y == 0).sum() >= 20:
            w["models"] = cv_models(X, Y, reps); w["effect_sizes"] = effect_sizes(X, Y)
        res["windows"][f"{W}_months"] = w
    os.makedirs("results", exist_ok=True)
    json.dump(res, open("results/r5_b1_results.json", "w"), indent=1, default=float)
    L = [f"# B1 - features from the period before inactivity (T_obs {res['T_obs_utc']})", "",
         f"Cohort: {res['cohort']['active']} active, {res['cohort']['attrition']} attrition ({res['cohort']['source']}; accounts without records: {res['cohort']['cohort_accounts_without_records']}).", ""]
    for k, w in res["windows"].items():
        L.append(f"## Window: {k} ending 3 months before each account's last submission")
        L.append(f"Accounts with enough activity in the window: {w['n_active']} active, {w['n_attrition']} attrition")
        for m, v in w.get("models", {}).items():
            L.append(f"- {m}: ROC-AUC {v['auc']} [{v['auc_ci95'][0]}, {v['auc_ci95'][1]}], PR-AUC {v['pr_auc']} (base {v['pr_auc_baseline']}), Brier {v['brier']} (base {v['brier_baseline']})")
        for e in w.get("effect_sizes", []):
            L.append(f"  - {e['feature']}: r = {e['r']} [{e['r_ci95'][0]}, {e['r_ci95'][1]}], Holm p = {e['p_holm']:.3g}")
        L.append("")
    L += [f"B3 (attrition accounts): {b3}", f"E4 (accounts whose inactivity rounds to 3.0): {res['e4_accounts_rounding_to_3_0']}"]
    open("results/r5_b1_report.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))

if __name__ == "__main__":
    main()
