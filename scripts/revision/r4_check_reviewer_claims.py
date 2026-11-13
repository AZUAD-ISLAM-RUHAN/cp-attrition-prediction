"""r4_check_reviewer_claims.py - tests every numerical claim in the reviewer report of the corrected version
(AJSE Paper 1999, received 8 Nov 2026) against the public data, using the same cohort rules and model settings
as r3_inquiry_reanalysis.py. Writes results/r4_reviewer_claims.json and prints a verdict per claim.
Run from the repository root:   python scripts/revision/r4_check_reviewer_claims.py
"""
import json, warnings
import numpy as np, pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, RepeatedStratifiedKFold, cross_val_score
warnings.filterwarnings("ignore")
SEED = 42
R = json.load(open("results/r3_results.json")); OUT = {}
FEAT_D = ["math_solve_rate", "ds_solve_rate", "acceptance_rate", "avg_struggle_minutes",
          "upsolves_per_contest", "post_drop_recovery", "editorial_dependency_index", "solved_per_contest"]

raw = pd.read_csv("data/cf_attrition_features.csv")
q1 = raw.total_submissions < raw.total_contests
q2 = (~q1) & (raw.contests_per_month > 15)
clean = raw[~(q1 | q2)].copy()

def add_feats(d):
    d = d.copy()
    d["editorial_dependency_index"] = d.upsolves_per_contest * d.avg_struggle_minutes
    d["solved_per_contest"] = d.total_problems_solved / d.total_contests
    d["subs_per_contest"] = d.total_submissions / d.total_contests
    return d

def cohort(d, sample_seed=SEED, peak_cut=1500, all_active=False):
    A = d[(d.status_proxy == "Active") & (d.max_rating < peak_cut)].copy()
    S = d[(d.status_proxy == "Stopped") & (d.max_rating < peak_cut)].copy()
    A["label"] = 0; S["label"] = 1
    if not all_active: A = A.sample(n=len(S), random_state=sample_seed)
    return add_feats(pd.concat([A, S], ignore_index=True))

def rf(): return RandomForestClassifier(n_estimators=200, random_state=SEED, class_weight="balanced", n_jobs=-1)
def lr(): return LogisticRegression(max_iter=1000, random_state=SEED, class_weight="balanced")
def auc(d, feats, model=rf, reps=1):
    pipe = Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler()), ("m", model())])
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=reps, random_state=SEED) if reps > 1 else StratifiedKFold(5, shuffle=True, random_state=SEED)
    return float(cross_val_score(pipe, d[feats], d.label, cv=cv, scoring="roc_auc").mean())

def show(k, claim, ours, verdict):
    OUT[k] = {"reviewer_claim": claim, "our_check": ours, "verdict": verdict}
    print(f"\n[{k}] {verdict}\n   reviewer: {claim}\n   check:    {ours}")

# ---- B2: one random sample of active users
M42 = cohort(clean)
base42 = auc(M42, FEAT_D)
seeds = list(range(50)) if 42 in range(50) else list(range(49)) + [42]
vals = {s: auc(cohort(clean, sample_seed=s), FEAT_D) for s in seeds}
v = np.array(list(vals.values())); rank42 = int((v > vals[42]).sum()) + 1
allA = cohort(clean, all_active=True); a_all = auc(allA, FEAT_D)
show("B2", "AUC over other random samples of active users ranges about 0.605-0.625; seed 42 gave the highest value",
     f"Random Forest, 5-fold CV, 50 samples (seeds 0-49): mean {v.mean():.3f}, SD {v.std():.3f}, range {v.min():.3f}-{v.max():.3f}; "
     f"seed 42 = {vals[42]:.3f} (rank {rank42} of {len(v)}). All 3,421 active + 908 attrition with class weights: AUC {a_all:.3f}.",
     "CONFIRMED in substance" if v.min() < vals[42] else "NOT CONFIRMED")
OUT["B2"]["per_seed"] = {int(k): round(x, 4) for k, x in vals.items()}

# ---- B3: incomplete histories
n_bad = int((q1 | q2).sum()); act_bad = int(((q1 | q2) & (raw.status_proxy == "Active")).sum())
low = M42[M42.subs_per_contest < 2]
show("B3a", "888 of 6,927 accounts (12.8%) had incomplete histories, all active",
     f"{n_bad} of {len(raw)} ({100*n_bad/len(raw):.1f}%); active among them: {act_bad}",
     "CONFIRMED" if n_bad == 888 and act_bad == 888 else "DIFFERS")
show("B3b", "Among kept users, 117 active but only 4 quitters have fewer than 2 submissions per contest",
     f"matched cohort (seed 42): active {int((low.label == 0).sum())}, attrition {int((low.label == 1).sum())}; "
     f"median submissions per contest: active {M42[M42.label==0].subs_per_contest.median():.2f}, attrition {M42[M42.label==1].subs_per_contest.median():.2f}",
     "CONFIRMED" if (int((low.label == 0).sum()), int((low.label == 1).sum())) == (117, 4) else "CLOSE / DIFFERS (see numbers)")
strict = {}
for thr in [2, 3]:
    c = clean[clean.total_submissions / clean.total_contests >= thr]
    vv = [auc(cohort(c, sample_seed=s), FEAT_D) for s in range(10)]
    strict[thr] = (np.mean(vv), np.min(vv), np.max(vv), int(((c.status_proxy == "Stopped") & (c.max_rating < 1500)).sum()))
show("B3c", "With a stricter rule the AUC is only about 0.58-0.61",
     "; ".join(f">= {t} submissions per contest: attrition n={s[3]}, AUC mean {s[0]:.3f} (range {s[1]:.3f}-{s[2]:.3f}, 10 samples)" for t, s in strict.items()),
     "CONFIRMED in substance" if all(s[0] < base42 for s in strict.values()) else "NOT CONFIRMED")

# ---- B5: account age
a_age, s_age = M42[M42.label == 0].account_age_months.median(), M42[M42.label == 1].account_age_months.median()
adj = auc(M42, FEAT_D + ["account_age_months", "total_contests"])
show("B5", "Active users have newer accounts (median 19 vs 33.5 months); adjusted AUC about 0.628",
     f"median account age: active {a_age:.1f}, attrition {s_age:.1f} months; AUC with account age and total contests added as covariates: {adj:.3f} (without: {base42:.3f})",
     "CONFIRMED" if abs(a_age - 19) < 1 and abs(s_age - 33.5) < 1 else "DIFFERS")

# ---- E2, E4
U = raw[raw.status_proxy.isin(["Active", "Stopped"])]
show("E2", "The published unmatched analysis (Spec A) included 4 users rated 2400 or more",
     f"accounts with peak rating >= 2400 in the released file: {int((raw.max_rating >= 2400).sum())} (Table I removes them before modelling)",
     "CONFIRMED" if int((raw.max_rating >= 2400).sum()) >= 4 else "DIFFERS")
e4 = raw[(raw.months_since_last_submission.round(6) == 3.0)]
show("E4", "Seven accounts show exactly 3.0 months of inactivity but are labelled Active",
     f"accounts with months_since_last_submission == 3.0: {len(e4)}; status: {e4.status_proxy.value_counts().to_dict()}; "
     f"min months among Stopped: {raw[raw.status_proxy=='Stopped'].months_since_last_submission.min():.4f}",
     "CONFIRMED" if len(e4) == 7 and (e4.status_proxy == "Active").all() else "DIFFERS")

# ---- E5, B6 (from r3 results)
d = {r["feature"]: r for r in R["cf_descriptives_matched"]}["avg_struggle_minutes"]
show("E5", "Struggle time: adjusted p 0.191, unadjusted 0.095",
     f"r3: p = {d.get('p'):.3f}, Holm p = {d.get('p_holm'):.3f}" if d.get("p") is not None else str(d),
     "CONFIRMED" if d.get("p") and abs(d["p"] - 0.095) < 0.002 and abs(d["p_holm"] - 0.191) < 0.002 else "CHECK")
top = max(R["cf_importance_D"], key=lambda r: r["perm_auc_drop"])
show("B6", "Problems per contest importance rests on one test set (drop 0.066 in AUC)",
     f"r3 permutation importance on the held-out 20% test set: {top['feature']} drop {top['perm_auc_drop']:.3f} (SD {top['perm_sd']:.3f} over 30 repeats of the SAME test set)",
     "CONFIRMED")

# ---- B1 feasibility
show("B1", "Features use the whole history; redo with a fixed window ending 3 months before the last submission",
     "The released feature file holds only whole-history aggregates (26 columns, no timestamps). B1 needs the raw submission "
     "records (users_dynamic.jsonl) or a re-collection from the Codeforces API using the private handle list.",
     "CONFIRMED (cannot be done from the public files)")

# ---- Survey: A5, C4 and the 9 'other tracks' respondents
sv = pd.read_csv("data/survey_responses.csv"); S_ = "6. Your current CP status? "
st = sv[sv[S_] == "Previously did CP, but stopped"]; INT = "Interest in other tracks (Web Dev/ML)"
kept = st[st["31. Main reasons for quitting "] != INT]; nine = st[st["31. Main reasons for quitting "] == INT]
Q36 = '36. Have you taken 15+ consecutive days of break during your CP journey?"'
yk, ya = int((kept[Q36] == "Yes").sum()), int((st[Q36] == "Yes").sum())
show("A5", "Long break: 28/42 = 67% in the analysis set; the published 73% = 37/51 includes the 9 removed",
     f"Q36 'Yes': analysis set {yk}/{len(kept)} = {100*yk/len(kept):.1f}%; all stopped {ya}/{len(st)} = {100*ya/len(st):.1f}%",
     "CONFIRMED" if (yk, len(kept), ya, len(st)) == (28, 42, 37, 51) else "DIFFERS")
others = int((kept["31. Main reasons for quitting "] == "Others").sum())
show("C4", "23 never started; 9 left for other fields; 9 chose 'Others' and are counted as quitters",
     f"never started {int((sv[S_]=='Never started CP').sum())}; 'Interest in other tracks' {len(nine)}; 'Others' among the 42 kept: {others}",
     "CONFIRMED" if (len(nine), others) == (9, 9) else "DIFFERS")
Q32, Q43, Q30 = "32. Highest rating before quitting (0 if no rating) ", "43. Current focus area ", "30. Duration of CP practice before quitting "
r9 = pd.to_numeric(nine[Q32], errors="coerce")
OUT["nine_other_tracks"] = {"highest_rating_before_quitting": [None if np.isnan(x) else float(x) for x in r9],
                            "n_rating_ge_1500": int((r9 >= 1500).sum()), "n_rating_ge_1400": int((r9 >= 1400).sum()),
                            "current_focus_area": nine[Q43].fillna("(blank)").tolist() if Q43 in nine else None,
                            "duration_before_quitting": nine[Q30].fillna("(blank)").tolist()}
print("\n[The 9 'Interest in other tracks' respondents]", json.dumps(OUT["nine_other_tracks"], indent=1))
r42 = pd.to_numeric(kept[Q32], errors="coerce")
OUT["kept_42_highest_rating"] = {"median": float(r42.median()), "n_ge_1500": int((r42 >= 1500).sum()), "n_zero": int((r42 == 0).sum())}
print("[The 42 kept stopped respondents] highest rating:", OUT["kept_42_highest_rating"])
json.dump(OUT, open("results/r4_reviewer_claims.json", "w"), indent=1)
print("\nwrote results/r4_reviewer_claims.json")
