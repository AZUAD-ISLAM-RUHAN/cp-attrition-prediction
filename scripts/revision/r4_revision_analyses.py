"""r4_revision_analyses.py - analyses requested in the reviewer report of 8 November 2026 (AJSE Paper 1999), Part B.
Produces every number of the revised (v3) manuscript that does not need the raw API records.

Design (fixed before running):
  cohort   : accounts passing the data-quality rule (r3), peak rating < 1500 (rating restriction);
             active = last submission < 3 months before T_obs; attrition = no submission for >= 3 months.
             ALL eligible active accounts are used (no random draw of actives); class imbalance is handled by
             reporting threshold-free metrics (ROC-AUC, PR-AUC) and balanced accuracy.
  features : the 8 window-invariant features of r3 Spec D.
  models   : two pre-specified models, logistic regression (LR) and random forest (RF, 200 trees);
             repeated stratified 5-fold CV (5 repeats); 95% CIs by bootstrap over accounts of the
             out-of-fold predictions (2,000 resamples). Metrics are computed per repeat (each account
             predicted once, by a model not trained on it) and averaged; averaging predictions across repeats would act
             as an ensemble and inflate the estimate.
  effects  : rank-biserial r = P(attrition > active) - P(attrition < active) (positive: higher in the attrition
             group), bootstrap 95% CI, Mann-Whitney p and Holm-adjusted p (both reported, labelled).
Sections : B0 cohort and balance | B7 primary models | B2 balanced resamples | B3 data-quality rules |
           B4 attrition definitions | B5 account-age matching | B6 ablation and importance | descriptives.
Outputs  : results/r4_results.json, results/r4_report.md, results/r4_oof_predictions.csv
Run      : python scripts/revision/r4_revision_analyses.py [--fast]
"""
import json, sys, time, warnings
import numpy as np, pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, RepeatedStratifiedKFold
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, balanced_accuracy_score
from sklearn.inspection import permutation_importance
from sklearn.calibration import calibration_curve
warnings.filterwarnings("ignore")
FAST = "--fast" in sys.argv
SEED = 42; N_REP = 2 if FAST else 5; N_BOOT = 300 if FAST else 2000; N_RES = 10 if FAST else 50; N_SUB = 5 if FAST else 20
FEAT = ["math_solve_rate", "ds_solve_rate", "acceptance_rate", "avg_struggle_minutes",
        "upsolves_per_contest", "post_drop_recovery", "editorial_dependency_index", "solved_per_contest"]
WINDOW_DEP = ["contests_per_month", "problems_solved_per_month", "account_age_months", "total_contests"]
NICE = {"math_solve_rate": "Math-tag acceptance rate", "ds_solve_rate": "Data-structure acceptance rate",
        "acceptance_rate": "Overall acceptance rate", "avg_struggle_minutes": "Struggle time (min)",
        "upsolves_per_contest": "Upsolves per contest", "post_drop_recovery": "Post-drop recovery",
        "editorial_dependency_index": "Editorial dependency index", "solved_per_contest": "Problems solved per contest",
        "contests_per_month": "Rated contests per month", "problems_solved_per_month": "Problems solved per month",
        "account_age_months": "Account age (months)", "total_contests": "Rated contests (total)",
        "subs_per_contest": "Submissions per contest"}
R, MD, T0 = {"settings": {"seed": SEED, "cv": f"repeated stratified 5-fold x {N_REP}", "bootstrap": N_BOOT,
                          "balanced_resamples": N_RES, "fast": FAST, "features": FEAT}}, [], time.time()
def md(s=""): MD.append(s); print(s, flush=True)
def rnd(x, k=6): return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), k)

# ------------------------------------------------------------------ data
raw = pd.read_csv("data/cf_attrition_features.csv")
q1 = raw.total_submissions < raw.total_contests
q2 = (~q1) & (raw.contests_per_month > 15)
def add(d):
    d = d.copy()
    d["editorial_dependency_index"] = d.upsolves_per_contest * d.avg_struggle_minutes
    d["solved_per_contest"] = d.total_problems_solved / d.total_contests
    d["subs_per_contest"] = d.total_submissions / d.total_contests
    return d
raw = add(raw); clean = raw[~(q1 | q2)].copy()
def cohort(d, cut=1500, inactive_min=3.0):
    A = d[(d.months_since_last_submission < 3.0) & (d.status_proxy == "Active") & (d.max_rating < cut)].assign(label=0)
    S = d[(d.status_proxy == "Stopped") & (d.months_since_last_submission >= inactive_min) & (d.max_rating < cut)].assign(label=1)
    return pd.concat([A, S], ignore_index=True)
# note: status_proxy uses the unrounded idle time (>= 3 x 30 days); months_since_last_submission is rounded to 0.1,
# so 7 active accounts show 3.0 (idle 2.95-2.99). Actives are therefore selected by status_proxy, not by the rounded value.
def cohort_status(d, cut=1500, inactive_min=3.0):
    A = d[(d.status_proxy == "Active") & (d.max_rating < cut)].assign(label=0)
    S = d[(d.status_proxy == "Stopped") & (d.months_since_last_submission >= inactive_min) & (d.max_rating < cut)].assign(label=1)
    return pd.concat([A, S], ignore_index=True)
C = cohort_status(clean)
md("# r4 revision analyses (reviewer report of 8 Nov 2026)\n")
md(f"## B0 Cohort\n\nPrimary cohort: {len(C)} accounts = {(C.label==0).sum()} active + {(C.label==1).sum()} attrition (peak < 1500, after the data-quality rule)")
a, s = C[C.label == 0].max_rating, C[C.label == 1].max_rating
R["cohort"] = {"n": len(C), "active": int((C.label == 0).sum()), "attrition": int((C.label == 1).sum()),
               "prevalence": rnd((C.label == 1).mean()),
               "peak_rating": {"active_median": rnd(a.median()), "attrition_median": rnd(s.median()),
                               "active_mean": rnd(a.mean()), "attrition_mean": rnd(s.mean()),
                               "smd": rnd((a.mean() - s.mean()) / np.sqrt((a.var() + s.var()) / 2)),
                               "ks_D": rnd(stats.ks_2samp(a, s).statistic), "ks_p": float(stats.ks_2samp(a, s).pvalue)},
               "e4_rule": "inactive = (T_obs - last submission) / 30 days >= 3 (i.e. >= 90 days), applied to the unrounded value; "
                          "the released column months_since_last_submission is rounded to 0.1",
               "e4_rounded_3_0": {k: int(v) for k, v in raw[raw.months_since_last_submission == 3.0].status_proxy.value_counts().items()}}
md(f"- peak rating: {R['cohort']['peak_rating']}")

# ------------------------------------------------------------------ helpers
def models():
    return {"LR": LogisticRegression(max_iter=2000, random_state=SEED),
            "RF": RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=-1)}
def pipe(m): return Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler()), ("m", m)])
def oof(d, feats, mname, reps=N_REP, seed=SEED, importance=False):
    """repeated stratified 5-fold CV. Returns per-fold AUCs, out-of-fold predictions (one row per repeat), fold importances."""
    X, y = d[feats].values, d.label.values
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=reps, random_state=seed)
    P = np.zeros((reps, len(y))); aucs, imps = [], []
    for k, (tr, te) in enumerate(cv.split(X, y)):
        p_ = pipe(models()[mname]).fit(X[tr], y[tr]); pr = p_.predict_proba(X[te])[:, 1]
        P[k // 5, te] = pr; aucs.append(roc_auc_score(y[te], pr))
        if importance:
            pi = permutation_importance(p_, X[te], y[te], scoring="roc_auc", n_repeats=5, random_state=SEED, n_jobs=1)
            imps.append(pi.importances_mean)
    return np.array(aucs), P, (np.array(imps) if importance else None)        # P: one row of out-of-fold predictions per repeat
def boot_auc(y, p, n=N_BOOT, fn=roc_auc_score):
    rng = np.random.default_rng(SEED); v = []
    for _ in range(n):
        ix = rng.integers(0, len(y), len(y))
        if y[ix].min() != y[ix].max(): v.append(fn(y[ix], p[ix]))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))
def quick_auc(d, feats, mname="RF", reps=1, seed=SEED):
    return float(oof(d, feats, mname, reps=reps, seed=seed)[0].mean())

# ------------------------------------------------------------------ B7 primary models
md("\n## B7 Primary models (all eligible accounts, repeated 5-fold CV)\n")
y = C.label.values; prev = y.mean(); R["models"] = {}; OOFP = {}
for mname in ["LR", "RF"]:
    aucs, PP, imps = oof(C, FEAT, mname, importance=(mname == "RF"))
    OOFP[mname] = PP[0]                                                  # repeat 1: one honest prediction per account
    per = []
    for p in PP:
        lo, hi = boot_auc(y, p); aplo, aphi = boot_auc(y, p, fn=average_precision_score)
        thr = np.quantile(p, 1 - prev)                                   # flag the same share as the base rate
        per.append([roc_auc_score(y, p), lo, hi, average_precision_score(y, p), aplo, aphi, brier_score_loss(y, p),
                    balanced_accuracy_score(y, (p >= thr).astype(int))])
    per = np.array(per).mean(0)
    frac, mean_pred = calibration_curve(y, PP[0], n_bins=10, strategy="quantile")
    R["models"][mname] = {"auc_oof": rnd(per[0]), "auc_ci95": [rnd(per[1]), rnd(per[2])],
                          "auc_fold_mean": rnd(aucs.mean()), "auc_fold_sd": rnd(aucs.std()),
                          "auc_fold_p2_5": rnd(np.percentile(aucs, 2.5)), "auc_fold_p97_5": rnd(np.percentile(aucs, 97.5)),
                          "pr_auc": rnd(per[3]), "pr_auc_ci95": [rnd(per[4]), rnd(per[5])], "pr_auc_baseline": rnd(prev),
                          "brier": rnd(per[6]), "brier_baseline": rnd(prev * (1 - prev)),
                          "balanced_accuracy_at_base_rate": rnd(per[7]),
                          "note": "out-of-fold metrics computed per repeat and averaged over repeats; CI = bootstrap bounds averaged over repeats",
                          "calibration_repeat1": {"mean_predicted": [rnd(v, 4) for v in mean_pred], "observed": [rnd(v, 4) for v in frac]}}
    if imps is not None:
        R["importance_folds"] = {f: {"mean": rnd(imps[:, i].mean()), "sd": rnd(imps[:, i].std()),
                                     "p2_5": rnd(np.percentile(imps[:, i], 2.5)), "p97_5": rnd(np.percentile(imps[:, i], 97.5)),
                                     "share_of_folds_ranked_first": rnd((imps.argmax(1) == i).mean())} for i, f in enumerate(FEAT)}
    md(f"- {mname}: {R['models'][mname]}")
# class weights do not change the picture (AUC is threshold-free); checked once for the record
aw, _, _ = oof(C, FEAT, "RF", reps=1)
R["rf_class_weight_check"] = {"auc_without_weights_1rep": rnd(aw.mean()),
                              "auc_with_balanced_weights_1rep": rnd(np.mean([roc_auc_score(C.label.values[te], Pipeline([("i", SimpleImputer(strategy="median")), ("m", RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=-1, class_weight="balanced"))]).fit(C[FEAT].values[tr], C.label.values[tr]).predict_proba(C[FEAT].values[te])[:, 1]) for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED).split(C[FEAT], C.label)]))}
R["n_models_compared_history"] = ("Across the submission history the authors compared 9 classifiers in 4 feature specifications "
                                  "(36 configurations, r3) and 9 classifiers in 2 specifications earlier (r1). This revision pre-specifies "
                                  "two models (LR, RF) and reports both; selecting the best of many inflates the apparent AUC.")
pd.DataFrame({"label": y, "p_lr": OOFP["LR"], "p_rf": OOFP["RF"]}).to_csv("results/r4_oof_predictions.csv", index=False)
md(f"- class-weight check: {R['rf_class_weight_check']}  [{time.time()-T0:.0f}s]")

# ------------------------------------------------------------------ descriptives (Table II), sign rule fixed
md("\n## Descriptives (all eligible accounts; r > 0: higher in the attrition group)\n")
def rb(x1, x0):                                    # x1 attrition, x0 active
    U = stats.mannwhitneyu(x1, x0, alternative="two-sided")
    return 2 * U.statistic / (len(x1) * len(x0)) - 1, U.pvalue
desc, rng = [], np.random.default_rng(SEED)
for f in FEAT + WINDOW_DEP + ["subs_per_contest"]:
    x1, x0 = C.loc[C.label == 1, f].dropna().values, C.loc[C.label == 0, f].dropna().values
    r, p = rb(x1, x0); bs = []
    for _ in range(N_BOOT // 2):
        bs.append(rb(rng.choice(x1, len(x1)), rng.choice(x0, len(x0)))[0])
    desc.append({"feature": f, "label": NICE[f], "window_dependent": f in WINDOW_DEP, "in_model": f in FEAT,
                 "active_median": rnd(np.median(x0)), "active_q1": rnd(np.percentile(x0, 25)), "active_q3": rnd(np.percentile(x0, 75)),
                 "attr_median": rnd(np.median(x1)), "attr_q1": rnd(np.percentile(x1, 25)), "attr_q3": rnd(np.percentile(x1, 75)),
                 "r": rnd(r), "r_ci95": [rnd(np.percentile(bs, 2.5)), rnd(np.percentile(bs, 97.5))], "p": float(p)})
ps = np.array([d["p"] for d in desc]); order = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
for k, i in enumerate(order): run = max(run, min(1, (m - k) * ps[i])); adj[i] = run
for d, a_ in zip(desc, adj): d["p_holm"] = float(a_)
R["descriptives"] = desc
for d in desc: md(f"- {d['label']}: active {d['active_median']:.3f} vs attrition {d['attr_median']:.3f}; r = {d['r']:.3f} {d['r_ci95']}; p {d['p']:.2g}, Holm {d['p_holm']:.2g}")

# ------------------------------------------------------------------ B2 balanced resamples
md(f"\n## B2 Balanced resamples ({N_RES} random draws of 908 actives)\n")
A_all, S_all = C[C.label == 0], C[C.label == 1]; res = {"LR": [], "RF": []}
for s in range(N_RES):
    d = pd.concat([A_all.sample(n=len(S_all), random_state=s), S_all], ignore_index=True)
    for mname in res: res[mname].append(quick_auc(d, FEAT, mname))
R["b2_balanced_resamples"] = {mname: {"mean": rnd(np.mean(v)), "sd": rnd(np.std(v)), "min": rnd(np.min(v)), "max": rnd(np.max(v)),
                                      "p2_5": rnd(np.percentile(v, 2.5)), "p97_5": rnd(np.percentile(v, 97.5)),
                                      "seed42": rnd(v[42]) if len(v) > 42 else None,
                                      "seed42_rank_from_top": int((np.array(v) > v[42]).sum()) + 1 if len(v) > 42 else None,
                                      "values": [rnd(x, 4) for x in v]} for mname, v in res.items()}
md(f"- {({k: {kk: vv for kk, vv in v.items() if kk != 'values'} for k, v in R['b2_balanced_resamples'].items()})}  [{time.time()-T0:.0f}s]")

# ------------------------------------------------------------------ B3 data-quality rules
md("\n## B3 Incomplete histories and stricter rules\n")
spc = {g: raw.loc[(raw.status_proxy == g) & ~(q1 | q2), "subs_per_contest"] for g in ["Active", "Stopped"]}
R["b3"] = {"dq_removed": int((q1 | q2).sum()), "dq_removed_active": int(((q1 | q2) & (raw.status_proxy == "Active")).sum()),
           "dq_removed_pct": rnd(100 * (q1 | q2).mean()),
           "q1_fewer_subs_than_contests": int(q1.sum()), "q2_over_15_contests_per_month": int(q2.sum()),
           "subs_per_contest_cohort": {g: {"median": rnd(C.loc[C.label == l, "subs_per_contest"].median()),
                                           "q1": rnd(C.loc[C.label == l, "subs_per_contest"].quantile(.25)),
                                           "q3": rnd(C.loc[C.label == l, "subs_per_contest"].quantile(.75)),
                                           "lt2": int((C.loc[C.label == l, "subs_per_contest"] < 2).sum()),
                                           "lt3": int((C.loc[C.label == l, "subs_per_contest"] < 3).sum())} for g, l in [("active", 0), ("attrition", 1)]},
           "rules": {}}
for name, d in [("R0: published rule (subs >= contests; <= 15 contests/month)", C),
                ("R1: R0 + at least 2 submissions per contest", C[C.subs_per_contest >= 2]),
                ("R2: R0 + at least 3 submissions per contest", C[C.subs_per_contest >= 3]),
                ("R3: R0 + at least 5 submissions per contest", C[C.subs_per_contest >= 5])]:
    aucs, p, _ = oof(d, FEAT, "RF", reps=2); lr_, _, _ = oof(d, FEAT, "LR", reps=2)
    R["b3"]["rules"][name] = {"n": len(d), "active": int((d.label == 0).sum()), "attrition": int((d.label == 1).sum()),
                              "rf_auc": rnd(aucs.mean()), "rf_auc_sd": rnd(aucs.std()), "lr_auc": rnd(lr_.mean()), "lr_auc_sd": rnd(lr_.std())}
    md(f"- {name}: {R['b3']['rules'][name]}")
md(f"[{time.time()-T0:.0f}s]")

# ------------------------------------------------------------------ B4 attrition definitions
md("\n## B4 Definitions of attrition (inactivity x rating cut-off)\n")
R["b4"] = []
for cut in [1400, 1500, 1600]:
    for mi in [3.0, 6.0, 12.0]:
        d = cohort_status(clean, cut=cut, inactive_min=mi)
        aucs, _, _ = oof(d, FEAT, "RF", reps=2); lr_, _, _ = oof(d, FEAT, "LR", reps=2)
        x1, x0 = d.loc[d.label == 1, "solved_per_contest"], d.loc[d.label == 0, "solved_per_contest"]
        R["b4"].append({"rating_cut": cut, "inactive_months_min": mi, "active": int((d.label == 0).sum()), "attrition": int((d.label == 1).sum()),
                        "rf_auc": rnd(aucs.mean()), "rf_auc_sd": rnd(aucs.std()), "lr_auc": rnd(lr_.mean()), "lr_auc_sd": rnd(lr_.std()),
                        "r_solved_per_contest": rnd(rb(x1.values, x0.values)[0])})
        md(f"- {R['b4'][-1]}")
md(f"[{time.time()-T0:.0f}s]")

# ------------------------------------------------------------------ B5 account age and contests
md("\n## B5 Matching on account age and number of contests\n")
Z = lambda d: np.c_[np.log1p(d.account_age_months), np.log1p(d.total_contests)]
mu, sd = Z(C).mean(0), Z(C).std(0); zp, zs = (Z(A_all) - mu) / sd, (Z(S_all) - mu) / sd
b5 = []
for s in range(N_SUB):
    used = np.zeros(len(A_all), bool); idx = []; order = np.random.default_rng(s).permutation(len(S_all))
    for i in order:
        dist = ((zp - zs[i]) ** 2).sum(1); dist[used] = np.inf; j = int(dist.argmin()); used[j] = True; idx.append(j)
    d = pd.concat([A_all.iloc[idx], S_all], ignore_index=True)
    b5.append((quick_auc(d, FEAT, "RF", seed=s), quick_auc(d, FEAT, "LR", seed=s),
               d.loc[d.label == 0, "account_age_months"].median(), d.loc[d.label == 0, "total_contests"].median()))
b5 = np.array(b5)
R["b5"] = {"before": {"age_median_active": rnd(A_all.account_age_months.median()), "age_median_attrition": rnd(S_all.account_age_months.median()),
                      "contests_median_active": rnd(A_all.total_contests.median()), "contests_median_attrition": rnd(S_all.total_contests.median())},
           "after_matching": {"age_median_active": rnd(np.median(b5[:, 2])), "contests_median_active": rnd(np.median(b5[:, 3]))},
           "rf_auc_mean": rnd(b5[:, 0].mean()), "rf_auc_min": rnd(b5[:, 0].min()), "rf_auc_max": rnd(b5[:, 0].max()),
           "lr_auc_mean": rnd(b5[:, 1].mean()), "lr_auc_min": rnd(b5[:, 1].min()), "lr_auc_max": rnd(b5[:, 1].max()), "n_matchings": N_SUB}
md(f"- {R['b5']}  [{time.time()-T0:.0f}s]")

# ------------------------------------------------------------------ B6 ablation (paired folds) and correlation
md("\n## B6 Ablation of the two constructed features\n")
abl = {}
for name, feats in [("all 8", FEAT), ("without EDI", [f for f in FEAT if f != "editorial_dependency_index"]),
                    ("without solved_per_contest", [f for f in FEAT if f != "solved_per_contest"]),
                    ("without both", [f for f in FEAT if f not in ("editorial_dependency_index", "solved_per_contest")])]:
    abl[name] = {m: oof(C, feats, m)[0] for m in ["LR", "RF"]}
R["b6_ablation"] = {name: {m: {"auc": rnd(v.mean()), "delta_vs_all": rnd((v - abl["all 8"][m]).mean()),
                               "delta_sd_over_folds": rnd((v - abl["all 8"][m]).std()),
                               "delta_p2_5": rnd(np.percentile(v - abl["all 8"][m], 2.5)), "delta_p97_5": rnd(np.percentile(v - abl["all 8"][m], 97.5))}
                           for m, v in d.items()} for name, d in abl.items()}
for k, v in R["b6_ablation"].items(): md(f"- {k}: {v}")
rho = C[FEAT].corr(method="spearman")
R["b6_spearman"] = {f"{a}~{b}": rnd(rho.loc[a, b], 3) for i, a in enumerate(FEAT) for b in FEAT[i + 1:] if abs(rho.loc[a, b]) >= 0.4}
md(f"- feature pairs with |Spearman rho| >= 0.4: {R['b6_spearman']}  [{time.time()-T0:.0f}s]")

json.dump(R, open("results/r4_results.json", "w"), indent=1)
open("results/r4_report.md", "w").write("\n".join(MD))
md(f"\nwrote results/r4_results.json, results/r4_report.md, results/r4_oof_predictions.csv  [{time.time()-T0:.0f}s]")
