"""Corrected manuscript built paragraph-by-paragraph from the PUBLISHED camera-ready text.
Each block may carry  o=<index of the published paragraph it replaces>  so a tracked-changes
version can be generated against the published wording.  DEL(i) marks a published paragraph
that is removed.  Every number comes from results/*.json or the exported analysis sets.
Inline markup: *italic*, **bold**, _{sub}, ^{sup}, ⟦author placeholder⟧."""
import json
import pandas as pd
from pathlib import Path
REPO = str(Path(__file__).resolve().parents[1]); MB = str(Path(__file__).resolve().parent)
Path(MB, "output").mkdir(exist_ok=True)              # git-ignored, so absent in a fresh clone
PUB = json.load(open(f"{MB}/inputs/pub_paras.json"))
R = json.load(open(f"{REPO}/results/r3_results.json"))
T1 = json.load(open(f"{REPO}/results/r3_table1_cohort.json"))
SV = pd.read_csv(f"{REPO}/data/survey_analysis_set_n64.csv")
INSTR = json.load(open(f"{MB}/inputs/instrument.json"))

def fpv(p): return "<0.001" if p < 0.001 else f"{p:.3f}"
def g(x): return f"{x:,.0f}" if abs(x) >= 100 else (f"{x:.1f}" if abs(x) >= 10 else f"{x:.2f}")
T1d = {r["stage"]: r["accounts"] for r in T1}
coh = R["cf_cohorts"]["primary_matched_clean"]; bal_u, bal_m = R["cf_balance"]["original_unmatched"], R["cf_balance"]["primary_matched_clean"]
D = {r["feature"]: r for r in R["cf_descriptives_matched"]}; DU = {r["feature"]: r for r in R["cf_descriptives_original_unmatched"]}
H = R["original_headline_reproduced"]; B = R["cf_burnout"]["primary_matched_clean"]; UPS = R["cf_upsolving_bins"]["primary_matched_clean"]
MD = R["cf_models"]; Dm, Bm, Cm, Sm = MD["D_matched_consistent_8f"], MD["B_matched_12f"], MD["C_matched_r1_9f"], MD["D_on_uncleaned_matched"]
BASE, RAND = "Baseline: always 'attrition'", "Baseline: random (stratified)"
MODELS = [n for n in Dm if not n.startswith("Baseline")]
best = lambda M_: max(MODELS, key=lambda n: M_[n]["rcv_auc_mean"]); bD, bB, bC, bS = best(Dm), best(Bm), best(Cm), best(Sm)
n_below = lambda M_: sum(M_[n]["rcv_f1_mean"] < M_[BASE]["rcv_f1_mean"] for n in MODELS)
PERM = R["cf_permutation"]; IMP = sorted(R["cf_importance_D"], key=lambda r: -r["perm_auc_drop"])
SF = R["survey_flow"]; REAS = R["survey_reasons"]; ST = {r["feature"]: r for r in R["survey_tests_comparable"]}
SVM_ = R["survey_models_comparable"]; SVP = R["survey_permutation_LR"]; SVB = R["survey_branch_descriptives"]
svmods = [n for n in SVM_ if not n.startswith("Baseline")]; sv_best = max(svmods, key=lambda n: SVM_[n]["rcv_auc_mean"])
reas = {r["reason"]: r for r in REAS}; RN = reas["Rating not increasing/no progress"]
rep = R["environment"]["cv_repeats"]; nperm = PERM["Random Forest"]["n_perm"]
ms_a, ms_s = SV.loc[SV.label == 0, "math_skill"].mean(), SV.loc[SV.label == 1, "math_skill"].mean()
ds_a, ds_s = SV.loc[SV.label == 0, "ds_understanding"].mean(), SV.loc[SV.label == 1, "ds_understanding"].mean()
math, dsu = ST["math_skill"], ST["ds_understanding"]
sig = [f for f, r in D.items() if r["p_holm"] < 0.05 and f != "account_age_months"]
maxr = max(abs(D[f]["r_rb"]) for f in sig)
dq_removed = T1d["After peak rating < 2400"] - T1d["After data-quality check (complete submission history)"]
FIG = f"{REPO}/figures/revised"

blocks = []
def H1(t, o=None): blocks.append({"t": "h1", "text": t, "o": o})
def H2(t, o=None): blocks.append({"t": "h2", "text": t, "o": o})
def P(t, o=None, noindent=False): blocks.append({"t": "p", "text": t, "o": o, "noindent": noindent})
def URL(u): blocks.append({"t": "url", "text": u, "o": None})   # own centred line, clickable, 8 pt so it never wraps
def EQ(t, n, o=None): blocks.append({"t": "eq", "text": t, "num": n, "o": o})
def F(name, cap, o_cap=None, wide=False): blocks.append({"t": "fig", "path": f"{FIG}/{name}.png", "cap": cap, "o": o_cap, "wide": wide})
def TAB(cap, head, rows, w, note=None, size=13, wide=True, o_cap=None): blocks.append({"t": "tab", "cap": cap, "head": head, "rows": rows, "w": w, "note": note, "size": size, "wide": wide, "o": o_cap})
def DEL(*idx):
    for i in idx: blocks.append({"t": "del", "o": i})

meta = {"title": PUB[0], "authors": PUB[1], "affil": PUB[3].split("\n"), "index": PUB[5].replace("Index Terms—", "")}
meta["notice"] = ("Corrected version prepared in response to the AJSE Editorial Desk inquiry of 3 November 2026 (Paper ID 1999). "
                  "All numerical results were regenerated from the deposited data and code; each change is listed in the accompanying response.")
meta["abstract"] = (   # AJSE template: one paragraph, 150-250 words, self-contained, no abbreviations or references
 "Competitive programming develops algorithmic reasoning in computer science students, yet many withdraw after stalled progress or thin mentorship, "
 "and this attrition has not been studied as a behavioral phenomenon. "
 "We report two independent analyses: platform activity logs and a local student survey. "
 f"From {T1d['Released feature file (>=5 rated contests, current rating 1-2399)']:,} Codeforces accounts, we removed {dq_removed} with incomplete submission histories and formed a balanced cohort of {coh['n']:,} users, "
 "half persistently active and half withdrawn, matched on peak rating so that disengagement is not confounded with skill. "
 "Every feature whose value depends on the length or end of the observation window was removed to prevent temporal leakage. "
 f"Compared with active users of the same rating range, users who withdrew entered fewer rated contests (median {g(D['contests_per_month']['attr_median'])} versus {g(D['contests_per_month']['active_median'])} per month), "
 f"solved fewer problems per month ({g(D['problems_solved_per_month']['attr_median'])} versus {g(D['problems_solved_per_month']['active_median'])}), and were slightly less accurate on mathematics and data-structure problems; "
 f"all of these effects were small (rank-biserial |r| ≤ {maxr:.2f}). "
 f"The best classifier reached a cross-validated area under the receiver operating characteristic curve of {Dm[bD]['rcv_auc_mean']:.3f} (random forest {Dm['Random Forest']['rcv_auc_mean']:.3f}, permutation p = {PERM['Random Forest']['p']:.3f}). "
 "This signal is above chance but modest: no model exceeded the F1 score of a trivial baseline that predicts attrition for every user. "
 f"In the survey ({SF['responses']} responses, {SF['analysis_set']} analyzed), stalled progress was the most frequent reason for stopping ({RN['n']} of 51). "
 f"Students who stopped rated their mathematics ability higher than active peers ({ms_s:.2f} versus {ms_a:.2f}), but the difference does not survive correction for multiple testing, "
 "so the Skill-Application Paradox is stated as a hypothesis, not a finding.")

# ---------------------------------------------------------------- I Introduction
H1("I. Introduction", o=6)
P(PUB[7], o=7)
P(PUB[8].replace("stop within months [5].", "stop within months, a pattern also documented for dropout from introductory programming courses [5]."), o=8)
P(PUB[9], o=9)
P("We therefore built a two-layer study and framed it around three questions. RQ1 asks which reasons students themselves select, from a closed list, for discontinuing competitive programming. "
  "RQ2 asks whether behavioral proxies drawn from Codeforces activity separate active users from true attrition users once the two groups are matched on peak rating. "
  "RQ3 asks whether models trained on Codeforces behavior or on psychographic survey responses can identify attrition better than trivial baselines.", o=10)
P("The paper makes four contributions. First, we build a rating-matched Codeforces cohort with a documented stage-by-stage flow and an explicit data-quality rule. "
  "Second, we introduce two domain-specific interaction features, the Intensity Ratio and the Editorial Dependency Index, and report how they behave once temporal leakage is removed. "
  "Third, we benchmark nine classifiers against trivial baselines with per-fold uncertainty and a permutation test. In doing so, we quantify how much apparent signal in this kind of study comes from skill confounding, timing leakage and incomplete platform histories. "
  "Fourth, we report an exploratory survey analysis restricted to items that are comparable across questionnaire branches, together with the full instrument, data and code.", o=11)

# ---------------------------------------------------------------- II Related Work
H1("II. Related Work", o=12)
H2(PUB[13], o=13); P(PUB[14].replace("tabular educational prediction .", "tabular educational prediction."), o=14)
H2(PUB[15], o=15); P(PUB[16], o=16)
H2(PUB[17], o=17); P(PUB[18], o=18)
H2(PUB[19], o=19)
P("We are not aware of any prior study pairing competitive programming platform logs with psychographic survey responses. Telemetry is objective but silent on why a user stopped; surveys reach the reasoning yet depend on recall, and both raise questions of student agency and data ethics [22]. "
  "In this study the two sources share no subjects, features or labels, so we report them side by side rather than combining them.", o=20)

# ---------------------------------------------------------------- III Methodology
H1("III. Methodology", o=21)
F("fig01_study_design", "Fig. 1. Study design. The Codeforces analysis and the survey analysis use different subjects, features and labels, and are reported side by side; no result in one is used to support the other.", o_cap=24, wide=True)
H2(PUB[26], o=26)
P("Submission histories, contest records, and profile metadata were pulled from the public Codeforces API. The sampling frame was the platform's list of rated users (user.ratedList, activeOnly = false), "
  "from which a pool of 26,000 handles was drawn, stratified by current rating band in proportion to band size with at least 50 per band (seed 42). "
  f"The {T1d['Released feature file (>=5 rated contests, current rating 1-2399)']:,} accounts that passed the collection gate described below form the released feature file.", o=27)
P("All features are computed from each account's retrieved history at a single observation time, T_{obs}: the moment the feature file was built, in June 2026, before 24 June 2026. The original notebook did not record the exact time, so the deposited rebuild script now takes T_{obs} as an explicit argument. "
  "Account age and months since the last submission are measured to T_{obs}, and the three-month inactivity criterion in the attrition label is measured backward from T_{obs}. "
  "The per-month rates and the Activity Trend Ratio, by contrast, are computed over each account's own submission span, from its first to its last retrieved submission, not over calendar windows before T_{obs}. "
  "The published version of this paragraph stated otherwise, and the Feature Engineering subsection now gives the definitions as implemented.", o=28)
P(f"Accounts were retrieved only if they had at least five rated contests, a current rating between 1 and 2399, and at least one accepted submission. These criteria were enforced at collection, so all "
  f"{T1d['Released feature file (>=5 rated contests, current rating 1-2399)']:,} accounts satisfy them. Peak rating below 2400 was applied afterwards and removed "
  f"{T1d['Released feature file (>=5 rated contests, current rating 1-2399)'] - T1d['After peak rating < 2400']} accounts. Both modelling classes are restricted to peak ratings below 1500, so this step does not affect the modelling set.", o=29)
P(f"Every rated contest requires at least one submission, so an account with fewer retrieved submissions than rated contests has an incomplete history. "
  f"We excluded such accounts, together with accounts showing more than 15 rated contests per month of submission span (the highest value among inactive accounts was {R['cf_flow']['max_contests_per_month_among_stopped']:.0f}). "
  f"This removed {dq_removed} accounts, all of them active at T_{{obs}}. Left in, they would have inflated the apparent contrast between active and inactive users, because their submission-derived features are computed from truncated histories.")
P("Inactive users fall into two very different groups. An account that had gone three consecutive months without a submission and had never exceeded 1500 was labeled True Attrition. "
  "The cut-off of 1500 is a study choice that lies inside the Codeforces Specialist band (1400–1599); it is not a platform rank boundary. The reasoning is that a user who never progressed beyond that level is unlikely to have left because they achieved what they came for. "
  "Accounts that went quiet at 1500 or above were labeled Intentional Exits and dropped, since career transitions are the more plausible explanation there.", o=30)
P(PUB[31].replace("4,047 active accounts fall below the threshold", f"{T1d['Matching pool: active, peak < 1500']:,} active accounts fall below the threshold after the data-quality check"), o=31)
t1rows = [[r["stage"].replace(">=", "≥").replace("(>=5 rated contests, current rating 1-2399)", "(≥5 rated contests, current rating 1–2399)"), f"{r['accounts']:,}"] for r in T1]
TAB("TABLE I. Cohort construction, stage by stage", ["Stage", "Accounts"], t1rows, [6000, 1500], size=14, wide=False, o_cap=32,
    note=f"Data-quality check: {dq_removed} accounts removed, all active. Produced by scripts/revision/r3_table1_cohort.py.")
DEL(33)
H2("Dataset 2: Student Survey", o=35)
P("The study was reviewed and approved by the Research Ethics Committee of the authors' institution, Metropolitan University, Sylhet (approval no. REC/MU/2026/007). Approval was given by resolution of the Committee's meeting on 24 February 2026, "
  "and the approval letter was issued on 17 March 2026. Responses were collected between 6 March and 2 April 2026. Participation was voluntary and anonymous. "
  "The questionnaire collected no names, student identifiers, email addresses or institutional affiliations, and responses cannot be traced to individuals. The landing page stated the purpose of the study and that responses would be used for academic research. "
  "It also stated that submission constituted consent, and respondents could close the form at any point without submitting. No incentive was offered. "
  "The Codeforces data comes from the platform's public API and covers only information users have chosen to make public. Account handles are pseudonymised with a salted hash in every released file, all published statistics are aggregates, and no attempt was made to link accounts to survey respondents.", o=36)
P(f"We distributed a structured survey online to computer science students at universities in Bangladesh and collected {SF['responses']} responses. The form did not record institution, so we report no breakdown by institution. "
  f"Respondents sorted into three groups: currently active in CP ({SF['status_counts']['Currently active in CP']}), previously active but stopped ({SF['status_counts']['Previously did CP, but stopped']}), and never started ({SF['status_counts']['Never started CP']}). The {SF['status_counts']['Never started CP']} who never started were set aside.", o=37)
P(PUB[38], o=38)
P("The questionnaire branches by status, so active and stopped respondents answered different item sets. A feature drawn from one branch alone is perfectly confounded with the outcome, "
  "and so is a feature that pairs items measuring different things. We therefore use only items that are asked identically of everyone (Q3, Q4, Q5) or worded in parallel across branches: "
  "data structure understanding (Q14 and Q37), mentor support (Q22 and Q35) and prior consideration of quitting (Q28 and Q34). The last three carry a recall caveat for the stopped group. "
  "Two pairings used in the published version are not valid and are no longer used for any between-group test or model. Q11 asks about post-contest upsolving, whereas Q33 asks about general practice habit in the month before quitting. "
  "Q27 asks about breaks in the last three months, whereas Q36 asks about breaks over the whole CP journey. Peer circle density (Q39) was asked only of stopped respondents and is dropped. Items that cannot be compared are reported within their branch only.", o=39)
H2(PUB[40], o=40)
P("For the Codeforces cohort, whose features are heavy-tailed, we report medians and interquartile ranges, compare groups with the two-sided Mann–Whitney U test [33], and give the rank-biserial correlation with a 2,000-sample percentile bootstrap 95 percent confidence interval [28]. "
  "Proportions are reported with Wilson intervals [34]. For the survey we compare the two 1–5 ratings with Welch's t-test [25], chosen over the pooled-variance form because the groups are unequal in size, and report Cohen's d [26] with a confidence interval. "
  "Categorical items use Pearson's chi-square without continuity correction, with exact p-values: Fisher's exact test for 2×2 tables, and a Monte-Carlo permutation test with 10,000 shuffles otherwise, because several expected counts fall below 5. "
  "Cramér's V [27] is given with a bootstrap confidence interval.", o=41)
P("Because we run six survey tests on the same sample, the conventional 0.05 threshold no longer means what it does for a single test. Across six independent tests of features that do not differ, the chance of at least one landing under 0.05 by accident is roughly 26 percent. "
  "We therefore report Holm's sequentially rejective procedure [32], which controls the family-wise error rate like the Bonferroni correction [23] but is uniformly more powerful, and Benjamini-Hochberg [24], which controls the false discovery rate at 5 percent. "
  "The same Holm and Benjamini-Hochberg corrections are applied across the eleven Codeforces comparisons. A feature that passes neither correction is a directional observation, not a finding.", o=42)
lab2 = {"math_skill": "math_skill (Q5)", "ds_understanding": "ds_understanding (Q14/Q37)", "dsa_grade": "dsa_grade (Q4)", "prior_exp": "prior_exp (Q3)",
        "mentor_support": "mentor_support (Q22/Q35)", "thought_quit": "thought_quit (Q28/Q34)"}
t2 = []
for f in ["math_skill", "ds_understanding", "dsa_grade", "mentor_support", "thought_quit", "prior_exp"]:
    r = ST[f]; num = f in ("math_skill", "ds_understanding")
    t2.append([lab2[f], "t" if num else "χ^{2}", f"{r['stat']:.2f}", fpv(r["p"]),
               (f"d = {r['eff']:.2f}" if num else f"V = {r['eff']:.2f}") + f" [{r['ci_lo']:.2f}, {r['ci_hi']:.2f}]", fpv(r["p_holm"]), fpv(r["p_bh"])])
TAB(f"TABLE II. Group differences on comparable items, active (n = {SF['active']}) vs. true attrition (n = {SF['true_attrition']})",
    ["Feature", "Test", "Stat.", "p", "Effect [95% CI]", "Holm p", "BH p"], t2, [2300, 600, 800, 800, 2200, 900, 900], o_cap=44,
    note="t: Welch, positive = stopped higher. χ^{2}: Pearson without continuity correction; p exact (Fisher, 2×2) or Monte-Carlo (10,000 shuffles). Upsolving habit and long break are not compared across branches (see Dataset 2).")
DEL(45)
P(f"No survey difference survives either correction. Mathematical self-rating reaches nominal significance (p = {math['p']:.3f}) with a medium effect (d = {math['eff']:.2f}), "
  f"but its Holm-adjusted p is {math['p_holm']:.3f}. We describe it below as directional rather than established.", o=48)
H2(PUB[49], o=49)
P("Twelve features were derived from the raw API responses. Six are direct behavioral proxies: math solve rate, data structure solve rate, upsolves per contest, mean struggle minutes, activity trend ratio, and post-drop recovery. "
  "All models use the raw values of these features. Earlier versions also showed percentile-binned 1 to 5 scores in descriptive charts, and those charts are not used here. Table VI (Appendix A) gives the definition of every feature as implemented.", o=50)
P(PUB[51], o=51)
EQ("IR_{i} = P_{month,i} / (C_{month,i} + e)", 1, o=52)
P(PUB[53] + f" Because both monthly rates share the same denominator, the length of the user's submission span, that span cancels and IR approximately equals problems solved per rated contest. "
  f"The audited specification therefore uses the exactly window-invariant form SPC_{{i}} = S_{{i}}/C_{{i}}, where S_{{i}} is distinct problems solved and C_{{i}} rated contests (Spearman ρ = {R['ir_vs_solved_per_contest_spearman']:.3f} with IR).", o=53)
P(PUB[54], o=54)
EQ("EDI_{i} = U_{i} × ΔT_{struggle,i}", 2, o=55)
P("where U_{i} is upsolving frequency per contest (accepted practice-mode submissions to contests the user entered) and ΔT_{struggle} is the mean time to acceptance, itself defined as the mean of T_{AC} minus T_{first} over all accepted problems. "
  "A high EDI next to low contest frequency is the pattern the index was designed to detect.", o=56)
P("Decay in activity is captured by the Activity Trend Ratio: the number of submissions in the second half of the user's own submission span divided by the number in the first half, set to 1 when the first half is empty. "
  "An account is flagged for activity decay when this ratio falls below 0.5. Three columns were deliberately kept out: months since last submission encodes the label definition directly, peak rating appears in the label threshold, "
  "and current rating is not measured at a comparable point in time across the two groups.", o=57)
P("From the survey, six features enter the tests and models: mathematics self-rating and data structure understanding, both self-rated 1 to 5; course grade in Data Structures and Algorithms; mentor support; prior consideration of quitting; "
  "and programming experience before university. Upsolving habit and long breaks are described within each branch only. Semester and cumulative grade average were available but excluded, as neither is plausibly connected to CP attrition except through variables already in the model.", o=58)
H2(PUB[59], o=59)
P("Nine architectures were evaluated: logistic regression with L2 regularization, a Gini-split decision tree, Random Forest with 200 estimators (Gini impurity), k-nearest neighbors at k = 5, an RBF-kernel support vector machine, XGBoost [13], LightGBM [14], "
  "a multi-layer perceptron with hidden layers of 64 and 32 units, ReLU activations and a logistic output, and a soft-voting ensemble over the first, third, fifth and sixth of these. "
  "The ensemble averages the four members' attrition probabilities with equal weights; no weights were tuned.", o=60)
EQ("P̂(y = 1 | x) = (1/4) Σ_{m=1..4} P_{m}(y = 1 | x)", 3)
DEL(62, 63, 65, 66)
P("All preprocessing and modeling pipelines were implemented using scikit-learn [21]. Balanced class weights were used wherever the implementation supports them (all models except k-nearest neighbors and the multi-layer perceptron), with XGBoost using a scaled positive weight for the same purpose. "
  "Preprocessing was median imputation followed by standardization on numeric columns and one-hot encoding on categorical ones, fitted inside each training fold. "
  f"We report two protocols. The first is the protocol of the published version: stratified five-fold cross-validation [29] on the 80 percent part of an 80/20 split, with test metrics on the held-out 20 percent. "
  f"The second is stratified five-fold cross-validation repeated {rep} times on the full cohort, reported as mean ± SD over {5 * rep} folds. "
  "ROC-AUC is the primary metric because it does not depend on a decision threshold. F1, balanced accuracy and recall are reported alongside, and every table includes two trivial baselines: always predicting attrition, and predicting at random in class proportion. "
  f"On balanced data, the always-attrition baseline has F1 = 2/3, so F1 must be read against it. Signal is tested with a label-permutation test [35] ({nperm} permutations), and feature importance is measured as the drop in held-out ROC-AUC under permutation (30 repeats). "
  "The random seed is 42 throughout, and the exact library versions are pinned in the deposited requirements file.", o=68)

# ---------------------------------------------------------------- IV Results
H1("IV. Results", o=69)
H2("Behavioral Differences in the Rating-Matched Cohort", o=70)
P(f"Matching worked as intended. Peak ratings in the two classes are balanced (standardized mean difference {bal_m['standardised_mean_difference']:.3f}, Kolmogorov–Smirnov D = {bal_m['ks_D']:.3f}, p = {bal_m['ks_p']:.3f}), "
  f"against {bal_u['standardised_mean_difference']:.2f} and {bal_u['ks_D']:.3f} in the unmatched comparison. Active users entered a median of {g(D['contests_per_month']['active_median'])} rated contests per month of activity and true attrition users {g(D['contests_per_month']['attr_median'])} "
  f"(rank-biserial r = {D['contests_per_month']['r_rb']:.2f}, Holm p {('< 0.001' if D['contests_per_month']['p_holm'] < 0.001 else '= ' + format(D['contests_per_month']['p_holm'], '.3f'))}). "
  f"The published figure of an 83.7 percent fall (7.27 vs. 1.19 contests per month) came from the unmatched cohort. It was driven by {H['active_rows_failing_dq_in_original_sample']} active accounts with truncated submission histories, and is withdrawn. "
  "Table III gives every behavioral comparison on the matched cohort.", o=71)
order = ["contests_per_month", "problems_solved_per_month", "solved_per_contest", "math_solve_rate", "ds_solve_rate", "acceptance_rate", "activity_trend_ratio", "post_drop_recovery", "upsolves_per_contest", "avg_struggle_minutes", "account_age_months"]
lab = {"contests_per_month": "Rated contests / month", "problems_solved_per_month": "Problems solved / month", "solved_per_contest": "Problems solved / contest (SPC)", "avg_struggle_minutes": "Struggle time (min)",
       "math_solve_rate": "Math solve rate", "ds_solve_rate": "DS solve rate", "acceptance_rate": "Acceptance rate", "upsolves_per_contest": "Upsolves / contest",
       "activity_trend_ratio": "Activity trend ratio", "post_drop_recovery": "Post-drop recovery", "account_age_months": "Account age (months)†"}
TAB(f"TABLE III. Behavioral measures on the rating-matched cohort ({coh['active']} active vs. {coh['attrition']} true attrition)",
    ["Measure", "Active median [IQR]", "Attrition median [IQR]", "r_{rb} [95% CI]", "Holm p"],
    [[lab[f], f"{g(D[f]['active_median'])} [{g(D[f]['active_q1'])}, {g(D[f]['active_q3'])}]", f"{g(D[f]['attr_median'])} [{g(D[f]['attr_q1'])}, {g(D[f]['attr_q3'])}]",
      f"{D[f]['r_rb']:.2f} [{D[f]['r_lo']:.2f}, {D[f]['r_hi']:.2f}]", fpv(D[f]["p_holm"])] for f in order], [2400, 1900, 1900, 1700, 900],
    note="Mann–Whitney U; r_{rb} > 0 means attrition values tend to be larger. †Includes the idle period that defines the label; shown for transparency, not modelled.")
F("fig03_cf_matched_distributions", "Fig. 2. Distributions of six behavioral measures in the rating-matched cohort: (a) rated contests per month, (b) problems solved per month, (c) problems solved per contest, (d) struggle time, (e) math-tag acceptance rate and (f) data-structure-tag acceptance rate (boxes: IQR; line: median; whiskers: 1.5 IQR; outliers hidden; log scale for counts and times). Panel titles give the rank-biserial r and the Holm-adjusted p.", o_cap=73)
DEL(72)
P(f"Struggle time does not differ once the cohorts are matched (median {g(D['avg_struggle_minutes']['active_median'])} vs. {g(D['avg_struggle_minutes']['attr_median'])} minutes, Holm p = {D['avg_struggle_minutes']['p_holm']:.3f}). "
  "The published 15.6 percent increase compared means of a heavy-tailed variable in the unmatched cohort and is withdrawn.", o=74)
DEL(75, 76)
P(f"Attrition users were less productive and slightly less accurate. They solved fewer problems per month ({g(D['problems_solved_per_month']['attr_median'])} vs. {g(D['problems_solved_per_month']['active_median'])}, r = {D['problems_solved_per_month']['r_rb']:.2f}) "
  f"and fewer per rated contest ({g(D['solved_per_contest']['attr_median'])} vs. {g(D['solved_per_contest']['active_median'])}, r = {D['solved_per_contest']['r_rb']:.2f}). "
  f"Their math solve rate ({g(D['math_solve_rate']['attr_median'])} vs. {g(D['math_solve_rate']['active_median'])}, r = {D['math_solve_rate']['r_rb']:.2f}) and data structure solve rate "
  f"({g(D['ds_solve_rate']['attr_median'])} vs. {g(D['ds_solve_rate']['active_median'])}, r = {D['ds_solve_rate']['r_rb']:.2f}) were also lower. All of these survive Holm correction, and all are small effects.", o=77)
DEL(78, 79)
P(f"Activity decay, an Activity Trend Ratio below 0.5 (see Feature Engineering), occurred in {B['attr_pct']:.1f} percent of attrition users against {B['active_pct']:.1f} percent of active users "
  f"(difference {B['diff_pp']:.1f} percentage points, 95 percent CI {B['diff_ci_pp'][0]:.1f}–{B['diff_ci_pp'][1]:.1f}). For inactive users the second half of the span ends at their final submission, "
  "so part of this difference follows from the label definition. For that reason the ratio is reported here but excluded from the audited model.", o=80)
F("fig04_cf_activity_decay", "Fig. 3. Activity decay: share of users whose submissions in the second half of their own active span were fewer than half of those in the first half, with 95 percent Wilson intervals.", o_cap=82)
DEL(81)
P(f"Upsolving does not differ between the groups (Holm p = {D['upsolves_per_contest']['p_holm']:.3f}). In both, about two-thirds of users average fewer than 0.5 upsolves per contest "
  f"({UPS['active']['lt_0.5_pct']:.1f} and {UPS['attrition']['lt_0.5_pct']:.1f} percent). The published contrast of 2.94 against 2.81 on a percentile-binned scale came from the unmatched cohort, "
  "so the pattern the Editorial Dependency Index was formulated to describe is not present in the matched data. We leave the editorial-dependency idea as an untested hypothesis.", o=83)
DEL(84, 85)
H2("Survey: Self-Rated Skill", o=86)
P(f"Students who had stopped CP rated their mathematical ability at {ms_s:.2f} out of 5, against {ms_a:.2f} among students still active (Welch t = {math['stat']:.2f}, p = {math['p']:.3f}, d = {math['eff']:.2f}). "
  f"Data structure understanding followed the same direction, {ds_s:.2f} against {ds_a:.2f}, though that comparison does not reach significance (p = {dsu['p']:.3f}). Neither survives correction.", o=87)
F("fig08_survey_self_ratings", f"Fig. 4. Self-rated skill among active (n = {SF['active']}) and true attrition (n = {SF['true_attrition']}) respondents, mean with 95 percent t-interval. Neither difference survives correction for multiple comparisons.", o_cap=89)
DEL(88)
P("The published version called this pattern, together with weaker practice among students who stopped, the Skill-Application Paradox. Its behavioral half rested on the upsolving item. "
  "That item paired a post-contest upsolving question for active students (Q11) with a general practice-habit question about the month before quitting for stopped students (Q33), under a mapping that placed even regular practice below the top active category. "
  "The resulting group difference reflects the pairing rather than behavior, and it is withdrawn.", o=90)
P("What remains is the confidence half, and it is directional only: students who stopped rated their own ability at least as high as the active group, without any difference being established at this sample size.", o=91)
P("Most of the respondents who stopped had earned an A or A+ in their Data Structures and Algorithms course, so the confidence is not baseless. One interpretation is that strong coursework performance produces confidence in theoretical command, "
  "and that this confidence makes independent practice feel less necessary than it is. We state this as a hypothesis for a prospective study with identical items for all respondents, not as a finding of this one.", o=92)
DEL(93, 94, 95)
H2(PUB[96], o=96)
P(PUB[97], o=97)
P(f"Read at that level, the distribution is still informative. Stalled progress was the most common selection at {RN['n']} of 51 ({RN['pct']:.1f} percent, 95 percent CI {RN['ci'][0]:.1f}–{RN['ci'][1]:.1f}). "
  "It was followed by an unspecified other category and a shift to other technical tracks at 9 each, lack of guidance at 8, academic pressure at 7, and burnout at 6. The intervals overlap widely. "
  "Attrition is spread across several causes rather than dominated by one. Establishing why students leave would require open-ended responses or semi-structured interviews analysed under a stated coding procedure.", o=98)
F("fig07_survey_reasons", "Fig. 5. Self-reported reasons for quitting (Q31, single choice, n = 51) with 95 percent Wilson intervals. Respondents citing a voluntary move to another track (grey) were excluded from the true attrition class.", o_cap=100)
DEL(99)
H2(PUB[101], o=101)
P("Before reporting performance we have to deal with a problem in our own feature set. Account age runs from registration to T_{obs}, so for inactive users it includes the idle period that defines the label. "
  "Contests per month and problems solved per month are both divided by the user's submission span, so they share one denominator. The Intensity Ratio is built from both, and the Activity Trend Ratio compares the two halves of a span that, for inactive users, ends at their final submission. "
  "The audit in the published version removed account age, contests per month and the trend ratio, but kept problems solved per month and the Intensity Ratio, which depend on the same span. "
  "We now apply one rule throughout: every feature whose value depends on the length or end of the observed activity window is removed, and the Intensity Ratio is replaced by its window-invariant form SPC. "
  "Leakage is meant in the sense of Kaufman et al. [30]: information about the target enters through how the data were assembled rather than through anything the subject did.", o=102)
P(f"We report three specifications, all on the data-quality-checked, rating-matched cohort. Specification B keeps all twelve features. Specification C applies the published audit (nine features). "
  f"Specification D applies the consistent audit, with eight window-invariant features. The unmatched specification of the first submission is retained in the deposited code. Table IV gives Specification D in full, and Fig. 6 compares all three.", o=103)
rows4 = []
for n in MODELS + [BASE, RAND]:
    r = Dm[n]; ci = r.get("test_auc_ci")
    rows4.append([n.replace("Baseline: ", "Baseline: "), f"{Bm[n]['rcv_auc_mean']:.3f}", f"{Cm[n]['rcv_auc_mean']:.3f}", f"{r['rcv_auc_mean']:.3f} ± {r['rcv_auc_sd']:.3f}",
                  f"{r['rcv_f1_mean']:.3f} ± {r['rcv_f1_sd']:.3f}", f"{r['rcv_balacc_mean']:.3f}", f"{r['test_auc']:.3f}" + (f" [{ci[0]:.2f}, {ci[1]:.2f}]" if ci else ""), f"{r['test_recall']:.3f}"])
TAB(f"TABLE IV. Codeforces classifier performance on the rating-matched cohort (n = {coh['n']:,}). ROC-AUC under Specifications B and C; full metrics under the audited Specification D",
    ["Classifier", "(B) AUC", "(C) AUC", "(D) AUC ± SD", "(D) F1 ± SD", "(D) Bal. acc.", "(D) Test AUC [95% CI]", "(D) Test rec."], rows4,
    [2100, 850, 850, 1300, 1300, 950, 1550, 900], size=12, o_cap=105,
    note=f"Repeated stratified 5-fold CV ({rep}×, mean ± SD over {5*rep} folds). Test: 20% hold-out (n = {Dm[bD]['n_test']}), bootstrap CI (2,000). Per-fold values under the published protocol are in results/r3_results.json.")
DEL(106)
P(f"The audited models carry a real but modest signal. The best repeated-CV ROC-AUC is {Dm[bD]['rcv_auc_mean']:.3f} ± {Dm[bD]['rcv_auc_sd']:.3f} ({bD}), with Random Forest at {Dm['Random Forest']['rcv_auc_mean']:.3f}. "
  f"Label permutation gives p = {PERM['Random Forest']['p']:.3f} for Random Forest and p = {PERM['Logistic Regression']['p']:.3f} for logistic regression, the smallest values attainable with {nperm} permutations. "
  f"The signal is nonetheless weak. Balanced accuracy does not exceed {max(Dm[n]['rcv_balacc_mean'] for n in MODELS):.3f}, and all {n_below(Dm)} classifiers fall below the F1 of {Dm[BASE]['rcv_f1_mean']:.3f} achieved by always predicting attrition. "
  "Read with F1 alone and without that baseline, as in the published version, such results look stronger than they are.", o=109)
P(f"The three specifications show where the higher published scores came from. With all twelve features the best AUC is {Bm[bB]['rcv_auc_mean']:.3f}. "
  f"The published audit lowers it to {Cm[bC]['rcv_auc_mean']:.3f}, and the consistent audit to {Dm[bD]['rcv_auc_mean']:.3f}. Without the data-quality rule, Specification D reaches {Sm[bS]['rcv_auc_mean']:.3f}, "
  "because the truncated histories, all among active users, add separability that has nothing to do with behavior.", o=110)
P("The tree ensembles hold up better than the linear and distance-based models once the window-dependent columns are gone. This suggests that what remains of the signal is partly interactive rather than additive. "
  "The absolute level is low, however, and we read the result as evidence that behavior before attrition differs measurably but not as a basis for individual prediction.", o=111)
F("fig05_cf_model_comparison", f"Fig. 6. Repeated-CV (a) ROC-AUC and (b) F1 for nine classifiers under Specifications B, C and D (n = {coh['n']:,}; mean ± SD). Dashed lines: chance AUC and the F1 of the always-attrition baseline.", o_cap=113)
DEL(112)
P(f"On the survey layer, a classifier trained on the six comparable items reaches a repeated-CV ROC-AUC of at most {SVM_[sv_best]['rcv_auc_mean']:.3f} ± {SVM_[sv_best]['rcv_auc_sd']:.3f} ({sv_best}; permutation p = {SVP['p']:.3f}). "
  f"No model exceeds the F1 of {SVM_[BASE]['rcv_f1_mean']:.3f} obtained by always predicting the majority class (best: {max(SVM_[n]['rcv_f1_mean'] for n in svmods):.3f}). "
  "The published survey F1 scores (0.924, then 0.832) depended on the branch-confounded features described next. With n = 64 the survey does not support a predictive model, and we do not claim one.", o=114)
rows5 = [[n, f"{SVM_[n]['rcv_auc_mean']:.3f} ± {SVM_[n]['rcv_auc_sd']:.3f}", f"{SVM_[n]['rcv_f1_mean']:.3f} ± {SVM_[n]['rcv_f1_sd']:.3f}", f"{SVM_[n]['rcv_balacc_mean']:.3f}"] for n in svmods + [BASE, RAND]]
TAB(f"TABLE V. Survey classifier performance on the six comparable items (n = {SF['analysis_set']})", ["Classifier", "AUC ± SD", "F1 ± SD", "Bal. acc."], rows5, [2600, 1500, 1500, 1100],
    size=13, wide=False, o_cap=115, note=f"Repeated stratified 5-fold CV ({rep}×). 'attrition' is the majority class here (42 of 64).")
DEL(116, 118, 119)
H2(PUB[120], o=120)
P(PUB[121], o=121)
P("Pairing items does not repair them if the items measure different things. Q27 (a break in the last three months) and Q36 (a break at any point in the CP journey) refer to different periods. "
  "Q11 (upsolving after contests) and Q33 (practice habit in the month before quitting) refer to different behaviors. We therefore report them only within their branch. "
  f"Among active respondents, {SVB['Q27_break_last3months_active_n22'].get('Yes', 0)} of 22 reported a long break in the last three months, and Q11 answers were "
  + ", ".join(f"{k.lower()} {v}" for k, v in SVB['Q11_upsolving_active_n22'].items()) + ". "
  f"Among stopped respondents, {SVB['Q36_break_ever_stopped_n51'].get('Yes', 0)} of 51 reported a long break at some point, and Q33 answers were "
  + ", ".join(f"{k.lower()} {v}" for k, v in SVB['Q33_practice_month_before_quitting_stopped_n51'].items()) + ". "
  "Peer circle density cannot be repaired either, since the item was never put to active respondents.", o=122)
H2(PUB[123], o=123)
P(f"Account tenure ranked first in the unaudited model. That interpretation does not hold: account age is fixed at registration and advanced by the calendar, and for inactive users it includes the idle period itself. "
  f"In the matched cohort, attrition accounts are in fact older, not newer (median {g(D['account_age_months']['attr_median'])} vs. {g(D['account_age_months']['active_median'])} months), which corrects a statement in the published version. "
  "Contest frequency, ranked second, depends on the submission span in the same way as problems solved per month.", o=124)
P("Under the consistent audit, the window-invariant form of the Intensity Ratio, problems solved per rated contest, is the most important feature by permutation importance, followed by "
  + ", ".join(f"{r['feature']} ({r['perm_auc_drop']:.3f})" for r in IMP[1:4])
  + f". The balance between practice and contest participation therefore keeps its place once timing is removed, although its contribution to held-out ROC-AUC is small ({IMP[0]['perm_auc_drop']:.3f}).", o=125)
F("fig06_cf_permutation_importance", "Fig. 7. Permutation importance (drop in held-out ROC-AUC, 30 repeats, mean ± SD) for Random Forest under the audited Specification D.", o_cap=127)
DEL(126)
H2(PUB[128], o=128)
P("The published version applied the survey-trained Random Forest to the 22 active respondents as a proof-of-concept Early Warning System. We withdraw it. "
  "Those 22 students were part of the training data, so an active student scored as high risk, whether in-sample or out of fold, is a misclassification of a known label. "
  "Without follow-up data there is no basis for reading those errors as at-risk profiles. In addition, the risk tiers depended on the confounded upsolving feature and changed with library version (6/10/6 published; 5/8/9 on re-execution). "
  "A prospective design that validates flags against later outcomes is left to future work.", o=129)
DEL(130, 131, 132, 133, 134)

# ---------------------------------------------------------------- V Discussion
H1("V. Discussion", o=135)
H2(PUB[136], o=136)
P(PUB[137], o=137)
P("The two analyses also do not point the same way. In the platform data, users who withdrew were slightly less accurate and less active than matched peers. In the survey, students who stopped rated their own ability slightly higher, without a significant difference. "
  "The upsolving contrast that the published version took as a shared direction rested on non-comparable survey items. "
  "Self-ratings and platform accuracy measure different things, and the survey comparison is retrospective for the stopped group. We therefore treat the two analyses as separate pieces of evidence.", o=138)
H2(PUB[139], o=139)
P("Declining contest and practice frequency is the most consistent behavioral difference we observe, and a programming club can notice it without any model. Structured post-contest review sessions and mentor pairings remain sensible responses to visible disengagement. "
  "Our results do not, however, support automated risk scoring of individual students, and the effect of such interventions would need to be tested in a controlled study.", o=140)
H2(PUB[141], o=141)
P("Several things constrain what we can claim. The survey modeling set is small at 64, and it is confined to Bangladeshi universities, so generalization is untested. "
  "The Codeforces labels rest on an inactivity proxy that cannot separate a permanent departure from a semester spent on coursework, and the peak-rating cut-off at 1500 is a study choice. "
  "Features summarize each account's history up to T_{obs} rather than a fixed window before the stop. A fixed-window rebuild from the raw API records is provided with the deposited code. "
  "Codeforces users are a global population, not specifically university students.", o=142)
P(PUB[143].replace("Features such as upsolving habit and prior consideration of quitting were", "Features such as data structure understanding, mentor support and prior consideration of quitting were"), o=143)
P("Finally, the questionnaire branches asked different questions, which limits the between-group comparisons that are possible. Both datasets are observational throughout, so nothing reported here supports a causal claim.", o=144)

# ---------------------------------------------------------------- VI Conclusion
H1("VI. Conclusion", o=145)
P(f"This paper set out to study attrition in competitive programming using two independent sources: Codeforces behavioral logs after data-quality checks, rating matching and balancing, and an anonymous student survey in Bangladesh. "
  "In the rating-matched cohort, users who withdrew had entered fewer rated contests, solved fewer problems, and were slightly less accurate on math- and data-structure-tagged problems. These differences are significant after correction but small.", o=146)
P("The Skill-Application Paradox is not established. Its behavioral half rested on survey items that cannot be compared across branches. Its confidence half is directional only: the mathematics self-rating gap is nominal at p = "
  f"{math['p']:.3f} and does not survive correction.", o=147)
P(f"On the modeling side, window-invariant behavioral features predict attrition above chance but modestly, with a best repeated-CV ROC-AUC of {Dm[bD]['rcv_auc_mean']:.3f}. No model exceeds the F1 of a trivial baseline, and the survey supports no predictive model at n = 64. "
  f"The difference between {Bm[bB]['rcv_auc_mean']:.3f} with all features and {Dm[bD]['rcv_auc_mean']:.3f} after the audit measures how much apparent predictive power in this kind of study can come from timing artifacts rather than behavior. "
  "The window-invariant form of the Intensity Ratio is the highest-ranked behavioral feature once the audit is applied.", o=148)
P(PUB[149].replace(", and a prospective trial of the Early Warning System with a partner programming club", ", and a prospective, validated early-warning procedure developed with a partner programming club"), o=149)

# ---------------------------------------------------------------- Appendices
H1(PUB[150].replace("Appendix A", "Appendix A"), o=150)
P(PUB[151].replace("Table V", "Table VI").replace("whether it is retained in the specification we report", "whether it is retained in the audited Specification D")
  .replace("(b) denominator or window anchored to the observation date rather than to the user's active span", "(b) depends on the length or end of the user's submission span")
  + " (h) items differ in construct or reference period across branches.", o=151)
T6 = [["CODEFORCES LAYER", "", "", ""],
      ["math_solve_rate", "Accepted / all submissions on math-tagged problems (falls back to acceptance rate)", "API submissions", "yes"],
      ["ds_solve_rate", "Same, data-structure-tagged problems", "API submissions", "yes"],
      ["upsolves_per_contest", "Accepted practice-mode submissions to entered contests, per rated contest", "API submissions", "yes"],
      ["avg_struggle_minutes", "Mean time from first attempt to first acceptance", "API submissions", "yes"],
      ["post_drop_recovery", "Mean rating change in the contest following a rating drop", "API rating history", "yes"],
      ["acceptance_rate", "Accepted submissions over all submissions", "API submissions", "yes"],
      ["editorial_dependency_index", "U × ΔT_{struggle}, (2)", "engineered", "yes"],
      ["solved_per_contest (SPC)", "Distinct problems solved / rated contests", "engineered", "yes"],
      ["intensity_ratio", "P_{month} / (C_{month} + 0.1), (1); replaced by SPC", "engineered", "no (b)"],
      ["problems_solved_per_month", "Distinct problems solved / submission span (months, min. 1)", "API submissions", "no (b)"],
      ["contests_per_month", "Rated contests / submission span (months, min. 1)", "API contest history", "no (b)"],
      ["activity_trend_ratio", "Submissions in second half / first half of own span", "engineered", "no (b)"],
      ["account_age_months", "Months from registration to T_{obs}", "API profile", "no (a)"],
      ["months_since_last_submission", "Months of inactivity at T_{obs}", "API submissions", "no (c)"],
      ["max_rating", "Peak rating attained", "API profile", "no (d)"],
      ["current_rating", "Most recent rating", "API profile", "no (e)"],
      ["SURVEY LAYER", "", "", ""],
      ["math_skill", "Self-rated mathematics ability, 1 to 5", "Q5, all", "yes"],
      ["ds_understanding", "Self-rated data-structure understanding, 1 to 5", "Q14 / Q37", "yes"],
      ["dsa_grade", "Grade in the algorithms course", "Q4, all", "yes"],
      ["prior_exp", "Programming experience before university", "Q3, all", "yes"],
      ["mentor_support", "Access to a mentor or senior guide", "Q22 / Q35", "yes"],
      ["thought_quit", "Ever seriously considered quitting", "Q28 / Q34", "yes"],
      ["long_break", "Break of 15+ consecutive days", "Q27 / Q36", "no (h)"],
      ["upsolving_habit", "Post-contest upsolving vs. practice habit", "Q11 / Q33", "no (h)"],
      ["friend_circle_cp", "Peers in the respondent's circle doing CP", "Q39, stopped only", "no (f)"],
      ["semester, CGPA", "Academic progress measures", "Q1, Q2", "no (g)"]]
TAB("TABLE VI. Complete feature specification for both layers", ["Feature", "Definition (as implemented)", "Source", "Kept (D)"], T6, [2600, 4400, 1700, 900], size=13, o_cap=153)
DEL(154)
H1(PUB[157], o=157)
P(PUB[158], o=158)
H2(PUB[159], o=159)
P(PUB[160].replace("(A+ or A / B+ or B / C or below / not yet taken)", "(A+ or A / B+ or B / C+ or C / D or below / not yet taken)"), o=160)
for i in range(161, 167):
    (H2 if i in (161, 163, 165) else P)(PUB[i], o=i)
H2(PUB[167], o=167)
P("Q3, Q4 and Q5 are common to all respondents. Q14 pairs with Q37, Q22 with Q35, and Q28 with Q34, each with parallel wording. Q11 and Q33 measure different behaviors and Q27 and Q36 refer to different periods, so neither pair is aligned. "
  "Q31 is used for label refinement, with interest in other tracks classifying an intentional exit. Q39 has no active-branch counterpart. Items that are not aligned are reported within their branch only.", o=168)
H1("Data and Code Availability")
P("All data and code needed to verify this article are publicly available in the authors' GitHub repository:")
URL("https://github.com/AZUAD-ISLAM-RUHAN/cp-attrition-prediction")
P("It comprises the pseudonymised Codeforces feature file and the rating-matched modelling set; the anonymised survey responses with response dates; "
  "every analysis script, with pinned library versions; and a single command that regenerates every number, table and figure. Raw API records that contain account handles are available to the editor on request.", noindent=True)
H1(PUB[169], o=169)
P("The authors thank the students who took the time to answer the survey, and the Research Ethics Committee of Metropolitan University for reviewing the study. We are also grateful to the two anonymous reviewers, "
  "and to the AJSE Editorial Desk, whose detailed scrutiny led to the corrections in this version of the paper.", o=170)
H1(PUB[171], o=171)
for i in range(172, 180): P(PUB[i], o=i)
H1(PUB[180], o=180)
P(PUB[181] + " In preparing this corrected version, Claude (Anthropic) was used to help re-run and audit the analysis code, verify references against bibliographic databases, and draft revised text; the authors checked every output. "
  "AI coding assistants were also used to help draft parts of the original analysis code, which the authors reviewed and ran.", o=181)

REFS = [PUB[i] for i in range(183, 214)]
REFS = [r.split("] ", 1)[1] for r in REFS]
REFS[4] = "P. Kinnunen and L. Malmi, “Why students drop out CS1 course?” in Proc. 2nd Int. Workshop on Computing Education Research (ICER), 2006, pp. 97–108."
REFS[8] = "M. Kloft, F. Stiehler, Z. Zheng, and N. Pinkwart, “Predicting MOOC dropout over weeks using machine learning methods,” in Proc. EMNLP 2014 Workshop on Analysis of Large Scale Social Interaction in MOOCs, 2014, pp. 60–65."
REFS[9] = "P. Ihantola et al., “Educational data mining and learning analytics in programming: Literature review and case studies,” in Proc. ITiCSE Working Group Reports, 2015, pp. 41–63."
REFS[5] = "M. Guzdial, Learner-Centered Design of Computing Education: Research on Computing for Everyone, Synthesis Lectures on Human-Centered Informatics, vol. 8, no. 6. Morgan & Claypool, 2015."
REFS += ["S. Holm, “A simple sequentially rejective multiple test procedure,” Scand. J. Statist., vol. 6, no. 2, pp. 65–70, 1979.",
         "H. B. Mann and D. R. Whitney, “On a test of whether one of two random variables is stochastically larger than the other,” Ann. Math. Statist., vol. 18, no. 1, pp. 50–60, 1947.",
         "E. B. Wilson, “Probable inference, the law of succession, and statistical inference,” J. Amer. Statist. Assoc., vol. 22, no. 158, pp. 209–212, 1927.",
         "M. Ojala and G. C. Garriga, “Permutation tests for studying classifier performance,” J. Mach. Learn. Res., vol. 11, pp. 1833–1863, 2010."]
PUBREFS = [PUB[i].split("] ", 1)[1] for i in range(183, 214)]
BIOS = json.load(open(f"{MB}/inputs/pub_tables.json"))[5:12]
BIOS = [b[0][0] for b in BIOS]

# ---- AJSE template conformance pass (IEEE style): American spelling, "Acknowledgment", "whereas" for contrast.
import re as _re
_US = {"modelling": "modeling", "modelled": "modeled", "pseudonymised": "pseudonymized", "anonymised": "anonymized",
       "recognised": "recognized", "analysed": "analyzed", "practised": "practiced", "practising": "practicing",
       "practise": "practice", "characterisation": "characterization", "Acknowledgement": "Acknowledgment",
       "while the active class is not": "whereas the active class is not"}
_RX = _re.compile(r"(?<![\w/.])(" + "|".join(sorted(map(_re.escape, _US), key=len, reverse=True)) + r")(?!\w|\.\w)")   # skips file names such as x_modelling_set.csv
def _us(s): return _RX.sub(lambda m: _US[m.group(1)], s) if isinstance(s, str) else s
for _b in blocks:
    for _k in ("text", "cap", "note"):
        if _b.get(_k): _b[_k] = _us(_b[_k])
    if _b.get("rows"): _b["rows"] = [[_us(c) for c in r] for r in _b["rows"]]
    if _b.get("head"): _b["head"] = [_us(c) for c in _b["head"]]
for _k in ("abstract", "notice"): meta[_k] = _us(meta[_k])
PHOTOS = [f"{MB}/inputs/author_photos/{p}" for p in ["image16.jpg", "image17.jpg", "image18.jpg", "image19.png", "image19.png", "image20.jpg", "image21.jpg"]]
used = {b.get("o") for b in blocks if b.get("o") is not None}
json.dump({"meta": meta, "pub_abstract": PUB[4].replace("Abstract—", ""), "blocks": blocks, "refs": REFS, "pub_refs": PUBREFS, "bios": BIOS, "photos": PHOTOS,
           "pub": PUB}, open(f"{MB}/output/content_pub.json", "w"), ensure_ascii=False, indent=1)
skipped = [i for i, t in enumerate(PUB[:214]) if t.strip() and i not in used and i not in (0, 1, 3, 4, 5) and not (182 <= i <= 213)]
print("blocks", len(blocks), "| abstract words", len(meta["abstract"].split()), "| published paragraphs not mapped:", skipped)
