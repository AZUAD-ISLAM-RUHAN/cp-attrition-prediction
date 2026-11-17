"""Revised manuscript (v3), responding to the reviewer report of 8 November 2026 (AJSE Paper 1999).
Every number is read from results/ (r3_table1_cohort.json, r4_results.json); references are cited by key ([@key])
and numbered in order of first citation. Writes manuscript_build/v3/output/content_v3.json for render_pub.js:
    CONTENT=manuscript_build/v3/output/content_v3.json node manuscript_build/render_pub.js clean <out.docx>
Placeholders ⟦...⟧ mark facts only the authors can supply, and the analysis that needs the raw API records (B1)."""
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
V3 = Path(__file__).resolve().parent; MB = V3.parent; ROOT = MB.parent
sys.path.insert(0, str(V3)); from refs_v3 import REFS
R = json.load(open(ROOT / "results" / "r4_results.json"))
T1 = {r["stage"]: r["accounts"] for r in json.load(open(ROOT / "results" / "r3_table1_cohort.json"))}
R5 = json.load(open(ROOT / "results" / "r5_b4_e4_results.json")); B4R = R5["b4_return_check"]
B1R = json.load(open(ROOT / "results" / "r5_b1_results.json")); W6, W12 = B1R["windows"]["6_months"], B1R["windows"]["12_months"]
A6R = json.load(open(ROOT / "results" / "r5_a6_feature_reproduction.json"))
b1_auc = [w["models"][m]["auc"] for w in (W6, W12) for m in ("LR", "RF")]
b1_signal = all(w["models"][m]["auc_ci95"][0] > 0.5 for w in (W6, W12) for m in ("LR", "RF"))
def b1sig(w): return [e for e in w["effect_sizes"] if e["p_holm"] < 0.05]
a6_min = min(A6R["attrition"]["share_reproducing_released_value"].values())
def b1_effect_sentence():
    both = [e for e in sorted(b1sig(W6), key=lambda e: e["r"]) if e["feature"] in {x["feature"] for x in b1sig(W12)}]
    r12 = {x["feature"]: x["r"] for x in W12["effect_sizes"]}
    def nm(f): return nice.get(f, f).replace(" (min)", "").lower()
    items = [f"{nm(e['feature'])} (r = {f2(e['r'])} and {f2(r12[e['feature']])})" for e in both]
    lst = items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]
    dirs = {e["r"] < 0 for e in both}
    if not items: return "No single measure differs after Holm correction in both windows."
    word = {1: "One measure", 2: "Two measures", 3: "Three measures", 4: "Four measures", 5: "Five measures"}.get(len(items), f"{len(items)} measures")
    return (f"{word} {'is' if len(items) == 1 else 'are'} {'lower' if dirs == {True} else 'different'} in the attrition group in both windows after Holm correction: {lst}.")
SC = B1R["subset_whole_history_check"]
FIG = str(ROOT / "figures" / "v3")
CONCEPT_DOI, VERSION_DOI = "10.5281/zenodo.24054464", "10.5281/zenodo.24054465"
REPO = "https://github.com/AZUAD-ISLAM-RUHAN/cp-attrition-prediction"
blocks = []
def H1(t): blocks.append({"t": "h1", "text": t, "o": None})
def H2(t): blocks.append({"t": "h2", "text": t, "o": None})
def P(t, noindent=False): blocks.append({"t": "p", "text": t, "o": None, "noindent": noindent})
def EQ(t, n): blocks.append({"t": "eq", "text": t, "num": n, "o": None})
def F(name, cap, wide=False): blocks.append({"t": "fig", "path": f"{FIG}/{name}.png", "cap": cap, "o": None, "wide": wide})
def TAB(cap, head, rows, w, note=None, wide=True): blocks.append({"t": "tab", "cap": cap, "head": head, "rows": rows, "w": w, "note": note, "size": 16, "wide": wide, "o": None})
def URL(u): blocks.append({"t": "url", "text": u, "o": None})
f2, f3 = (lambda x: f"{x:.2f}"), (lambda x: f"{x:.3f}")
def pfmt(p): return "< 0.001" if p < 0.001 else f"{p:.3f}"
def ci(a): return f"[{a[0]:.3f}, {a[1]:.3f}]"

# ------------------------------------------------------------------ numbers
coh = R["cohort"]; M = R["models"]; LR, RF = M["LR"], M["RF"]; B2 = R["b2_balanced_resamples"]; B3 = R["b3"]; B5 = R["b5"]; B6 = R["b6_ablation"]
D = {d["feature"]: d for d in R["descriptives"]}
n_all = T1["Released feature file (>=5 rated contests, current rating 1-2399)"]; n2400 = T1["After peak rating < 2400"]
n_dq = T1["After data-quality check (complete submission history)"]; n_act = T1["Active at T_obs"]; n_inact = T1["Inactive >= 3 months at T_obs"]
n_ie = T1["Intentional Exit (excluded)"]
raw = pd.read_csv(ROOT / "data" / "cf_attrition_features.csv")
q1 = raw.total_submissions < raw.total_contests; q2 = (~q1) & (raw.contests_per_month > 15); flag = raw[q1 | q2]
rule = {k[:2]: v for k, v in B3["rules"].items()}
b4 = {(d["rating_cut"], int(d["inactive_months_min"])): d for d in R["b4"]}
b4_rf = [d["rf_auc"] for d in R["b4"]]; b4_lr = [d["lr_auc"] for d in R["b4"]]
all_auc = [LR["auc_oof"], RF["auc_oof"], B2["LR"]["mean"], B2["RF"]["mean"], B5["lr_auc_mean"], B5["rf_auc_mean"]] + b4_rf + b4_lr + \
          [v[m] for v in B3["rules"].values() for m in ("rf_auc", "lr_auc")]
lo_auc, hi_auc = min(all_auc), max(all_auc)
spc, ma, da, acc = D["solved_per_contest"], D["math_solve_rate"], D["ds_solve_rate"], D["acceptance_rate"]
imp = R["importance_folds"]; top = max(imp, key=lambda f: imp[f]["mean"])
nice = {d["feature"]: d["label"] for d in R["descriptives"]}
sig = [d for d in R["descriptives"] if d["p_holm"] < 0.05]

meta = {"title": "Behavioral Differences Between Active and Inactive Users in Competitive Programming: A Rating-Restricted Analysis of Codeforces Activity",
        "authors": "Azuad Islam Ruhan, Golam Mostofa Naeem, Rakibul Islam Rafi, Sherin Afrin Mim, Nazira Bani Opi, Dewan Fahad Chowdhury, and Md. Rejaul Korim Sadi",
        "notice": "",
        "index": "Codeforces, competitive programming, educational data mining, learner disengagement, robustness analysis"}
meta["abstract"] = (
 "We compared the recorded behavior of competitive programmers who became inactive on Codeforces with that of active users of similar skill. "
 f"From {n_all:,} accounts collected through the public Codeforces application programming interface in June 2026, we removed {len(flag)} accounts whose retrieved submission histories were incomplete "
 f"and restricted both groups to a peak rating below 1500. This left {coh['active']:,} active accounts and {coh['attrition']} accounts with no submission for at least three months, labeled attrition. "
 f"The differences between the groups were small. Accounts labeled attrition accepted smaller shares of their attempts, overall and on mathematics and data-structure problems (rank-biserial r from {f2(min(ma['r'], da['r'], acc['r']))} to {f2(max(ma['r'], da['r'], acc['r']))}), "
 f"and solved fewer problems per rated contest (median {f2(spc['attr_median'])} versus {f2(spc['active_median'])}; r = {f2(spc['r'])}); struggle time, upsolving and recovery after rating drops did not differ after correction for multiple testing. "
 f"Two pre-specified models using eight features that do not depend on the length of the observation window reached cross-validated areas under the receiver operating characteristic curve of {f3(LR['auc_oof'])} (logistic regression) and {f3(RF['auc_oof'])} (random forest), "
 f"with probabilities barely better than the base rate. Across random samples, stricter cleaning rules, other definitions of inactivity and matching on account tenure, the value ranged from {lo_auc:.2f} to {hi_auc:.2f}. "
 + (f"Using only activity from the 6 or 12 months ending three months before each user's last submission, it was {min(b1_auc):.2f} to {max(b1_auc):.2f}, so a small difference precedes inactivity, but it is too weak to identify individual users at risk. "
    if b1_signal else
    f"Using only activity from the 6 or 12 months ending three months before each user's last submission, it was {min(b1_auc):.2f} to {max(b1_auc):.2f}, so no reliable difference is present before inactivity, and the results do not support predicting it. ") +
 "The data and code are publicly archived, and one command regenerates every reported number.")

# ------------------------------------------------------------------ I Introduction
H1("I. Introduction")
P("Competitive programming (CP) is a widely used extra-curricular route for building algorithmic reasoning in computer science students [@laaksonen], [@skiena]. "
  "Platforms such as Codeforces supply immediate verdicts, timed contests and a public rating against which progress can be measured [@combefis]. Problems arrive without hints, under fixed time and memory limits, and the learner decides alone what to try next [@halim].")
P("Many learners who start do not stay. Dropout from introductory programming courses is well documented: students who leave most often report a lack of time or motivation and difficulty with the course [@kinnunen], and learning to program is widely recognized as hard [@robins]. "
  "Educational data mining has modeled dropout from grade records and from the activity logs of massive open online courses [@romero], [@kloft]. Voluntary competitive practice sits outside these settings: it happens off the transcript and has no deadline, whereas data-mining studies of programming have mostly examined courses [@ihantola].")
P("This paper asks what the public activity records of a large platform can and cannot tell us about learners who stop. We address three questions. "
  "RQ1: Do users who become inactive on Codeforces differ in their recorded behavior from active users whose peak rating lies in the same range, and by how much? "
  "RQ2: How well do behavioral features that do not depend on the length of the observation window separate the two groups, and how sensitive is that answer to the choices made in the analysis: which active users are sampled, how incomplete records are cleaned, how inactivity is defined, and how long users have held their accounts? "
  "RQ3: Is a difference already present in the activity recorded before users became inactive?")
P("The paper makes three contributions. First, it builds a rating-restricted cohort of "
  f"{coh['n']:,} Codeforces accounts with a documented stage-by-stage flow and an audit of incomplete platform histories. "
  "Second, it reports the size of the behavioral differences, with confidence intervals, separating measures that are comparable between active and inactive users from measures that depend on how long each user was observed. "
  "Third, it shows how a modest classification signal behaves across analysis choices, including measures restricted to the months before inactivity, reporting discrimination, precision–recall performance and calibration rather than a single best score. The data and code are archived with a DOI and regenerate every number in the paper.")

# ------------------------------------------------------------------ II Related Work
H1("II. Related Work")
H2("Educational Data Mining and Dropout")
P("Work on student retention has moved from predicting degree completion with demographic and first-year records [@romero], [@baker] to modeling dynamic behavior such as submission patterns and forum participation in online courses [@kloft]. "
  "In introductory programming, data logged while students program predicted course performance better than traditional background factors [@watson], and data-mining techniques can identify students at risk of failure early in a course [@costa]. Most of this work studies enrolled students with a defined course end, where dropout is observed directly.")
H2("Programming Platform Telemetry")
P("Studies of programming environments and online judges treat compilation errors, inter-submission gaps and wrong-answer rates as signals of difficulty [@ihantola], [@watson]. "
  "These logs record what learners did, not why. Voluntary competitive participation also differs from course work: there is no deadline, and disengagement unfolds over weeks or months, so the moment of quitting is not observed but has to be inferred from inactivity.")
H2("Motivation and Persistence")
P("Motivational orientation and self-efficacy are established predictors of persistence [@deci], [@bandura], and the adoption of programming contests has been described as a diffusion process driven by peers and perceived benefit [@raman]. "
  "None of these factors is visible in platform logs, which bounds what a log-based study can explain. Using learners' activity data also raises questions of agency and consent [@prinsloo], which shaped our decision to publish only pseudonymized aggregates.")

# ------------------------------------------------------------------ III Data and Methods
H1("III. Data and Methods")
H2("Data Collection")
P("Submission histories, contest records and profile data were retrieved from the public Codeforces application programming interface (API). The sampling frame was the platform's list of rated users (user.ratedList), from which a pool of 26,000 handles was drawn, stratified by current rating band in proportion to band size with at least 50 per band (seed 42). "
  f"Accounts were retained only if they had at least five rated contests, a current rating between 1 and 2399 and at least one accepted submission; {n_all:,} accounts met these criteria. "
  "For each account the collection requested up to 10,000 submissions (user.status) and the full rating history (user.rating).")
P("All measures refer to one observation time, T_{obs}, the moment the feature file was built. The collection notebook did not record it; matching each account's rounded age in the released file to its registration time in the raw API records places it on 23 June 2026 between 13:41 and 13:44 UTC. "
  "Handles are replaced by a salted hash in every released file.")
H2("Labels")
P("We call an account inactive when its last retrieved submission lies at least three months before T_{obs}, where months are computed as elapsed days divided by 30 and the threshold is applied to the unrounded value (at least 90 days). "
  f"Accounts that meet this condition and never reached a rating of 1500 are labeled attrition. The label records inactivity at one date; it does not establish that a user has stopped for good, and Section IV-D tests how the results change with longer inactivity thresholds. "
  "Accounts with a last submission less than 90 days before T_{obs} are labeled active.")
P(f"The rating restriction applies to both groups. Inactive accounts that had reached 1500 ({n_ie}) are excluded, because leaving after reaching an intermediate level may have other causes, and active accounts are likewise restricted to a peak rating below 1500. "
  "Without this restriction, a classifier could separate the groups partly by skill level, since the inactive group would be capped by construction and the active group would not. "
  "The threshold of 1500 is a study choice inside the Codeforces Specialist band (1400–1599); Section IV-D repeats the analysis with 1400 and 1600.")
H2("Incomplete Histories")
P(f"Every rated contest requires at least one submission, so an account with fewer retrieved submissions than rated contests has an incomplete history. Such accounts, and accounts with more than 15 rated contests per month of submission span, were excluded. "
  f"The rule removed {len(flag)} of the {n_all:,} accounts ({100 * len(flag) / n_all:.1f}%), all of them active at T_{{obs}}. "
  f"The removed accounts had a median of {int(flag.total_submissions.median())} retrieved submissions against a median of {int(flag.total_contests.median())} rated contests. "
  "The collection requested complete histories in a single call, and its consistency check flagged only responses that were completely empty, so partial responses were not detected at collection time. "
  "The feature file does not show why the affected accounts are all active; the raw API responses are needed to establish the cause (Section V). "
  "Because the rule was defined after the data had been inspected, Section IV-D also reports three stricter rules.")
H2("Behavioral Measures")
P("We use eight measures that do not depend on how long an account was observed. Six are taken directly from the API data: the shares of accepted attempts overall, on mathematics-tagged problems and on data-structure-tagged problems; "
  "mean struggle time, the time from the first attempt on a problem to its acceptance; upsolves per rated contest, accepted practice submissions on problems of contests the user took part in; and post-drop recovery, the mean rating change in the contest that follows a rating drop (0 for accounts without a drop). Two are constructed:")
EQ("SPC_{i} = S_{i} / C_{i}", 1)
P("where S_{i} is the number of distinct problems user i solved and C_{i} the number of rated contests entered, and", noindent=True)
EQ("EDI_{i} = U_{i} × ΔT_{struggle,i}", 2)
P("where U_{i} is upsolves per rated contest and ΔT_{struggle,i} is mean struggle time in minutes. Problems solved per contest (SPC) relates practice volume to contest participation. The Editorial Dependency Index (EDI) was constructed to capture slow, after-the-fact solving. "
  "Four further measures, rated contests per month, problems solved per month, account age and the total number of rated contests, depend on the length of the observed activity span, which ends at the last submission for inactive users and at T_{obs} for active users. They are reported descriptively but are not used in the models. "
  "Table V in Appendix A gives every definition as implemented.", noindent=True)
H2("Statistical Analysis")
P("Group differences are reported as medians with interquartile ranges and as rank-biserial correlations [@kerby], r = P(X_{attrition} > X_{active}) − P(X_{attrition} < X_{active}), so that a negative r means lower values in the attrition group. "
  "Confidence intervals come from 1,000 bootstrap resamples of accounts [@efron]. Table II reports both the Mann–Whitney p-value [@mann] and the Holm-adjusted p-value over the 13 measures tested [@holm], labeled as such.")
P("Two models were specified before the analysis: logistic regression and a random forest with 200 trees [@breiman], both implemented in scikit-learn [@pedregosa] with median imputation and standardization fitted inside each training fold. "
  "Using all eligible accounts avoids depending on one random sample of active users. Performance is estimated by stratified 5-fold cross-validation repeated five times [@kohavi]. The main measure is the area under the receiver operating characteristic curve (ROC-AUC), with a 95% confidence interval from 2,000 bootstrap resamples of the out-of-fold predictions; every metric is computed within each repeat and then averaged over the five repeats. "
  f"Because only {100 * coh['prevalence']:.0f}% of accounts are labeled attrition, a class imbalance under which ROC-AUC alone can give a favorable impression [@he], we also report the area under the precision–recall curve (PR-AUC) [@saito], whose value for random guessing equals that share, and the Brier score with a calibration curve [@brier], [@niculescu]. "
  "Restricting the analysis to two models limits the optimism that comes from selecting the best of many [@cawley]. Features that leak information about the label from outside the observation period were excluded by design [@kaufman].")
P("To test how much the results depend on analysis choices, we repeat the models (i) on 50 balanced samples of active users, (ii) under stricter rules for incomplete histories, (iii) with inactivity thresholds of 3, 6 and 12 months crossed with rating limits of 1400, 1500 and 1600, and (iv) after matching each attrition account to the active account nearest in account age and number of rated contests. "
  "The contribution of the two constructed measures is tested by removing them and comparing paired cross-validation folds. Permutation importance is computed on every held-out fold; it is reported with caution because several measures are correlated [@strobl].")

# ------------------------------------------------------------------ IV Results
H1("IV. Results")
P("To test whether the difference is present before users become inactive (RQ3), the eight model measures were recomputed from a window that ends three months before each account's last submission and covers the preceding 6 or 12 months; "
  "active accounts, whose last submission lies close to T_{obs}, are treated in the same way. Accounts need at least five rated contests and one accepted submission inside the window. "
  "For this analysis the submission and rating histories of the cohort were retrieved again from the public API in November 2026, at a rate within the platform's limits, and cut at T_{obs}. "
  f"Histories were obtained for all {B1R['cohort']['attrition']} attrition accounts and for {B1R['cohort']['active']:,} of the {coh['active']:,} active accounts ({100 * B1R['cohort']['active'] / coh['active']:.0f}%) before the retrieval was stopped; "
  f"on these accounts the whole-history models give ROC-AUC {f3(SC['accounts retrieved again']['LR_auc'])} and {f3(SC['accounts retrieved again']['RF_auc'])}, as on the full cohort ({f3(SC['full cohort']['LR_auc'])} and {f3(SC['full cohort']['RF_auc'])}), so the subset does not change the result. "
  f"For the {A6R['attrition']['accounts_compared']} attrition accounts, which made no submissions after their retrieval in June, the measures recomputed from these histories equal the released values for at least {100 * a6_min:.1f}% of accounts on every measure, so the retrieval reproduces the data analyzed above. "
  "The same two models and cross-validation are used.")
H2("Cohort")
P(f"Table I gives the count at every stage. The analysis cohort contains {coh['n']:,} accounts: {coh['active']:,} active and {coh['attrition']} labeled attrition. "
  f"The rating restriction leaves the two groups with nearly identical peak ratings (median {coh['peak_rating']['active_median']:.0f} versus {coh['peak_rating']['attrition_median']:.0f}; standardized mean difference {coh['peak_rating']['smd']:.2f}). "
  f"The groups differ in tenure: the active accounts are younger (median account age {B5['before']['age_median_active']:.1f} versus {B5['before']['age_median_attrition']:.1f} months) but have entered the same median number of rated contests ({B5['before']['contests_median_active']:.0f}).")
TAB("TABLE I. Cohort construction, stage by stage",
    ["Stage", "Accounts"],
    [["Retrieved from the API (≥ 5 rated contests, current rating 1–2399)", f"{n_all:,}"],
     ["Peak rating below 2400", f"{n2400:,}"],
     ["Complete submission history (data-quality rule)", f"{n_dq:,}"],
     ["   active at T_{obs}", f"{n_act:,}"],
     ["   inactive for ≥ 3 months at T_{obs}", f"{n_inact:,}"],
     ["Peak rating below 1500: active", f"{coh['active']:,}"],
     ["Peak rating below 1500: inactive (labeled attrition)", f"{coh['attrition']}"],
     ["Analysis cohort", f"{coh['n']:,}"]],
    [7000, 1800],
    note=f"The data-quality rule removes {len(flag)} accounts from the full file and {n2400 - n_dq} after the peak-rating step. Inactive accounts with a peak rating of 1500 or more ({n_ie}) and active accounts with a peak of 1500 or more ({n_act - coh['active']:,}) are excluded.", wide=False)
H2("Group Differences")
rows = []
for f in ["solved_per_contest", "math_solve_rate", "ds_solve_rate", "acceptance_rate", "avg_struggle_minutes", "upsolves_per_contest",
          "post_drop_recovery", "editorial_dependency_index", "contests_per_month", "problems_solved_per_month", "account_age_months", "total_contests", "subs_per_contest"]:
    d = D[f]; fmt = (lambda v: f"{v:.3f}") if d["active_median"] < 1 else (lambda v: f"{v:.1f}") if d["active_median"] < 100 else (lambda v: f"{v:.0f}")
    rows.append([d["label"] + ("†" if d["window_dependent"] else "") + ("‡" if f == "subs_per_contest" else ""),
                 f"{fmt(d['active_median'])} [{fmt(d['active_q1'])}, {fmt(d['active_q3'])}]", f"{fmt(d['attr_median'])} [{fmt(d['attr_q1'])}, {fmt(d['attr_q3'])}]",
                 f"{d['r']:.2f} [{d['r_ci95'][0]:.2f}, {d['r_ci95'][1]:.2f}]", pfmt(d["p"]), pfmt(d["p_holm"])])
P(f"Table II and Fig. 1 report all measures. Among the eight measures used in the models, the largest differences are in acceptance: accounts labeled attrition accepted smaller shares of their attempts on mathematics-tagged problems "
  f"(median {f3(ma['attr_median'])} versus {f3(ma['active_median'])}; r = {f2(ma['r'])}, 95% CI [{f2(ma['r_ci95'][0])}, {f2(ma['r_ci95'][1])}]), overall (r = {f2(acc['r'])}) and on data-structure-tagged problems (r = {f2(da['r'])}). "
  f"They also solved fewer problems per rated contest, a median of {f2(spc['attr_median'])} against {f2(spc['active_median'])} (r = {f2(spc['r'])}, 95% CI [{f2(spc['r_ci95'][0])}, {f2(spc['r_ci95'][1])}]). "
  f"Struggle time, upsolving, post-drop recovery and the Editorial Dependency Index do not differ after Holm correction. Every effect is small: no measure used in the models exceeds |r| = {max(abs(D[f]['r']) for f in R['settings']['features']):.2f}.")
P(f"The window-dependent measures show larger differences, partly by construction. Accounts labeled attrition entered fewer rated contests per month (median {f2(D['contests_per_month']['attr_median'])} versus {f2(D['contests_per_month']['active_median'])}) and solved fewer problems per month "
  f"({f2(D['problems_solved_per_month']['attr_median'])} versus {f2(D['problems_solved_per_month']['active_median'])}). Their accounts are older, so their activity is spread over a longer span, while the total number of rated contests is similar. "
  "These measures are therefore descriptive only.")
TAB("TABLE II. Behavioral measures, active (n = " + f"{coh['active']:,}" + ") versus attrition (n = " + f"{coh['attrition']}" + ")",
    ["Measure", "Active, median [IQR]", "Attrition, median [IQR]", "r [95% CI]", "p (unadj.)", "p (Holm)"], rows,
    [2700, 1750, 1750, 1500, 900, 900],
    note="r: rank-biserial correlation, P(attrition > active) − P(attrition < active); negative values mean lower values in the attrition group. "
         "p (unadj.): two-sided Mann–Whitney test; p (Holm): adjusted over the 13 measures. † Depends on the length of the observed activity span; descriptive only, not used in the models. "
         "‡ Data-quality diagnostic (Section IV-D).")
F("fig1_effect_sizes", "Fig. 1. Rank-biserial correlations with 95% bootstrap confidence intervals for the twelve behavioral measures. Filled markers: measures used in the models; open markers: measures that depend on the length of the observed activity span.")
H2("Model Performance")
P(f"Table III summarizes performance. Logistic regression reached a cross-validated ROC-AUC of {f3(LR['auc_oof'])} (95% CI {ci(LR['auc_ci95'])}) and the random forest {f3(RF['auc_oof'])} ({ci(RF['auc_ci95'])}). "
  f"Both are above chance, but the separation is weak. The PR-AUC values ({f3(LR['pr_auc'])} and {f3(RF['pr_auc'])}) exceed the base rate of {f3(LR['pr_auc_baseline'])}, and the Brier scores ({f3(LR['brier'])} and {f3(RF['brier'])}) are close to the value of {f3(LR['brier_baseline'])} obtained by predicting the base rate for every account. "
  f"In Fig. 2 the mean predicted probability per decile ranges from {min(RF['calibration_repeat1']['mean_predicted']):.2f} to {max(RF['calibration_repeat1']['mean_predicted']):.2f} for the random forest and from {min(LR['calibration_repeat1']['mean_predicted']):.2f} to {max(LR['calibration_repeat1']['mean_predicted']):.2f} for logistic regression; "
  "the random forest underestimates the share of attrition in its lowest deciles and overestimates it in its highest decile. The models rank accounts slightly better than chance but do not provide usable individual risk estimates.")
TAB("TABLE III. Cross-validated performance of the two pre-specified models (n = " + f"{coh['n']:,}" + ")",
    ["Model", "ROC-AUC [95% CI]", "Fold SD", "PR-AUC [95% CI]", "Brier score", "Balanced accuracy"],
    [["Logistic regression", f"{f3(LR['auc_oof'])} {ci(LR['auc_ci95'])}", f3(LR["auc_fold_sd"]), f"{f3(LR['pr_auc'])} {ci(LR['pr_auc_ci95'])}", f3(LR["brier"]), f3(LR["balanced_accuracy_at_base_rate"])],
     ["Random forest", f"{f3(RF['auc_oof'])} {ci(RF['auc_ci95'])}", f3(RF["auc_fold_sd"]), f"{f3(RF['pr_auc'])} {ci(RF['pr_auc_ci95'])}", f3(RF["brier"]), f3(RF["balanced_accuracy_at_base_rate"])],
     ["Reference: chance / base rate", "0.500", "–", f3(LR["pr_auc_baseline"]), f3(LR["brier_baseline"]), "0.500"]],
    [2300, 2000, 900, 2000, 1200, 1500],
    note="Stratified 5-fold cross-validation repeated five times on all eligible accounts; each metric is computed on the out-of-fold predictions of one repeat and averaged over the five repeats. Confidence intervals: 2,000 bootstrap resamples of accounts in each repeat, bounds averaged over repeats. "
         "Balanced accuracy at a threshold that flags the same share of accounts as the base rate. The base-rate Brier score is p(1 − p) with p the share of attrition.")
F("fig2_calibration", "Fig. 2. Calibration of the out-of-fold predicted probabilities of the first cross-validation repeat (deciles) with 95% bootstrap bands. The dotted line marks the base rate of attrition.")
H2("Robustness to Analysis Choices")
P(f"Table IV and Fig. 3 repeat the models under different choices. On {len(B2['RF']['values'])} balanced samples of {coh['attrition']} active accounts, the random forest averaged {f3(B2['RF']['mean'])} (2.5th–97.5th percentile {f3(B2['RF']['p2_5'])}–{f3(B2['RF']['p97_5'])}) and logistic regression {f3(B2['LR']['mean'])} ({f3(B2['LR']['p2_5'])}–{f3(B2['LR']['p97_5'])}). "
  "A result reported from a single sample can therefore differ from the typical value by several hundredths.")
P(f"Among the accounts kept by the data-quality rule, {B3['subs_per_contest_cohort']['active']['lt2']} active accounts but only {B3['subs_per_contest_cohort']['attrition']['lt2']} attrition accounts have fewer than two submissions per rated contest; "
  f"the medians are {f2(B3['subs_per_contest_cohort']['active']['median'])} and {f2(B3['subs_per_contest_cohort']['attrition']['median'])}. Some incomplete histories may therefore remain among active accounts. "
  f"Requiring at least 2, 3 or 5 submissions per contest changes the random-forest ROC-AUC to {f3(rule['R1']['rf_auc'])}, {f3(rule['R2']['rf_auc'])} and {f3(rule['R3']['rf_auc'])}, and the logistic-regression value to {f3(rule['R1']['lr_auc'])}, {f3(rule['R2']['lr_auc'])} and {f3(rule['R3']['lr_auc'])}.")
P(f"Longer inactivity thresholds give similar or slightly higher values: at 12 months with the 1500 limit, {f3(b4[(1500, 12)]['rf_auc'])} for the random forest and {f3(b4[(1500, 12)]['lr_auc'])} for logistic regression, with {b4[(1500, 12)]['attrition']} accounts labeled attrition. "
  f"Rating limits of 1400 and 1600 leave the results essentially unchanged. The difference in problems solved per contest keeps its direction in all nine definitions (r from {min(d['r_solved_per_contest'] for d in R['b4']):.2f} to {max(d['r_solved_per_contest'] for d in R['b4']):.2f}).")
P(f"Matching each attrition account to the active account nearest in account age and number of rated contests removes the tenure difference (median age of the matched active accounts {B5['after_matching']['age_median_active']:.1f} months). "
  f"The ROC-AUC then falls to {f3(B5['rf_auc_mean'])} for the random forest (range over {B5['n_matchings']} matchings {f3(B5['rf_auc_min'])}–{f3(B5['rf_auc_max'])}) and {f3(B5['lr_auc_mean'])} for logistic regression. "
  "Part of the signal is therefore associated with tenure. Across all the analyses in Table IV the values stay between "
  f"{lo_auc:.2f} and {hi_auc:.2f}: a small but persistent difference, not a basis for identifying individual users.")
trows = [["Primary: all eligible accounts", f"{coh['n']:,}", f"{f3(LR['auc_oof'])} {ci(LR['auc_ci95'])}", f"{f3(RF['auc_oof'])} {ci(RF['auc_ci95'])}"],
         [f"Balanced samples ({len(B2['RF']['values'])} draws), mean [2.5–97.5%]", f"{2 * coh['attrition']:,}", f"{f3(B2['LR']['mean'])} [{f3(B2['LR']['p2_5'])}, {f3(B2['LR']['p97_5'])}]", f"{f3(B2['RF']['mean'])} [{f3(B2['RF']['p2_5'])}, {f3(B2['RF']['p97_5'])}]"]]
for k, lab in [("R1", "≥ 2 submissions per contest"), ("R2", "≥ 3 submissions per contest"), ("R3", "≥ 5 submissions per contest")]:
    v = rule[k]; trows.append([lab, f"{v['n']:,}", f"{f3(v['lr_auc'])} ± {f3(v['lr_auc_sd'])}", f"{f3(v['rf_auc'])} ± {f3(v['rf_auc_sd'])}"])
for d in R["b4"]:
    if (d["rating_cut"], d["inactive_months_min"]) == (1500, 3.0): continue
    trows.append([f"Peak < {d['rating_cut']}, inactive ≥ {int(d['inactive_months_min'])} months", f"{d['active'] + d['attrition']:,}",
                  f"{f3(d['lr_auc'])} ± {f3(d['lr_auc_sd'])}", f"{f3(d['rf_auc'])} ± {f3(d['rf_auc_sd'])}"])
trows.append([f"Matched on account age and contests ({B5['n_matchings']} matchings), mean [range]", f"{2 * coh['attrition']:,}", f"{f3(B5['lr_auc_mean'])} [{f3(B5['lr_auc_min'])}, {f3(B5['lr_auc_max'])}]", f"{f3(B5['rf_auc_mean'])} [{f3(B5['rf_auc_min'])}, {f3(B5['rf_auc_max'])}]"])
for k, w in (("6", W6), ("12", W12)):
    trows.append([f"Before inactivity: {k}-month window ending 3 months before the last submission", f"{w['n_active'] + w['n_attrition']:,}",
                  f"{f3(w['models']['LR']['auc'])} {ci(w['models']['LR']['auc_ci95'])}", f"{f3(w['models']['RF']['auc'])} {ci(w['models']['RF']['auc_ci95'])}"])
TAB("TABLE IV. ROC-AUC under alternative analysis choices", ["Analysis", "Accounts", "Logistic regression", "Random forest"], trows, [4200, 1100, 2300, 2300],
    note="± values are standard deviations over cross-validation folds; brackets give 95% bootstrap confidence intervals unless stated. Rows with a rating limit or inactivity threshold change only that element of the primary definition (peak < 1500, inactive ≥ 3 months). The two last rows use only accounts with at least five rated contests in the window.")
F("fig3_robustness", "Fig. 3. ROC-AUC of logistic regression (circles) and random forest (squares) under the analyses of Table IV, with 95% confidence intervals (primary), 2.5–97.5% ranges (balanced samples), ranges over matchings, or ± one fold standard deviation. The dashed line marks chance.")
H2("Contribution of Individual Measures")
ab = B6
P(f"Removing the Editorial Dependency Index changes the ROC-AUC by {ab['without EDI']['LR']['delta_vs_all']:+.3f} for logistic regression and {ab['without EDI']['RF']['delta_vs_all']:+.3f} for the random forest, so it adds nothing measurable. "
  f"Removing problems solved per contest lowers the values by {abs(ab['without solved_per_contest']['LR']['delta_vs_all']):.3f} and {abs(ab['without solved_per_contest']['RF']['delta_vs_all']):.3f} (Fig. 4(b)). "
  f"Problems solved per contest also has the largest permutation importance in the random forest (mean drop {f3(imp[top]['mean'])}; 2.5th–97.5th percentile over folds {f3(imp[top]['p2_5'])}–{f3(imp[top]['p97_5'])}) and ranks first in {100 * imp[top]['share_of_folds_ranked_first']:.0f}% of folds (Fig. 4(a)). "
  "Several measures are strongly correlated (for example, the overall and mathematics-tagged acceptance rates), and permutation importance can misattribute importance among correlated measures [@strobl], so the ranking below the first measure is not reliable.")
F("fig4_importance_ablation", "Fig. 4. (a) Permutation importance in the random forest on every held-out fold (mean and 2.5–97.5% range). (b) Change in ROC-AUC when the constructed measures are removed, over paired cross-validation folds.")
H2("Activity Before Inactivity")
P(f"In the window of 6 months, {W6['n_active']:,} active and {W6['n_attrition']} attrition accounts had at least five rated contests and one accepted submission; "
  f"the ROC-AUC was {f3(W6['models']['LR']['auc'])} {ci(W6['models']['LR']['auc_ci95'])} for logistic regression and {f3(W6['models']['RF']['auc'])} {ci(W6['models']['RF']['auc_ci95'])} for the random forest. "
  f"In the window of 12 months ({W12['n_active']:,} and {W12['n_attrition']} accounts) it was {f3(W12['models']['LR']['auc'])} {ci(W12['models']['LR']['auc_ci95'])} and {f3(W12['models']['RF']['auc'])} {ci(W12['models']['RF']['auc_ci95'])} (Table IV). "
  + (f"These values are similar to, or slightly higher than, those of the whole-history analysis ({f3(LR['auc_oof'])} and {f3(RF['auc_oof'])}), so a small difference is already present in the months before users become inactive. "
     if b1_signal else
     "The confidence intervals include 0.5, so no reliable difference is present in the months before users become inactive, and the paper makes no claim that inactivity can be predicted. ")
  + b1_effect_sentence() + " "
  + f"Because only {100 * W6['n_attrition'] / coh['attrition']:.0f}% (6 months) and {100 * W12['n_attrition'] / coh['attrition']:.0f}% (12 months) of attrition accounts had five rated contests in the window, this analysis describes users who were still competing regularly in the months before they stopped.")

# ------------------------------------------------------------------ V Discussion
H1("V. Discussion")
H2("What the Results Show")
P("Users who became inactive differ from active users of similar peak rating in a few measurable ways: they accepted slightly smaller shares of their attempts and solved fewer problems per rated contest. "
  "These differences are small, persist across sampling, cleaning rules and definitions of inactivity, and shrink when tenure is controlled. "
  + ("When the measures are restricted to the months before inactivity, the groups still differ about as much, so part of the difference precedes inactivity; problems solved per contest remains the clearest signal. "
   if b1_signal else "When the measures are restricted to the months before inactivity, no reliable difference remains, so the whole-history difference may partly reflect the period in which users were already disengaging. ")
  + "The difference is small: it does not show why users stop, and it cannot identify individual users at risk.")
H2("Limitations")
P("The label is inactivity at one date. Some accounts labeled attrition may have resumed after T_{obs}, and longer inactivity thresholds reduce but do not remove this error. "
  f"A re-query of the public Codeforces API on 17 November 2026, about five months after T_{{obs}}, found that {B4R['submitted_again_after_T_obs']} of the {B4R['attrition_accounts']} accounts labeled attrition ({100 * B4R['share_submitted_again']:.1f}%) had submitted again; none had been deleted. "
  "The label therefore marks a pause of at least three months at T_{obs}, not a permanent departure.")
P(f"The retrieved histories of {len(flag)} accounts were incomplete, all of them active. They were excluded, but the cause is not yet established, and the remaining imbalance in submissions per contest suggests that some incomplete active histories may remain. "
  "The rule for excluding them was chosen after inspecting the data; Table IV shows how stricter rules change the results.")
P("The data come from one platform and from a worldwide population of users, not only students, so the results do not describe any particular group of learners. "
  "The observation time T_{obs} was not recorded by the collection code and is reconstructed from the data (Section III). "
  "The analysis of activity before inactivity uses histories retrieved again in November 2026 and includes only accounts with enough rated contests in the window. "
  "The two groups differ in tenure, and matching on tenure reduces the signal. Finally, the analysis reports several variants of the same models; although the two models were fixed in advance, the variants are not independent tests and should be read as a sensitivity analysis.")

# ------------------------------------------------------------------ VI Conclusion
H1("VI. Conclusion")
P(f"In a rating-restricted cohort of {coh['n']:,} Codeforces accounts, users who became inactive accepted slightly smaller shares of their attempts and solved fewer problems per contest than active users of similar skill. "
  f"Models built on eight window-invariant measures separate the groups only weakly (ROC-AUC {lo_auc:.2f}–{hi_auc:.2f} across analyses) and give poorly informative probabilities. "
  + ("A difference of similar size is already present in the months before inactivity. " if b1_signal else "No reliable difference is present in the months before inactivity. ")
  + "Platform logs alone therefore offer a modest description of disengagement, not a means of predicting it for individuals. The archived data and code allow every result to be checked and extended.")

# ------------------------------------------------------------------ Appendix, statements
H1("Appendix A: Feature Definitions")
P("Table V lists every measure, its definition as implemented in the collection code, and its use in this paper.", noindent=True)
TAB("TABLE V. Behavioral measures as implemented",
    ["Measure", "Definition", "Source", "Use"],
    [["Problems solved per contest", "Distinct problems solved / rated contests entered, (1)", "API submissions, contests", "model"],
     ["Math-tag acceptance rate", "Accepted / all submissions on problems tagged math, number theory, combinatorics or probabilities (overall rate if none)", "API submissions", "model"],
     ["Data-structure acceptance rate", "Accepted / all submissions on problems tagged data structures, trees, graphs or dsu (overall rate if none)", "API submissions", "model"],
     ["Overall acceptance rate", "Accepted submissions / all submissions", "API submissions", "model"],
     ["Struggle time", "Mean minutes from first attempt to first acceptance, over solved problems", "API submissions", "model"],
     ["Upsolves per contest", "Accepted practice-mode submissions on problems of contests the user was rated in / rated contests", "API submissions", "model"],
     ["Post-drop recovery", "Mean rating change in the contest after a rating drop, in rating points (0 if no drop)", "API rating history", "model"],
     ["Editorial dependency index", "Upsolves per contest × struggle time, (2)", "constructed", "model"],
     ["Rated contests per month", "Rated contests / months from first to last submission (at least 1)", "API contests", "descriptive"],
     ["Problems solved per month", "Distinct problems solved / months from first to last submission (at least 1)", "API submissions", "descriptive"],
     ["Account age", "Months from registration to T_{obs}", "API profile", "descriptive"],
     ["Rated contests (total)", "Number of rated contests entered", "API rating history", "descriptive"],
     ["Submissions per contest", "Retrieved submissions / rated contests", "API submissions", "data quality"]],
    [2400, 4300, 1900, 1200], note="A month is 30 days throughout. Inactivity: (T_{obs} − last submission) / 30 days ≥ 3, applied to the unrounded value.")
H1("Data and Code Availability")
P("The pseudonymized Codeforces feature file from which the analysis cohort is derived, all analysis code and a script that regenerates every number, table and figure of this paper (reproduce_all.sh) are archived on Zenodo:", noindent=True)
URL(f"https://doi.org/{CONCEPT_DOI}")
P("and developed in the public repository", noindent=True)
URL(REPO)
P(f"The raw API responses contain Codeforces handles, which identify users; they, the histories retrieved again in November 2026 for the analysis of activity before inactivity, and the salt used to pseudonymize handles are not public, "
  "and are available to the editor and reviewers on request for verification.", noindent=True)
H1("Acknowledgment")
P("An earlier version of this work was presented orally at EFAST 2026. "
  "We are grateful to the anonymous reviewers and the AJSE Editorial Desk for their detailed scrutiny.")
H1("Author Contributions")
P("Azuad Islam Ruhan led the study: he collected the Codeforces data, built the processing and analysis pipelines, ran the analyses, wrote the manuscript and handled the correspondence with the journal.")
P("Golam Mostofa Naeem supervised the work, helped shape the research question and the methodology, and reviewed and revised the manuscript.")
P("Rakibul Islam Rafi carried out the literature review for the Related Work section and critically revised the manuscript.")
P("Sherin Afrin Mim worked with R. I. Rafi on the literature review for the Related Work section and critically revised the manuscript.")
P("Nazira Bani Opi worked with R. I. Rafi on the literature review for the Related Work section and critically revised the manuscript.")
P("Dewan Fahad Chowdhury worked with M. R. K. Sadi on the Python scripts for collecting and processing the Codeforces data and critically revised the manuscript.")
P("Md. Rejaul Korim Sadi contributed to the design of the study and the data modeling, maintained the data-collection code, led the processing and analysis of the Codeforces logs, and revised the manuscript.")
P("All seven authors meet the ICMJE authorship criteria, approved the final manuscript and take responsibility for its content.")
H1("Use of AI Tools")
P("ChatGPT (OpenAI) was used for language editing, to refine the research topic and the initial proposal, and to help draft parts of the original data-collection and analysis code, which the authors reviewed and ran. "
  "In preparing the first submission, ChatGPT also suggested references for the Related Work section; three of them did not exist and were not checked by the authors. Every reference in this version has been checked against Crossref or DataCite. Grammarly was used for language editing. "
  "During the revision, Claude Opus 5.5 (Anthropic) was used to write and debug the re-analysis code, the figure and manuscript-generation scripts and the verification tests, to check every reference against Crossref, and to draft revised text; OpenAI tools were also used to organize the LaTeX source and to debug code. "
  "The authors ran every script, checked the reported numbers against the outputs, and take full responsibility for the content of this paper.")

# ------------------------------------------------------------------ references by first citation
order = []
def cite_keys(t):
    for k in re.findall(r"\[@(\w+)\]", t):
        if k not in order: order.append(k)
for b in blocks:
    for fld in ("text", "cap", "note"): cite_keys(b.get(fld) or "")
unknown = [k for k in order if k not in REFS]; assert not unknown, unknown
num = {k: i + 1 for i, k in enumerate(order)}
for b in blocks:
    for fld in ("text", "cap", "note"):
        if b.get(fld): b[fld] = re.sub(r"\[@(\w+)\]", lambda m: f"[{num[m.group(1)]}]", b[fld])
refs = [REFS[k][0] + (f", doi: {REFS[k][1]}." if REFS[k][1] else ".") for k in order]
unused = [k for k in REFS if k not in num]
BIO = json.load(open(MB / "inputs" / "pub_tables.json"))
bios = [BIO[i][0][0] for i in range(5, 12)]          # all seven authors, in the published order
photos = [str(MB / "inputs" / "author_photos" / p) for p in ["image16.jpg", "image17.jpg", "image18.jpg", "image19.png", "image19.png", "image20.jpg", "image21.jpg"]]
AFF = json.load(open(MB / "output" / "content_pub.json"))["meta"]["affil"]
meta["affil"] = AFF                                  # all seven authors
(V3 / "output").mkdir(exist_ok=True)
json.dump({"meta": meta, "blocks": blocks, "refs": refs, "ref_keys": order, "bios": bios, "photos": photos},
          open(V3 / "output" / "content_v3.json", "w"), ensure_ascii=False, indent=1)
words = len(meta["abstract"].split())
print(f"content_v3.json: {len(blocks)} blocks, {len(refs)} references (unused in database: {unused}), abstract {words} words, "
      f"placeholders {sum(len(re.findall('⟦', b.get('text') or '')) for b in blocks)}")
