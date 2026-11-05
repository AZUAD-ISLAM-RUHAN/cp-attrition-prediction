"""
r3_inquiry_reanalysis.py
========================
Re-analysis prepared in response to the AJSE Editorial Desk inquiry (Paper ID 1999,
notice dated 3 Nov 2026). Every number reported in the corrected manuscript is
produced by this script from the two files in data/. Nothing is typed by hand.

What it does (section numbers match the response letter):
  CF-1  Cohort flow with counts at every stage, and data-quality checks.
  CF-2  Rating-matched cohort (peak rating < 1500 in BOTH classes) with balance check.
  CF-3  Descriptive comparison recomputed ON THE MATCHED COHORT (medians, IQR,
        Mann-Whitney U, rank-biserial effect size + bootstrap CI, Holm & BH).
  CF-4  Activity-decay ("burnout") flag reported under its implemented definition.
  CF-5  Classifiers under three feature specifications, with trivial baselines,
        ROC-AUC, balanced accuracy, per-fold SD, permutation test, test-set CIs.
  CF-6  Feature importance (impurity and permutation) for the final specification.
  SV-1  Survey sample flow 96 -> 73 -> 64.
  SV-2  Item comparability across the questionnaire branches.
  SV-3  Group tests on comparable items only (exact / permutation p-values,
        effect sizes, CIs, Holm & BH).
  SV-4  Survey classifier on comparable items only, against trivial baselines.
  SV-5  Reproduction of the original Table 1 / Table II statistics, to document
        exactly how they arose.
Outputs: results/r3_results.json, results/r3_report.md, data/cf_matched_modelling_set.csv,
         data/survey_analysis_set_n64.csv  (figures: run r3_figures.py afterwards)

Run from the repository root:
    python scripts/revision/r3_inquiry_reanalysis.py
Environment used for the reported numbers: see results/r3_results.json["environment"].
"""
import json, os, sys, platform, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
import sklearn, xgboost as xgb, lightgbm as lgb
from sklearn.model_selection import (StratifiedKFold, RepeatedStratifiedKFold, train_test_split,
                                     cross_validate, permutation_test_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.dummy import DummyClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import (f1_score, accuracy_score, recall_score, precision_score,
                             roc_auc_score, balanced_accuracy_score)

SEED = 42
FAST = "--fast" in sys.argv          # fewer permutations / repeats for a quick check
N_PERM = 30 if FAST else 200
N_REP = 2 if FAST else 5
N_BOOT = 500 if FAST else 2000
os.makedirs("results", exist_ok=True)
R = {"environment": {"python": platform.python_version(), "numpy": np.__version__,
                     "pandas": pd.__version__, "scipy": __import__("scipy").__version__,
                     "scikit-learn": sklearn.__version__, "xgboost": xgb.__version__,
                     "lightgbm": lgb.__version__, "seed": SEED,
                     "n_permutations": N_PERM, "cv_repeats": N_REP, "n_bootstrap": N_BOOT}}
MD = []                               # markdown report lines
def md(s=""): MD.append(s); print(s)

# ----------------------------------------------------------------------------- helpers
def holm(p):
    p = np.asarray(p, float); m = len(p); o = np.argsort(p); adj = np.empty(m); run = 0
    for k, i in enumerate(o):
        run = max(run, (m - k) * p[i]); adj[i] = min(1, run)
    return adj
def bh(p):
    p = np.asarray(p, float); m = len(p); o = np.argsort(p)[::-1]; adj = np.empty(m); run = 1
    for k, i in enumerate(o):
        rank = m - k; run = min(run, p[i] * m / rank); adj[i] = run
    return adj
def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    ph = k / n; den = 1 + z**2 / n; c = (ph + z**2 / (2 * n)) / den
    h = z * np.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2)) / den
    return (c - h, c + h)
def newcombe(k1, n1, k2, n2):
    """95% CI for p1-p2 (Newcombe hybrid score method 10)."""
    p1, p2 = k1 / n1, k2 / n2; l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2)
    d = p1 - p2
    return (d - np.sqrt((p1 - l1)**2 + (u2 - p2)**2), d + np.sqrt((u1 - p1)**2 + (p2 - l2)**2))
def rank_biserial(a, b):
    """r = 1 - 2U/(n1 n2) with U for sample a; positive => a tends to be larger."""
    u = stats.mannwhitneyu(a, b, alternative="two-sided").statistic
    return 2 * u / (len(a) * len(b)) - 1
def boot_ci(fn, a, b, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed); a = np.asarray(a); b = np.asarray(b); out = []
    for _ in range(n):
        out.append(fn(rng.choice(a, len(a)), rng.choice(b, len(b))))
    return tuple(np.percentile(out, [2.5, 97.5]))
def fmt_p(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"
def r3(x): return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 6)

# =============================================================================
# CODEFORCES LAYER
# =============================================================================
raw = pd.read_csv("data/cf_attrition_features.csv")
md("# r3 re-analysis report\n")
md("## CF-1 Cohort flow and data-quality checks\n")
flow = {}
flow["rows_in_released_file"] = len(raw)
flow["note_collection_gate"] = ("Rows already passed the collection gate in 01_collect_and_build_features "
                                "(current rating >0 and <2400, >=5 rated contests, >=1 accepted submission). "
                                "Counts excluded by that gate are only recoverable from the raw JSONL files.")
flow["peak_rating_ge_2400_in_file"] = int((raw.max_rating >= 2400).sum())
flow["current_rating_ge_2400_in_file"] = int((raw.current_rating >= 2400).sum())
q1 = raw.total_submissions < raw.total_contests                 # logically impossible if complete
q2 = (~q1) & (raw.contests_per_month > 15)                      # >15 rated contests per month
raw["dq_fail_q1"] = q1; raw["dq_fail_q2"] = q2
flow["dq_q1_fewer_submissions_than_rated_contests"] = {s: int(q1[raw.status_proxy == s].sum()) for s in ["Active", "Stopped"]}
flow["dq_q2_more_than_15_contests_per_month"] = {s: int(q2[raw.status_proxy == s].sum()) for s in ["Active", "Stopped"]}
flow["max_contests_per_month_among_stopped"] = r3(raw.loc[raw.status_proxy == "Stopped", "contests_per_month"].max())
clean = raw[~(q1 | q2)].copy()
flow["rows_after_data_quality"] = len(clean)
for tag, d in [("all_rows", raw), ("after_dq", clean)]:
    A = d[d.status_proxy == "Active"]; S = d[d.status_proxy == "Stopped"]
    flow[tag] = {"active": len(A), "stopped": len(S),
                 "stopped_peak_lt1500_true_attrition": int((S.max_rating < 1500).sum()),
                 "stopped_peak_ge1500_intentional_exit_excluded": int((S.max_rating >= 1500).sum()),
                 "active_peak_lt1500_matched_pool": int((A.max_rating < 1500).sum()),
                 "active_peak_ge1500_excluded_by_matching": int((A.max_rating >= 1500).sum())}
R["cf_flow"] = flow
for k, v in flow.items(): md(f"- {k}: {v}")

FEAT_FULL = ["math_solve_rate", "ds_solve_rate", "upsolves_per_contest", "avg_struggle_minutes",
             "activity_trend_ratio", "post_drop_recovery", "contests_per_month",
             "problems_solved_per_month", "acceptance_rate", "account_age_months",
             "intensity_ratio", "editorial_dependency_index"]
FEAT_R1C = [f for f in FEAT_FULL if f not in ["account_age_months", "contests_per_month", "activity_trend_ratio"]]
# Consistent audit: drop every feature whose value depends on the length or the end of the
# observed activity window (account age; per-month rates normalised by the submission span;
# the second-half/first-half trend). Keep window-invariant proportions and per-contest ratios.
FEAT_D = ["math_solve_rate", "ds_solve_rate", "acceptance_rate", "avg_struggle_minutes",
          "upsolves_per_contest", "post_drop_recovery", "editorial_dependency_index",
          "solved_per_contest"]

def build(d, matched, n_per_class=None):
    A = d[d.status_proxy == "Active"].copy(); S = d[(d.status_proxy == "Stopped") & (d.max_rating < 1500)].copy()
    if matched: A = A[A.max_rating < 1500]
    A["label"] = 0; S["label"] = 1
    n = n_per_class or len(S)
    out = pd.concat([A.sample(n=n, random_state=SEED), S.sample(n=n, random_state=SEED) if n < len(S) else S],
                    ignore_index=True)
    out["intensity_ratio"] = out.problems_solved_per_month / (out.contests_per_month + 0.1)   # as implemented originally
    out["editorial_dependency_index"] = out.upsolves_per_contest * out.avg_struggle_minutes
    out["solved_per_contest"] = out.total_problems_solved / out.total_contests                # window-invariant IR
    return out

M = build(clean, matched=True)                  # primary cohort
M_unclean = build(raw, matched=True)            # = r1 Spec B/C cohort (for comparison)
U_orig = build(raw, matched=False)              # = original unmatched cohort (for comparison)
R["cf_cohorts"] = {"primary_matched_clean": {"n": len(M), "active": int((M.label == 0).sum()), "attrition": int((M.label == 1).sum())},
                   "matched_uncleaned_r1": {"n": len(M_unclean)}, "original_unmatched": {"n": len(U_orig)}}
md(f"\nPrimary cohort: n={len(M)} ({(M.label==0).sum()} active, {(M.label==1).sum()} true attrition)")
md(f"Correlation of implemented intensity_ratio with solved_per_contest in primary cohort: "
   f"Spearman rho={stats.spearmanr(M.intensity_ratio, M.solved_per_contest)[0]:.3f}")
R["ir_vs_solved_per_contest_spearman"] = r3(stats.spearmanr(M.intensity_ratio, M.solved_per_contest)[0])

# ---------------------------------------------------------------- CF-2 balance on peak rating
md("\n## CF-2 Rating balance\n")
bal = {}
for tag, d in [("original_unmatched", U_orig), ("primary_matched_clean", M)]:
    a, s = d[d.label == 0].max_rating, d[d.label == 1].max_rating
    smd = (a.mean() - s.mean()) / np.sqrt((a.var() + s.var()) / 2)
    ks = stats.ks_2samp(a, s)
    bal[tag] = {"active_peak_mean": r3(a.mean()), "active_peak_median": r3(a.median()),
                "attrition_peak_mean": r3(s.mean()), "attrition_peak_median": r3(s.median()),
                "standardised_mean_difference": r3(smd), "ks_D": r3(ks.statistic), "ks_p": float(ks.pvalue)}
    md(f"- {tag}: {bal[tag]}")
R["cf_balance"] = bal

# ---------------------------------------------------------------- CF-3 descriptives
md("\n## CF-3 Descriptive comparison (matched cohort)\n")
DESC = ["contests_per_month", "problems_solved_per_month", "avg_struggle_minutes", "math_solve_rate",
        "ds_solve_rate", "acceptance_rate", "upsolves_per_contest", "activity_trend_ratio",
        "post_drop_recovery", "solved_per_contest", "account_age_months"]
def describe(d, feats):
    rows = []
    for f in feats:
        a = d.loc[d.label == 0, f].values; s = d.loc[d.label == 1, f].values
        mw = stats.mannwhitneyu(a, s, alternative="two-sided")
        rb = rank_biserial(s, a)        # positive => attrition larger
        lo, hi = boot_ci(lambda x, y: rank_biserial(y, x), a, s)
        rows.append(dict(feature=f, active_median=np.median(a), active_q1=np.percentile(a, 25), active_q3=np.percentile(a, 75),
                         attr_median=np.median(s), attr_q1=np.percentile(s, 25), attr_q3=np.percentile(s, 75),
                         active_mean=a.mean(), attr_mean=s.mean(), U=mw.statistic, p=mw.pvalue,
                         r_rb=rb, r_lo=lo, r_hi=hi,
                         median_pct_diff=(np.median(s) - np.median(a)) / np.median(a) * 100 if np.median(a) != 0 else np.nan))
    t = pd.DataFrame(rows); t["p_holm"] = holm(t.p); t["p_bh"] = bh(t.p)
    return t
desc_M = describe(M, DESC); desc_U = describe(U_orig, DESC)
md("| feature | active median [IQR] | attrition median [IQR] | median diff % | r_rb (attr>act) [95% CI] | p | p_Holm |")
md("|---|---|---|---|---|---|---|")
for _, r in desc_M.iterrows():
    md(f"| {r.feature} | {r.active_median:.3g} [{r.active_q1:.3g}, {r.active_q3:.3g}] | {r.attr_median:.3g} [{r.attr_q1:.3g}, {r.attr_q3:.3g}] | "
       f"{r.median_pct_diff:.1f} | {r.r_rb:.3f} [{r.r_lo:.3f}, {r.r_hi:.3f}] | {fmt_p(r.p)} | {fmt_p(r.p_holm)} |")
md("\nSame statistics on the ORIGINAL unmatched cohort (for the response letter only):")
for _, r in desc_U.iterrows():
    md(f"- {r.feature}: mean {r.active_mean:.3f} vs {r.attr_mean:.3f}; median {r.active_median:.3g} vs {r.attr_median:.3g}; r_rb={r.r_rb:.3f}; p={fmt_p(r.p)}")
R["cf_descriptives_matched"] = desc_M.round(8).to_dict(orient="records")
R["cf_descriptives_original_unmatched"] = desc_U.round(8).to_dict(orient="records")
# reproduce the original headline means (unmatched, uncleaned) for the letter
R["original_headline_reproduced"] = {
    "contests_per_month_mean_active": r3(U_orig[U_orig.label == 0].contests_per_month.mean()),
    "contests_per_month_mean_attr": r3(U_orig[U_orig.label == 1].contests_per_month.mean()),
    "active_rows_failing_dq_in_original_sample": int((U_orig.label.eq(0) & (U_orig.dq_fail_q1 | U_orig.dq_fail_q2)).sum()),
    "contests_per_month_mean_active_excluding_dq_fail": r3(U_orig[(U_orig.label == 0) & ~(U_orig.dq_fail_q1 | U_orig.dq_fail_q2)].contests_per_month.mean()),
    "struggle_mean_active": r3(U_orig[U_orig.label == 0].avg_struggle_minutes.mean()),
    "struggle_mean_attr": r3(U_orig[U_orig.label == 1].avg_struggle_minutes.mean()),
    "burnout_pct_active": r3(U_orig[U_orig.label == 0].burnout_flag.mean() * 100),
    "burnout_pct_attr": r3(U_orig[U_orig.label == 1].burnout_flag.mean() * 100)}
md(f"\nOriginal headline values reproduced: {R['original_headline_reproduced']}")

# ---------------------------------------------------------------- CF-4 activity decay
md("\n## CF-4 Activity-decay flag\n")
md("Implemented definition: ATR = submissions in the second half of the user's own submission span / "
   "submissions in the first half; flag = ATR < 0.5. ATR is set to 1.0 when the first half is empty.")
def burn(d):
    a = d[d.label == 0]; s = d[d.label == 1]
    ka, na, ks_, ns = int(a.burnout_flag.sum()), len(a), int(s.burnout_flag.sum()), len(s)
    ct = np.array([[ks_, ns - ks_], [ka, na - ka]]); chi = stats.chi2_contingency(ct, correction=False)
    return {"active_k": ka, "active_n": na, "active_pct": r3(ka / na * 100), "active_ci": [r3(x * 100) for x in wilson(ka, na)],
            "attr_k": ks_, "attr_n": ns, "attr_pct": r3(ks_ / ns * 100), "attr_ci": [r3(x * 100) for x in wilson(ks_, ns)],
            "diff_pp": r3((ks_ / ns - ka / na) * 100), "diff_ci_pp": [r3(x * 100) for x in newcombe(ks_, ns, ka, na)],
            "chi2": r3(chi[0]), "p": float(chi[1]), "relative_risk": r3((ks_ / ns) / (ka / na)),
            "atr_fallback_1.0_active": int((a.activity_trend_ratio == 1.0).sum()),
            "atr_fallback_1.0_attr": int((s.activity_trend_ratio == 1.0).sum())}
R["cf_burnout"] = {"primary_matched_clean": burn(M), "original_unmatched": burn(U_orig)}
for k, v in R["cf_burnout"].items(): md(f"- {k}: {v}")
up = {}
for tag, d in [("primary_matched_clean", M), ("original_unmatched", U_orig)]:
    up[tag] = {}
    for lab, g in [("active", d[d.label == 0]), ("attrition", d[d.label == 1])]:
        x = g.upsolves_per_contest
        up[tag][lab] = {"zero_pct": r3((x == 0).mean() * 100), "lt_0.5_pct": r3((x < 0.5).mean() * 100),
                        "0.5_to_1_pct": r3(((x >= .5) & (x < 1)).mean() * 100), "1_to_2_pct": r3(((x >= 1) & (x < 2)).mean() * 100),
                        "ge_2_pct": r3((x >= 2).mean() * 100), "mean_1to5": r3(g.upsolves_per_contest_1to5.mean())}
R["cf_upsolving_bins"] = up
md(f"- upsolving bins: {up}")

# ---------------------------------------------------------------- CF-5 models
md("\n## CF-5 Classifiers\n")
def model_zoo(y):
    pw = (y == 0).sum() / (y == 1).sum()
    m = {"Logistic Regression": LogisticRegression(max_iter=1000, random_state=SEED, class_weight="balanced"),
         "Decision Tree": DecisionTreeClassifier(random_state=SEED, class_weight="balanced"),
         "Random Forest": RandomForestClassifier(n_estimators=200, random_state=SEED, class_weight="balanced", n_jobs=-1),
         "KNN": KNeighborsClassifier(n_neighbors=5),
         "SVM": SVC(probability=True, random_state=SEED, class_weight="balanced"),
         "XGBoost": xgb.XGBClassifier(n_estimators=200, random_state=SEED, scale_pos_weight=pw, eval_metric="logloss", verbosity=0, n_jobs=2),
         "LightGBM": lgb.LGBMClassifier(n_estimators=200, random_state=SEED, class_weight="balanced", verbose=-1, n_jobs=2),
         "MLP": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=SEED, early_stopping=True)}
    m["Soft-Voting Ensemble"] = VotingClassifier([
        ("lr", LogisticRegression(max_iter=1000, random_state=SEED, class_weight="balanced")),
        ("rf", RandomForestClassifier(n_estimators=200, random_state=SEED, class_weight="balanced", n_jobs=-1)),
        ("svm", SVC(probability=True, random_state=SEED, class_weight="balanced")),
        ("xgb", xgb.XGBClassifier(n_estimators=200, random_state=SEED, scale_pos_weight=pw, eval_metric="logloss", verbosity=0, n_jobs=2))],
        voting="soft")                                       # equal weights (sklearn default)
    m["Baseline: always 'attrition'"] = DummyClassifier(strategy="constant", constant=1)
    m["Baseline: random (stratified)"] = DummyClassifier(strategy="stratified", random_state=SEED)
    return m
SCORING = {"f1": "f1", "roc_auc": "roc_auc", "bal_acc": "balanced_accuracy", "acc": "accuracy"}

def evaluate(d, feats, cat=None, label="", test_bootstrap=True):
    cat = cat or []
    num = [f for f in feats if f not in cat]
    X, y = d[feats].copy(), d["label"].values
    tr = [("num", Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]), num)]
    if cat: tr.append(("cat", Pipeline([("i", SimpleImputer(strategy="most_frequent")), ("o", OneHotEncoder(handle_unknown="ignore"))]), cat))
    prep = ColumnTransformer(tr)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    cv5 = StratifiedKFold(5, shuffle=True, random_state=SEED)
    rcv = RepeatedStratifiedKFold(n_splits=5, n_repeats=N_REP, random_state=SEED)
    out = {}
    for name, clf in model_zoo(pd.Series(y)).items():
        pipe = Pipeline([("prep", prep), ("clf", clf)])
        a = cross_validate(pipe, Xtr, ytr, cv=cv5, scoring=SCORING)                 # original protocol (train part)
        b = cross_validate(pipe, X, y, cv=rcv, scoring=SCORING)                     # repeated CV, full cohort
        pipe.fit(Xtr, ytr); pr = pipe.predict(Xte)
        pp = pipe.predict_proba(Xte)[:, 1]
        res = {"cv5_train_f1_mean": r3(a["test_f1"].mean()), "cv5_train_f1_sd": r3(a["test_f1"].std()),
               "cv5_train_f1_folds": [r3(v) for v in a["test_f1"]],
               "cv5_train_auc_mean": r3(a["test_roc_auc"].mean()), "cv5_train_auc_sd": r3(a["test_roc_auc"].std()),
               "rcv_f1_mean": r3(b["test_f1"].mean()), "rcv_f1_sd": r3(b["test_f1"].std()),
               "rcv_auc_mean": r3(b["test_roc_auc"].mean()), "rcv_auc_sd": r3(b["test_roc_auc"].std()),
               "rcv_balacc_mean": r3(b["test_bal_acc"].mean()), "rcv_balacc_sd": r3(b["test_bal_acc"].std()),
               "test_acc": r3(accuracy_score(yte, pr)), "test_f1": r3(f1_score(yte, pr, zero_division=0)),
               "test_precision": r3(precision_score(yte, pr, zero_division=0)), "test_recall": r3(recall_score(yte, pr, zero_division=0)),
               "test_auc": r3(roc_auc_score(yte, pp)) if len(np.unique(pp)) > 1 else 0.5, "n_test": int(len(yte))}
        if test_bootstrap and not name.startswith("Baseline"):
            rng = np.random.default_rng(SEED); aucs, f1s = [], []
            for _ in range(N_BOOT):
                ix = rng.integers(0, len(yte), len(yte))
                if len(np.unique(yte[ix])) < 2: continue
                aucs.append(roc_auc_score(yte[ix], pp[ix])); f1s.append(f1_score(yte[ix], pr[ix], zero_division=0))
            res["test_auc_ci"] = [r3(v) for v in np.percentile(aucs, [2.5, 97.5])]
            res["test_f1_ci"] = [r3(v) for v in np.percentile(f1s, [2.5, 97.5])]
        out[name] = res
    md(f"\n### {label} (n={len(d)}, {len(feats)} features)")
    md("| model | CV-F1 (train, 5-fold) | rep-CV F1 | rep-CV ROC-AUC | rep-CV bal.acc | test acc | test F1 | test recall | test AUC [95% CI] |")
    md("|---|---|---|---|---|---|---|---|---|")
    for n_, r in out.items():
        ci = f" [{r['test_auc_ci'][0]}, {r['test_auc_ci'][1]}]" if "test_auc_ci" in r else ""
        md(f"| {n_} | {r['cv5_train_f1_mean']} ± {r['cv5_train_f1_sd']} | {r['rcv_f1_mean']} ± {r['rcv_f1_sd']} | "
           f"{r['rcv_auc_mean']} ± {r['rcv_auc_sd']} | {r['rcv_balacc_mean']} ± {r['rcv_balacc_sd']} | {r['test_acc']} | "
           f"{r['test_f1']} | {r['test_recall']} | {r['test_auc']}{ci} |")
    return out, prep

R["cf_models"] = {}
R["cf_models"]["B_matched_12f"], _ = evaluate(M, FEAT_FULL, label="Spec B: matched + DQ, 12 original features")
R["cf_models"]["C_matched_r1_9f"], _ = evaluate(M, FEAT_R1C, label="Spec C: matched + DQ, r1 audit (9 features)")
R["cf_models"]["D_matched_consistent_8f"], prepD = evaluate(M, FEAT_D, label="Spec D: matched + DQ, consistent window audit (8 features) [PRIMARY]")
# sensitivity: Spec D without data-quality exclusion (cohort used in the published version)
R["cf_models"]["D_on_uncleaned_matched"], _ = evaluate(M_unclean, FEAT_D, label="Sensitivity: Spec D on matched cohort WITHOUT data-quality exclusion", test_bootstrap=False)

# permutation test (label shuffling) for the primary model family
md("\n### Permutation tests (repeated-label shuffling, ROC-AUC, 5-fold CV on full primary cohort)")
perm = {}
X, y = M[FEAT_D], M["label"].values
for name in ["Random Forest", "Logistic Regression"]:
    clf = model_zoo(pd.Series(y))[name]
    sc, ps, pv = permutation_test_score(Pipeline([("prep", prepD), ("clf", clf)]), X, y,
                                        cv=StratifiedKFold(5, shuffle=True, random_state=SEED), scoring="roc_auc",
                                        n_permutations=N_PERM, random_state=SEED, n_jobs=2)
    perm[name] = {"auc": r3(sc), "null_mean": r3(ps.mean()), "null_95pct": r3(np.percentile(ps, 95)), "p": float(pv), "n_perm": N_PERM}
    md(f"- {name}: AUC={sc:.3f}; null mean={ps.mean():.3f}, null 95th pct={np.percentile(ps,95):.3f}; p={pv:.4f} ({N_PERM} permutations)")
R["cf_permutation"] = perm

# ---------------------------------------------------------------- CF-6 importance
md("\n## CF-6 Feature importance (Spec D, Random Forest)\n")
Xtr, Xte, ytr, yte = train_test_split(M[FEAT_D], M["label"].values, test_size=0.2, stratify=M["label"].values, random_state=SEED)
rf = Pipeline([("prep", prepD), ("clf", model_zoo(pd.Series(ytr))["Random Forest"])]).fit(Xtr, ytr)
imp = pd.DataFrame({"feature": FEAT_D, "impurity": rf.named_steps["clf"].feature_importances_})
pi = permutation_importance(rf, Xte, yte, scoring="roc_auc", n_repeats=30, random_state=SEED, n_jobs=2)
imp["perm_auc_drop"] = pi.importances_mean; imp["perm_sd"] = pi.importances_std
imp = imp.sort_values("impurity", ascending=False)
for _, r in imp.iterrows(): md(f"- {r.feature}: impurity={r.impurity:.3f}; permutation ΔAUC={r.perm_auc_drop:.3f} ± {r.perm_sd:.3f}")
R["cf_importance_D"] = imp.round(8).to_dict(orient="records")

# =============================================================================
# SURVEY LAYER
# =============================================================================
md("\n## SV-1 Survey sample flow\n")
sv = pd.read_csv("data/survey_responses.csv")
S_ = "6. Your current CP status? "
counts = sv[S_].value_counts().to_dict()
m = sv[sv[S_] != "Never started CP"].copy()
INT = "Interest in other tracks (Web Dev/ML)"
m["active"] = m[S_].str.contains("Currently active", na=False)
m64 = m[~((~m.active) & (m["31. Main reasons for quitting "] == INT))].copy()
m64["label"] = (~m64.active).astype(int)
R["survey_flow"] = {"responses": len(sv), "status_counts": counts, "excluded_never_started": int(counts.get("Never started CP", 0)),
                    "cp_experienced": len(m), "excluded_intentional_exit": int(((~m.active) & (m["31. Main reasons for quitting "] == INT)).sum()),
                    "analysis_set": len(m64), "active": int((m64.label == 0).sum()), "true_attrition": int((m64.label == 1).sum())}
md(str(R["survey_flow"]))

reasons = m.loc[~m.active, "31. Main reasons for quitting "].value_counts()
R["survey_reasons"] = [{"reason": k, "n": int(v), "pct": r3(v / 51 * 100), "ci": [r3(x * 100) for x in wilson(v, 51)]} for k, v in reasons.items()]
md("Reasons (n=51, single choice): " + "; ".join(f"{x['reason']}: {x['n']} ({x['pct']}%, 95% CI {x['ci']})" for x in R["survey_reasons"]))

md("\n## SV-2 Item comparability\n")
ITEMS = {
 "prior_exp":        ("Q3", "Q3", "common item, same wording for all respondents", "comparable"),
 "dsa_grade":        ("Q4", "Q4", "common item, same wording for all respondents", "comparable"),
 "math_skill":       ("Q5", "Q5", "common item, same wording for all respondents", "comparable"),
 "ds_understanding": ("Q14", "Q37", "parallel wording; stopped branch refers to 'when you quit'", "comparable with recall caveat"),
 "mentor_support":   ("Q22", "Q35", "parallel wording; present vs past tense", "comparable with recall caveat"),
 "thought_quit":     ("Q28", "Q34", "identical wording", "comparable with recall caveat"),
 "upsolving_habit":  ("Q11", "Q33", "different constructs: Q11 = post-contest upsolving frequency; Q33 = general practice habit in the month before quitting; original recoding Regular->Sometimes, Became irregular->Rarely, Stopped completely->Never", "NOT comparable - excluded from between-group inference"),
 "long_break":       ("Q27", "Q36", "different reference periods: Q27 = last 3 months; Q36 = whole CP journey", "NOT comparable - excluded from between-group inference"),
 "friend_circle_cp": ("-", "Q39", "asked of the stopped branch only; no active-branch item", "NOT comparable - excluded"),
}
R["survey_item_map"] = {k: {"active_item": v[0], "stopped_item": v[1], "note": v[2], "decision": v[3]} for k, v in ITEMS.items()}
for k, v in R["survey_item_map"].items(): md(f"- {k}: {v}")

def coal(r, a, s):
    v = r.get(a, np.nan); return v if pd.notna(v) else r.get(s, np.nan)
m64["prior_exp"] = m64["3. Did you know programming before university? "]
m64["dsa_grade"] = m64["4. Grade in Data Structures and Algorithms (DSA) course "]
m64["math_skill"] = m64["5. Mathematics skills rating "]
m64["ds_understanding"] = m64.apply(lambda r: coal(r, "14. Understanding of standard data structures ", "37. Understanding of standard data structures when you quit "), axis=1)
m64["mentor_support"] = m64.apply(lambda r: coal(r, "22. Have a mentor/senior guide? ", "35. Had mentor/senior support? "), axis=1)
m64["thought_quit"] = m64.apply(lambda r: coal(r, "28. Ever seriously thought about quitting CP? ", "34.  Ever seriously thought about quitting CP?"), axis=1)
NUM = ["math_skill", "ds_understanding"]; CAT = ["dsa_grade", "prior_exp", "mentor_support", "thought_quit"]

md("\n## SV-3 Group tests on comparable items (n=64)\n")
rng = np.random.default_rng(SEED)
def perm_chi2(sub, f, n=10000):
    ct = pd.crosstab(sub[f], sub["label"]); obs = stats.chi2_contingency(ct, correction=False)[0]
    lab = sub["label"].values; cnt = 0
    for _ in range(n):
        c = pd.crosstab(sub[f].values, rng.permutation(lab))
        if c.shape[1] < 2: continue
        cnt += stats.chi2_contingency(c, correction=False)[0] >= obs - 1e-12
    return (cnt + 1) / (n + 1)
rows = []
for f in NUM:
    a = pd.to_numeric(m64.loc[m64.label == 0, f]).values; s = pd.to_numeric(m64.loc[m64.label == 1, f]).values
    w = stats.ttest_ind(s, a, equal_var=False); mw = stats.mannwhitneyu(s, a, alternative="two-sided")
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(s) - 1) * s.var(ddof=1)) / (len(a) + len(s) - 2)); dd = (s.mean() - a.mean()) / sp
    lo, hi = boot_ci(lambda x, y: (y.mean() - x.mean()) / np.sqrt(((len(x)-1)*x.var(ddof=1)+(len(y)-1)*y.var(ddof=1))/(len(x)+len(y)-2)), a, s)
    rows.append(dict(feature=f, test="Welch t (Mann-Whitney U in note)", stat=w.statistic, df=w.df, p=w.pvalue, p_mw=mw.pvalue,
                     effect=f"Hedges-uncorrected d={dd:.2f}", eff=dd, ci_lo=lo, ci_hi=hi,
                     note=f"stopped mean {s.mean():.2f} (n={len(s)}) vs active {a.mean():.2f} (n={len(a)}); medians {np.median(s):.0f} vs {np.median(a):.0f}"))
for f in CAT:
    sub = m64[[f, "label"]].dropna(); ct = pd.crosstab(sub[f], sub["label"])
    chi_u = stats.chi2_contingency(ct, correction=False); n = ct.values.sum(); V = np.sqrt(chi_u[0] / (n * (min(ct.shape) - 1)))
    chi_y = stats.chi2_contingency(ct, correction=True)[0] if ct.shape == (2, 2) else np.nan
    p_exact = stats.fisher_exact(ct.values)[1] if ct.shape == (2, 2) else perm_chi2(sub, f, n=2000 if FAST else 10000)
    bs = []
    for _ in range(N_BOOT):
        b = sub.sample(len(sub), replace=True, random_state=int(rng.integers(1e9))).reset_index(drop=True)
        c = pd.crosstab(b[f], b["label"])
        if min(c.shape) < 2: continue
        bs.append(np.sqrt(stats.chi2_contingency(c, correction=False)[0] / (c.values.sum() * (min(c.shape) - 1))))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    exp_min = chi_u[3].min()
    rows.append(dict(feature=f, test="Pearson chi-square (no continuity correction); exact p" + (" Fisher" if ct.shape == (2, 2) else " Monte-Carlo permutation"),
                     stat=chi_u[0], df=chi_u[2], p=p_exact, p_asymptotic=chi_u[1], chi2_yates=chi_y, effect=f"Cramer V={V:.2f}", eff=V, ci_lo=lo, ci_hi=hi,
                     note=f"table {ct.shape[0]}x{ct.shape[1]}, n={n}, min expected count={exp_min:.2f}"))
T = pd.DataFrame(rows); T["p_holm"] = holm(T.p); T["p_bh"] = bh(T.p)
for _, r in T.iterrows():
    md(f"- {r.feature}: {r.test}; stat={r.stat:.2f}, df={r.df:.1f}, p={fmt_p(r.p)}, Holm={fmt_p(r.p_holm)}, BH={fmt_p(r.p_bh)}; {r.effect} "
       f"[{r.ci_lo:.2f}, {r.ci_hi:.2f}]; {r.note}")
R["survey_tests_comparable"] = T.round(8).to_dict(orient="records")
# descriptive only, within-branch, for the non-comparable items
R["survey_branch_descriptives"] = {
    "Q11_upsolving_active_n22": sv.loc[sv[S_].str.contains("Currently", na=False), "11. Do you do upsolving after contests? "].value_counts().to_dict(),
    "Q33_practice_month_before_quitting_stopped_n51": sv["33.  Practice habit in the month before quitting "].value_counts().to_dict(),
    "Q27_break_last3months_active_n22": sv["27. Taken 15+ consecutive days break in last 3 months? "].value_counts().to_dict(),
    "Q36_break_ever_stopped_n51": sv['36. Have you taken 15+ consecutive days of break during your CP journey?"'].value_counts().to_dict(),
    "Q39_friend_circle_stopped": sv["39. How many people in your friend circle did CP? "].value_counts().to_dict()}
md(f"Within-branch descriptives: {R['survey_branch_descriptives']}")

md("\n## SV-4 Survey classifier on comparable items only (n=64)\n")
R["survey_models_comparable"], _ = evaluate(m64, NUM + CAT, cat=CAT, label="Survey: 6 comparable items", test_bootstrap=False)
prep_s = ColumnTransformer([("num", Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]), NUM),
                            ("cat", Pipeline([("i", SimpleImputer(strategy="most_frequent")), ("o", OneHotEncoder(handle_unknown="ignore"))]), CAT)])
sc, ps, pv = permutation_test_score(Pipeline([("p", prep_s), ("m", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=SEED))]),
                                    m64[NUM + CAT], m64.label.values, cv=StratifiedKFold(5, shuffle=True, random_state=SEED),
                                    scoring="roc_auc", n_permutations=N_PERM, random_state=SEED, n_jobs=2)
R["survey_permutation_LR"] = {"auc": r3(sc), "null_mean": r3(ps.mean()), "p": float(pv), "n_perm": N_PERM}
md(f"Permutation test, LR on comparable items: AUC={sc:.3f}, null mean={ps.mean():.3f}, p={pv:.4f}")
oh = prep_s.fit(m64[NUM + CAT]).transform(m64[NUM + CAT]).shape[1]
R["survey_input_width_after_onehot"] = int(oh)
md(f"Input width after one-hot encoding of the 6 comparable items: {oh}")

md("\n## SV-5 Reproducing the original statistics\n")
mo = m.copy(); mo["label"] = (~mo.active).astype(int)
mo["long_break_orig"] = mo['36. Have you taken 15+ consecutive days of break during your CP journey?"']   # stopped-branch only
mo["friend_orig"] = mo["39. How many people in your friend circle did CP? "]
rep = {}
for f, col in [("long_break_orig", "long_break_orig"), ("friend_circle_orig", "friend_orig")]:
    x = mo[col].fillna("MISSING"); ct = pd.crosstab(x, mo.label)
    rep[f] = {"chi2_missing_as_category_n73": r3(stats.chi2_contingency(ct)[0]), "crosstab": ct.to_dict()}
ua = mo["11. Do you do upsolving after contests? "]; ps_ = mo["33.  Practice habit in the month before quitting "]
mo["ups"] = [a if pd.notna(a) else {"Regular": "Sometimes", "Became irregular": "Rarely", "Stopped completely": "Never"}.get(p, np.nan) for a, p in zip(ua, ps_)]
rep["upsolving_n73"] = r3(stats.chi2_contingency(pd.crosstab(mo.ups, mo.label))[0])
ups64 = [a if pd.notna(a) else {"Regular": "Sometimes", "Became irregular": "Rarely", "Stopped completely": "Never"}.get(p, np.nan)
         for a, p in zip(m64["11. Do you do upsolving after contests? "], m64["33.  Practice habit in the month before quitting "])]
ct64 = pd.crosstab(pd.Series(ups64, index=m64.index), m64.label)
rep["upsolving_n64_r2"] = {"chi2": r3(stats.chi2_contingency(ct64)[0]), "crosstab": ct64.to_dict()}
lb64 = m64.apply(lambda r: coal(r, "27. Taken 15+ consecutive days break in last 3 months? ", '36. Have you taken 15+ consecutive days of break during your CP journey?"'), axis=1)
ctlb = pd.crosstab(lb64, m64.label)
rep["long_break_paired_n64_r2"] = {"chi2_yates": r3(stats.chi2_contingency(ctlb, correction=True)[0]),
                                   "chi2_pearson": r3(stats.chi2_contingency(ctlb, correction=False)[0])}
for f in ["mentor_support", "thought_quit", "prior_exp"]:
    ct = pd.crosstab(m64[f], m64.label)
    rep[f + "_n64"] = {"chi2_yates": r3(stats.chi2_contingency(ct, correction=True)[0]), "chi2_pearson": r3(stats.chi2_contingency(ct, correction=False)[0])}
R["survey_original_stats_reproduced"] = rep
for k, v in rep.items(): md(f"- {k}: {v}")

# =============================================================================
# EXPORTS requested by the editorial desk (figures are drawn by r3_figures.py)
# =============================================================================
keep = ["handle", "label", "status_proxy", "max_rating", "current_rating", "total_contests", "total_submissions",
        "total_problems_solved", "months_since_last_submission", "burnout_flag"] + sorted(set(FEAT_FULL + FEAT_D))
M[keep].to_csv("data/cf_matched_modelling_set.csv", index=False)
m64[["label", "math_skill", "ds_understanding", "dsa_grade", "prior_exp", "mentor_support", "thought_quit"]].to_csv(
    "data/survey_analysis_set_n64.csv", index=False)
md("\nWrote data/cf_matched_modelling_set.csv and data/survey_analysis_set_n64.csv")

json.dump(R, open("results/r3_results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
open("results/r3_report.md", "w").write("\n".join(MD))
print("\nWrote results/r3_results.json and results/r3_report.md")
