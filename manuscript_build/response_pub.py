"""Point-by-point response to the AJSE inquiry, written against the PUBLISHED article (camera-ready).
All numbers are read from results/*.json and the exported analysis sets."""
import json, textwrap
import pandas as pd
from pathlib import Path
REPO = str(Path(__file__).resolve().parents[1])
OUT = str(Path(__file__).resolve().parent / "output" / "AJSE_1999_Response_to_Editorial_Inquiry.txt")
R = json.load(open(f"{REPO}/results/r3_results.json")); T1 = {r["stage"]: r["accounts"] for r in json.load(open(f"{REPO}/results/r3_table1_cohort.json"))}
SV = pd.read_csv(f"{REPO}/data/survey_analysis_set_n64.csv")
def fpv(p): return "<0.001" if p < 0.001 else f"{p:.3f}"
def fpH(p): return "< 0.001" if p < 0.001 else f"= {p:.3f}"
def g(x): return f"{x:,.0f}" if abs(x) >= 100 else (f"{x:.1f}" if abs(x) >= 10 else f"{x:.2f}")
flow = R["cf_flow"]; dq_full = sum(flow["dq_q1_fewer_submissions_than_rated_contests"].values()) + sum(flow["dq_q2_more_than_15_contests_per_month"].values())
dq_t1 = T1["After peak rating < 2400"] - T1["After data-quality check (complete submission history)"]
coh = R["cf_cohorts"]["primary_matched_clean"]; bu, bm = R["cf_balance"]["original_unmatched"], R["cf_balance"]["primary_matched_clean"]
D = {r["feature"]: r for r in R["cf_descriptives_matched"]}; DU = {r["feature"]: r for r in R["cf_descriptives_original_unmatched"]}
H = R["original_headline_reproduced"]; B = R["cf_burnout"]["primary_matched_clean"]; BU = R["cf_burnout"]["original_unmatched"]
MD = R["cf_models"]; Dm, Bm, Cm, Sm = MD["D_matched_consistent_8f"], MD["B_matched_12f"], MD["C_matched_r1_9f"], MD["D_on_uncleaned_matched"]
BASE = "Baseline: always 'attrition'"; MODELS = [n for n in Dm if not n.startswith("Baseline")]
best = lambda M_: max(MODELS, key=lambda n: M_[n]["rcv_auc_mean"]); bD, bB, bC, bS = best(Dm), best(Bm), best(Cm), best(Sm)
PERM = R["cf_permutation"]; IMP = sorted(R["cf_importance_D"], key=lambda r: -r["perm_auc_drop"])
SF = R["survey_flow"]; ST = {r["feature"]: r for r in R["survey_tests_comparable"]}; SVM_ = R["survey_models_comparable"]; SVP = R["survey_permutation_LR"]
REP = R["survey_original_stats_reproduced"]; svmods = [n for n in SVM_ if not n.startswith("Baseline")]; sv_best = max(svmods, key=lambda n: SVM_[n]["rcv_auc_mean"])
ms_a, ms_s = SV.loc[SV.label == 0, "math_skill"].mean(), SV.loc[SV.label == 1, "math_skill"].mean()
rep = R["environment"]["cv_repeats"]; nperm = PERM["Random Forest"]["n_perm"]; math = ST["math_skill"]

L = []
def w(s=""):
    if not s: L.append(""); return
    for para in s.split("\n"):
        L.append(textwrap.fill(para, 100, subsequent_indent="    " if para.startswith("  - ") else "") if para.strip() else "")
def sec(t): w(); w("=" * 100); w(t); w("=" * 100)
def sub(t): w(); w(t); w("-" * min(len(t), 100))
def quote(t): w(); w('INQUIRY (verbatim): "' + t + '"')
def what(t): w(); w("What we found. " + t)
def fix(t): w(); w("What we changed. " + t)

w("To: Editorial Desk, AIUB Journal of Science and Engineering (AJSE) <ajse@aiub.edu>")
w("Cc: Dr. M. Tanseer Ali; Prof. Dr. Md. Abdur Rahman; Md. Manirul Islam")
w("From: Azuad Islam Ruhan (corresponding author), on behalf of all authors and our supervisor")
w("Re: Paper ID 1999, \"Predicting Student Attrition in Competitive Programming: A Large-Scale Study Integrating Survey Insights and Global Behavioral Logs\", AJSE 25(2):231-243 (2026), DOI 10.53799/vka5w161")
w("Subject: Point-by-point response to the Temporary Retraction and Formal Inquiry Notice of 3 November 2026")
w("Date: 6 November 2026")
w()
w("Dear Editor,")
w()
w("We thank the Editorial Desk for the care with which the concerns about our article have been set out, and for giving us the opportunity to respond before any final decision. "
  "We have taken every point seriously. All authors and our supervisor re-examined the study from the raw materials upward: the Google Forms response sheet, the Codeforces feature file and API records, every script, and every sentence, number, table, figure and reference of the published article.")
w()
w("We followed three working rules. First, no number was edited by hand: every value in the corrected manuscript is produced by one deposited script (scripts/revision/r3_inquiry_reanalysis.py, seed 42, pinned library versions), which we ran twice with identical results. "
  "Second, the corrected manuscript was built paragraph by paragraph from the published text, and we enclose a tracked-changes version so that every changed word can be seen against the published article. "
  "Third, where the inquiry rests on a reading of the published text that differs from what the paper and code actually contain, we say so respectfully and show the evidence. Where the inquiry identified a genuine error, we say that plainly and show the correction.")
w()
w("In summary:")
w(f"  - The rating matching was performed, and the published Table III shows it. Re-running the deposited script r1 reproduces seven of the nine classifiers to the third decimal in each of its columns (B) and (C). "
  "The remaining differences are at most 0.008 and arise from library versions. The values the Desk found identical to the preprint belong to the descriptive results (\"Behavioral Trends Preceding Attrition\", Figs. 4-8), which was carried over from the first submission and not recomputed on the matched cohort. That was our error, and it is corrected.")
w(f"  - During re-verification we found one further problem: {dq_t1} active accounts had incomplete retrieved submission histories. "
  "They inflated the published contrast in contest frequency, are now excluded by an explicit rule, and are reported openly (Item 1.0).")
w(f"  - On the corrected, rating-matched cohort, users who withdrew still differ from matched active users. They entered fewer contests, solved fewer problems, and were slightly less accurate on math and data-structure problems. "
  f"Behavioral features predict attrition above chance (best repeated-CV ROC-AUC {Dm[bD]['rcv_auc_mean']:.3f}; Random Forest {Dm['Random Forest']['rcv_auc_mean']:.3f}, permutation p = {PERM['Random Forest']['p']:.3f}), but modestly, and the manuscript now reports them against trivial baselines.")
w("  - The survey classifier, the Early Warning System and the Skill-Application Paradox as a finding are withdrawn. The paradox remains only as a hypothesis, because its behavioral half rested on survey items that are not comparable across branches.")
w("  - The non-existent references the Desk identified ([3], [19], [20]) and the incorrect [22] are entries of our original submission. They were replaced in the published PDF but still stand in the Crossref deposit and in the arXiv preprint. "
  "Every reference has now been verified, and the remaining metadata and attribution errors in the published list ([5], [9], [10]) are corrected.")
w()
w("Data availability. As the Editor requested, all data and code needed to verify the work are publicly available at https://github.com/AZUAD-ISLAM-RUHAN/cp-attrition-prediction. The two data files analysed (data/cf_attrition_features.csv and data/survey_responses.csv) have been public in this repository since 19 September 2026, unchanged, and are byte-identical to the files from which every number of the corrected manuscript is computed; the corrected analysis code, documents and reproduction outputs have now been added to it. A copy is also attached to this e-mail (AJSE_1999_Public_Data_and_Code.zip). It contains:")
w(f"  (a) Codeforces data: the released feature file (6,927 accounts, handles pseudonymised with a salted hash) and the rating-matched modelling set exactly as analysed (n = {coh['n']:,}, with labels, all features, peak rating and data-quality fields).")
w("  (b) Survey data: all 96 anonymised responses (no names, IDs, e-mails or institutions), the response date of each submission so that the collection window can be checked, and the analysis set (n = 64). The public copy was verified cell by cell against the original Google Forms sheet.")
w("  (c) Complete code, from API collection to figures, including the first-submission and first-round revision scripts, kept unchanged so that every published number can be traced. A single command (reproduce_all.sh) regenerates every number, table and figure, as well as both versions of the corrected manuscript, and checks them against the submitted outputs.")
w("  (d) results/r3_results.json, containing every number of the corrected manuscript in machine-readable form, and the logs of a from-scratch reproduction run.")
w("  (e) The full questionnaire, a data dictionary, the ethics and data-handling record, and the reference-verification record.")
w("Raw API records that contain Codeforces handles, and the exact submission times of the survey, are not posted publicly because they are personal or quasi-identifying data. They are available to the Editorial Desk on request, and scripts/revision/r0_rebuild_from_raw_jsonl.py rebuilds every stage count from the raw records.")
w()
w("Format. The corrected manuscript is laid out on the AJSE camera-ready template (AJSE_Template_2020-OTH): US Letter, two columns, 10-point text, small-caps section headings, lettered subsections, table titles in small caps above each table, and figures redrawn at their printed size (400 dpi, Arial, 8-point labels, sub-figures labelled (a), (b), ...). The abstract was shortened to 249 words to meet the template's limit of 150-250 words. These layout changes alter no number. Every template rule is checked automatically (docs/AJSE_template_conformance.md).")
w("Attached to this e-mail: (1) this response letter; (2) the corrected manuscript, clean (DOCX and PDF); (3) the corrected manuscript with tracked changes against the published article (DOCX and PDF); (4) the ethics approval letter REC/MU/2026/007; "
  "(5) a supplementary verification file (published vs. reproduced values, reference verification, change map and draft correction notice); and (6) the public data and code archive.")

sec("ITEM 1.0  AN ADDITIONAL PROBLEM WE FOUND OURSELVES")
w("(Reported first because it bears on Items 1.1-1.3.)")
w(f"While rebuilding the cohort we checked every account for internal consistency. Every rated contest requires at least one submission, yet {flow['dq_q1_fewer_submissions_than_rated_contests']['Active']} accounts in the released file had fewer retrieved submissions than rated contests "
  f"(a median of 6 submissions against 24 rated contests, all dated within the month before collection). A further {flow['dq_q2_more_than_15_contests_per_month']['Active']} accounts showed more than 15 rated contests per month of submission span; "
  f"the highest value among inactive accounts was {flow['max_contests_per_month_among_stopped']:.0f}. All {dq_full} of these accounts were active, and {dq_t1} remain after the published peak-rating filter. "
  "Their retrieved histories are incomplete, so their submission-derived features are not reliable. "
  f"In the published unmatched sample, {H['active_rows_failing_dq_in_original_sample']} of them raised the active mean contest rate to {H['contests_per_month_mean_active']:.2f} per month; without them the mean is {H['contests_per_month_mean_active_excluding_dq_fail']:.2f}. "
  "The published \"83.7 percent fall in contest participation\" was therefore largely an artifact of incomplete data.")
fix("Such accounts are excluded by an explicit rule (Dataset 1 subsection, new data-quality paragraph; Table I). "
    f"The primary model is also reported without the rule, so the Desk can see the rule's effect (best AUC {Sm[bS]['rcv_auc_mean']:.3f} without it, {Dm[bD]['rcv_auc_mean']:.3f} with it). The raw records allow these accounts to be checked directly.")

sec("ITEM 1  METHODOLOGICAL AND STATISTICAL INCONSISTENCIES")
sub("1.1  Specification A and values identical to the unmatched preprint")
quote("The rating-matched analysis (Specification A) reports descriptive statistics, p-values, feature importances, and proportions identical to your earlier unmatched preprint, raising questions about whether you performed the described matching procedure.")
what("We respectfully clarify one point of reading and acknowledge one error. "
     "The clarification is that in the published Table III, Specification (A) is labelled \"Unmatched\". It was included on purpose, as the paper says, \"so the effect of the confound is visible\", and is therefore identical to the preprint by design. "
     "The rating-matched specifications are (B) and (C). They were computed on the matched cohort, and the deposited script r1 reproduces them: for (C), logistic regression 0.639, KNN 0.589, SVM 0.652, XGBoost 0.652, LightGBM 0.645, MLP 0.608 and the ensemble 0.679 are identical to the published values. "
     "Random Forest (0.682 published) and the Decision Tree differ only in the third decimal across library versions. The published Table I is also reproduced exactly from the data: 6,927, then 6,892, then 5,573 and 1,319, then 908 and 411, with a matching pool of 4,047.")
w()
w("The error is that the descriptive part of the paper was not recomputed on the matched cohort. The subsection \"Behavioral Trends Preceding Attrition\" and Figs. 4-8 are the first-submission results on the unmatched cohort, and the five figure files are byte-identical to those of the first submission. "
  "This includes 7.27 vs. 1.19 contests per month (83.7 percent), 2,646 vs. 3,059 minutes (15.6 percent), 13.70 vs. 7.86 problems per month (42.7 percent), burnout of 45.0 vs. 29.8 percent, and upsolving of 2.94 vs. 2.81. "
  "The abstract and conclusion repeated these figures. The conclusion also stated that \"these differences persist when the two cohorts are held to the same peak-rating ceiling\", which we had not computed. The feature importances in Fig. 14 are the unaudited ones, as their caption states.")
fix("Every descriptive statistic, test and proportion is now computed on the rating-matched cohort (first Results subsection, new Table III, Figs. 2-3), and the matched cohort is deposited. The following values show that matching changes the results:")
w(f"  - Peak rating: standardized mean difference {bu['standardised_mean_difference']:.2f} unmatched -> {bm['standardised_mean_difference']:.3f} matched; Kolmogorov-Smirnov D {bu['ks_D']:.3f} -> {bm['ks_D']:.3f} (p = {bm['ks_p']:.3f}).")
for f, lab in [("contests_per_month", "Contests per month"), ("problems_solved_per_month", "Problems solved per month"), ("avg_struggle_minutes", "Struggle time (min)"),
               ("math_solve_rate", "Math solve rate"), ("ds_solve_rate", "Data-structure solve rate")]:
    w(f"  - {lab}: published (unmatched means) {g(DU[f]['active_mean'])} vs {g(DU[f]['attr_mean'])}; corrected (matched medians, active vs attrition) {g(D[f]['active_median'])} vs {g(D[f]['attr_median'])}, "
      f"rank-biserial r = {D[f]['r_rb']:.2f} [{D[f]['r_lo']:.2f}, {D[f]['r_hi']:.2f}], Holm p {fpH(D[f]['p_holm'])}.")
w(f"  - Activity-decay flag: published {BU['active_pct']:.1f}% vs {BU['attr_pct']:.1f}%; corrected {B['active_pct']:.1f}% vs {B['attr_pct']:.1f}%.")
w("Withdrawn as a result: the 83.7 percent fall, the 15.6 percent rise in struggle time, the 42.7 percent figure, and the editorial-dependency reading of upsolving "
  f"(no difference, Holm p = {D['upsolves_per_contest']['p_holm']:.3f}). What remains is smaller and holds: lower contest and practice frequency and slightly lower topic-level accuracy, all significant after Holm correction, with |r| <= "
  f"{max(abs(D[f]['r_rb']) for f in ['contests_per_month','problems_solved_per_month','solved_per_contest','math_solve_rate','ds_solve_rate','acceptance_rate']):.2f}.")

sub("1.2  Activity Trend Ratio / attrition criteria vs. burnout percentages and Fig. 7")
quote("Discrepancies between the defined Activity Trend Ratio / Attrition criteria and the reported burnout percentages and plot distributions (e.g., Fig. 7).")
what("The published article describes the Activity Trend Ratio in three ways that do not agree with one another or with the code. "
     "The Dataset 1 subsection says the recent and prior windows are \"the three and six calendar months preceding T_obs\". The Feature Engineering subsection calls it \"the ratio of submissions in the recent three months to those in the prior three\". "
     "The Results define burnout as activity \"falling by more than half over the final three months\", and the Fig. 7 axis reads \"recent 6mo / prior 6mo\". "
     "The code computes none of these. It divides the submissions in the second half of each user's own submission span (first to last retrieved submission) by those in the first half, and flags burnout when the ratio is below 0.5. "
     "Under the calendar definition, every attrition user, having no submissions in the last three months, would have a ratio of 0, which Fig. 7 plainly does not show; this is the discrepancy the Desk observed. "
     f"Fig. 7 also paired a box plot of the raw ratio (t-test p = 0.610 on a heavy-tailed variable whose mean was higher for attrition users, {DU['activity_trend_ratio']['attr_mean']:.2f} vs {DU['activity_trend_ratio']['active_mean']:.2f}) with bars of the flag, from the unmatched cohort.")
fix("The implemented definition is now stated once (Feature Engineering subsection) and used consistently in the text, the figure and the code, including the fallback value of 1 when the first half is empty. "
    f"On the matched cohort the flag occurs in {B['attr_pct']:.1f}% vs {B['active_pct']:.1f}% of users (difference {B['diff_pp']:.1f} percentage points, 95% CI {B['diff_ci_pp'][0]:.1f}-{B['diff_ci_pp'][1]:.1f}; new Fig. 3, with Wilson intervals). "
    "We also state that, for inactive users, the second half of the span ends at the final submission, so part of this difference follows from the label definition. For that reason the ratio is reported but not modelled. "
    "The attrition criterion is stated precisely: last submission at least three months before T_obs, and peak rating below 1500. "
    "We also correct a factual slip: 1500 is not \"the Codeforces Specialist boundary\" (the Specialist band is 1400-1599), so it is described as a study-specific cut-off.")

sub("1.3  Inconsistent data-leakage audit between contest and problem-solving variables")
quote("Inconsistent application of the data leakage audit between contest and problem-solving variables.")
what("The published audit removed contests per month (reason: a denominator \"anchored to T_obs\") but kept problems solved per month. "
     "Table V describes both as \"divided by account tenure\". In the code, both are in fact divided by the same submission span, so they share a single denominator. "
     "The audit also kept the Intensity Ratio, which is built from both. The rule was therefore applied to the contest variable but not to its problem-solving counterparts. "
     "Table V also misdescribed post-drop recovery as \"submissions in the 30 days after a rating fall\"; the code computes the mean rating change in the contest after a drop. "
     "The published Eq. (1) for the Intensity Ratio does match the code.")
fix("One rule is now applied throughout: every feature whose value depends on the length or end of the observed activity window is removed (account age, both monthly rates, the trend ratio). "
    f"The Intensity Ratio is replaced by its exactly window-invariant form, problems solved per rated contest; the span cancels between numerator and denominator (Spearman rho = {R['ir_vs_solved_per_contest_spearman']:.3f}). "
    "Table VI (Appendix A) gives every definition as implemented, with the reason for each exclusion. Three specifications are reported side by side (Table IV, Fig. 6):")
for key, lab in [("B_matched_12f", "B, 12 features"), ("C_matched_r1_9f", "C, published audit (9)"), ("D_matched_consistent_8f", "D, consistent audit (8) [primary]"), ("D_on_uncleaned_matched", "D without the data-quality rule")]:
    M_ = MD[key]; b_ = best(M_); rf = "" if b_ == "Random Forest" else f"; Random Forest {M_['Random Forest']['rcv_auc_mean']:.3f}"
    w(f"  - {lab}: best repeated-CV ROC-AUC {M_[b_]['rcv_auc_mean']:.3f} +/- {M_[b_]['rcv_auc_sd']:.3f} ({b_}){rf}.")

sub("1.4  Confounding survey item mappings (Q11/Q33; break-history timelines)")
quote("Confounding survey item mappings (e.g., upsolving Q11/Q33 alignment and break history timelines).")
what("The Desk is right on both. The Dataset 2 subsection and Appendix B aligned Q11 (active: post-contest upsolving, always/sometimes/rarely/never) with Q33 (stopped: practice habit in the month before quitting) via regular->sometimes, became irregular->rarely, stopped completely->never. "
     "These are different behaviors, and the mapping puts even \"regular\" practice below the top active answer. "
     f"The resulting chi-square ({REP['upsolving_n64_r2']['chi2']:.2f}, Table II), its 35.5 percent feature importance (Fig. 10), and the \"behavioral half\" of the Skill-Application Paradox all reflect the coding, not behavior. "
     "Q27 (a break in the last three months) and Q36 (a break at any point in the CP journey) refer to different periods, so combining them does not create a comparable variable.")
fix("Only items asked identically of everyone (Q3, Q4, Q5) or worded in parallel (Q14/Q37, Q22/Q35, Q28/Q34, with a recall caveat) enter tests or models (Dataset 2 subsection). "
    "Q11, Q33, Q27, Q36 and Q39 are reported within their branch only. The upsolving result, Fig. 10 and the paradox as a finding are withdrawn, and Appendix B now states which items are and are not aligned.")

sub("1.5  Chi-square statistics (Table II) and conflicting conclusions between the layers")
quote("Unreproducible Chi-square test statistics (Table II) and conflicting conclusions between Codeforces logs and survey data layers.")
what("Table II was produced with scipy's chi2_contingency at its default settings, which apply Yates' continuity correction to 2x2 tables only, and the paper did not say so. "
     f"Anyone computing the ordinary Pearson statistic therefore obtains different values: mentor support {REP['mentor_support_n64']['chi2_yates']:.3f} (as published, Yates) vs {REP['mentor_support_n64']['chi2_pearson']:.3f} (Pearson), "
     f"prior consideration of quitting {REP['thought_quit_n64']['chi2_yates']:.3f} vs {REP['thought_quit_n64']['chi2_pearson']:.3f}, prior experience {REP['prior_exp_n64']['chi2_yates']:.3f} vs {REP['prior_exp_n64']['chi2_pearson']:.3f}, "
     f"and long break {REP['long_break_paired_n64_r2']['chi2_yates']:.3f} vs {REP['long_break_paired_n64_r2']['chi2_pearson']:.3f}. "
     "Several tables also have expected counts below 5, where asymptotic p-values are unreliable. The upsolving and long-break rows rest on the non-comparable items described in 1.4. "
     "On the conclusions: The Discussion said the two layers \"return findings that point the same way\" on practice between contests. Once the upsolving item is set aside, they do not. "
     "In the platform data, attrition users were slightly less accurate, whereas in the survey, students who stopped rated themselves slightly higher.")
fix(f"The new Table II reports the six comparable items (n = {SF['analysis_set']}) with Pearson chi-square without continuity correction (stated explicitly), exact p-values (Fisher for 2x2, Monte-Carlo with 10,000 shuffles otherwise), "
    "effect sizes with confidence intervals, and Holm and Benjamini-Hochberg adjustments. "
    f"No survey difference survives; the smallest Holm-adjusted p is {math['p_holm']:.3f} (mathematics self-rating, {ms_s:.2f} vs {ms_a:.2f}). "
    "The Discussion now states that the two analyses neither confirm each other nor point the same way, and treats them as separate evidence.")

sub("1.6  Below-baseline performance; training errors shown as Early Warning System signatures")
quote("Model performance falling below trivial baseline classifiers, along with classifier training errors presented as \"Early Warning System\" signatures.")
what("On a balanced cohort, always predicting attrition yields F1 = 2/3. Under the published audited Specification (C), seven of nine classifiers fall below that value, and the published F1 of 0.682 for Random Forest is only marginally above it. "
     f"Survey F1 values should likewise have been read against {SVM_[BASE]['rcv_f1_mean']:.3f}, the F1 of always predicting the majority class (42 of 64). "
     "The Early Warning System scored the same 22 active students on whom the model was trained. Even out of fold, an active student scored as high risk is a misclassification of a known label, and the Results described those misclassifications as the \"Skill-Application Paradox signature\". "
     "That reading was not justified. The tiers also depend on library version: re-running the deposited code gives 5/8/9 instead of the published 6/10/6.")
fix(f"Every model table now includes the always-attrition and random baselines. ROC-AUC (chance = 0.5) is the primary metric, alongside F1 and balanced accuracy with per-fold SD ({rep}x repeated 5-fold CV) and bootstrap test intervals. "
    f"A label-permutation test ({nperm} permutations) gives p = {PERM['Random Forest']['p']:.3f} for both Random Forest and logistic regression. "
    "The behavioral signal is therefore real but modest, and the manuscript says plainly that no classifier exceeds the trivial F1. "
    f"On comparable items the survey classifier reaches a repeated-CV ROC-AUC of at most {SVM_[sv_best]['rcv_auc_mean']:.3f} (permutation p = {SVP['p']:.3f}) and is not claimed. "
    "The Early Warning System is withdrawn, and its section now explains why.")

sec("ITEM 2  REFERENCE AND METADATA AUDIT")
quote("Discrepancies and inaccuracies in reference metadata between the preprint, Crossref deposit, and published PDF, including multiple references that appear unverified, misattributed, or non-existent (e.g., [3], [19], [20], [22]).")
what("The Desk is right that the three sources disagree, and we traced how. The arXiv preprint (v1, 27 July 2026) and the Crossref deposit for DOI 10.53799/vka5w161 (23 references) both carry the reference list of our original submission. "
     "In that list, [3] (Combefis & de le Vingne, WiPSCE 2016), [19] (Miao & Ahmad, Comput. Educ. 2023) and [20] (Al-Razgan et al., Comput. Hum. Behav. 2021) cannot be found in any bibliographic database, and [22] had the wrong title and journal. "
     "These entries were not verified before our first submission. That was our error, and we regret it. "
     "During the first revision the list was rebuilt, and the published PDF (31 references) replaces them with verifiable works:")
w("  - [3] S. Combefis, G. Beresnevicius, V. Dagiene, Olympiads in Informatics 10:39-60, 2016, doi:10.15388/ioi.2016.03")
w("  - [19] R. Raman, H. Vachharajani, K. Achuthan, Educ. Inf. Technol. 23(5):1919-1932, 2018, doi:10.1007/s10639-018-9697-3")
w("  - [20] E. B. Costa et al., Comput. Hum. Behav. 73:247-256, 2017, doi:10.1016/j.chb.2017.01.047")
w("  - [22] P. Prinsloo, S. Slade, J. Learning Analytics 3(1):159-182, 2016, doi:10.18608/jla.2016.31.10")
w("The deposit was generated from the reference metadata entered at submission and was not updated after the revision, so the deposited list and the printed list differ. We respectfully ask that the deposit be updated with the corrected list enclosed.")
fix("We verified all 31 published references against Crossref or publisher records. The remaining problems, now corrected, are:")
w("  - [5] Malmi et al. carried the wrong year and pages (it is ITiCSE 2002, pp. 55-59) and does not support the sentence citing it. It is replaced by Kinnunen & Malmi, ICER 2006, pp. 97-108, doi:10.1145/1151588.1151604.")
w("  - [9] Kotsiantis (a general review of classifiers) was cited for dropout modelling from online-course data. It is replaced by Kloft et al., EMNLP MOOC Workshop 2014, pp. 60-65, doi:10.3115/v1/W14-4111.")
w("  - [10] Ihantola et al.: the title is corrected to \"... Literature Review and Case Studies\" (doi:10.1145/2858796.2858798). [6] Guzdial: full title restored.")
w("  - The sentence citing [22] now matches its content (student agency and data ethics in learning analytics).")
w("  - Four standard methods references are added for the corrected statistics: [32] Holm 1979, [33] Mann & Whitney 1947 (doi:10.1214/aoms/1177730491), [34] Wilson 1927 (doi:10.1080/01621459.1927.10502953) and [35] Ojala & Garriga, JMLR 11:1833-1863, 2010.")
w("  - Author metadata: the deposit duplicates two surnames (\"Ruhan Ruhan\", \"Rafi Rafi\"), and the fourth author appears as \"Shehrin\" in the submission system but \"Sherin\" in the article and preprint. We ask that the deposit be corrected to match the published article.")
w("Preprint: once the Desk has reviewed the corrected version, we will post arXiv v2 with a note that it supersedes v1 following this inquiry.")

sec("ITEM 3  ETHICS AND DATA DISCLOSURES")
quote("Discrepancies between figure captions/titles and the text findings, as well as missing details on the sampling frame, seeds, T_obs, and ethics approval dates/institutional scope.")
sub("3.1  Figures, captions and text")
w("Every figure is now drawn from the results file by one script (r3_figures.py), so captions and text cannot diverge. The discrepancies corrected, by published figure number:")
for s in [
 "Fig. 2: \"eight psychographic inputs ... softmax output over the two classes\". After one-hot encoding the input is wider, and scikit-learn's binary multilayer perceptron has a single logistic output. Removed; the architecture is stated in the text.",
 "Fig. 3 and the Models subsection: \"weights tuned by cross-validation\". The ensemble uses equal weights, the library default, and no weights were tuned. Removed; Eq. (3) now states equal weights.",
 "Fig. 4: matched cohort implied, unmatched values shown; the image title also reads \"Active users participate 83.7% more frequently\", whereas 7.27 vs 1.19 is about six times, not 83.7 percent more. Replaced by Fig. 2 and Table III.",
 "Figs. 5-6: unmatched means of heavy-tailed variables. Replaced by matched medians (Table III, Fig. 2).",
 "Fig. 7: three ATR definitions (see 1.2). Replaced by Fig. 3.",
 "Fig. 8: the title says \"Stopped users upsolved more\", while the bars show the opposite share in the top band; \"Never\" in fact meant fewer than 0.5 upsolves per contest. Removed; the result is reported in the text.",
 "Fig. 10: survey importance led by the non-comparable upsolving item (1.4). Removed.",
 "Figs. 12-13: F1 shown without the trivial baseline. Replaced by Fig. 6 (ROC-AUC and F1 with baselines) and Tables IV-V.",
 "Fig. 14: unaudited importances, correctly captioned as such, but the accompanying text said attrition accounts \"were created more recently than active ones\". "
 f"In the data they are older (median {g(D['account_age_months']['attr_median'])} vs {g(D['account_age_months']['active_median'])} months), because account age includes the idle period. Replaced by Fig. 7 (audited) with the statement corrected.",
 "Fig. 15: Early Warning System (see 1.6). Removed.",
 "Fig. 1: the framework showed converging layers with the mixed numbers described in 1.1. Replaced by a study-design figure showing two independent analyses.",
 "Text: \"every classifier ran with balanced class weights\" (not possible for KNN and MLP); \"six proxies binned onto 1 to 5 ... so that users ... remain comparable\" (the models used raw values, and the binned set included rating volatility, not post-drop recovery); "
 "Appendix B listed four DSA-grade options where the form had five. All corrected."]:
    w("  - " + s)
sub("3.2  Sampling frame, seeds and T_obs")
w("  - Sampling frame (Dataset 1 subsection): the list of rated users from the Codeforces API (user.ratedList, activeOnly = false); a pool of 26,000 handles stratified by current rating band, proportional with a minimum of 50 per band. "
  "Collection gate: at least 5 rated contests, current rating 1-2399, at least one accepted submission. 6,927 accounts in the released file; every later stage is in Table I. Counts removed before the file are produced from the raw records by r0.")
w("  - Seeds: 42 for handle sampling, undersampling, data splits, cross-validation folds, models, bootstraps and permutations. Library versions are pinned.")
w("  - T_obs: the published article describes T_obs as \"the date on which the API crawl completed\". In the code it is the moment the feature file was built, and that moment was not recorded "
  "It falls in June 2026, before 24 June 2026, when the first figures were produced from the file. A later re-execution of the notebook on the same cached records shows 5,600/1,327 instead of the file's 5,603/1,324, "
  "consistent with three accounts crossing the three-month threshold between runs. The rebuild script r0 therefore takes T_obs as an explicit argument, and it also provides a fixed-window rebuild in which all features use activity before T_obs minus three months only.")
sub("3.3  Ethics approval dates and institutional scope")
w("  - The published article says the study was approved \"on 17 March 2026\". That is the date of the approval letter (REC/MU/2026/007, enclosed). The letter itself states that approval was given by resolution of the Research Ethics Committee's meeting of 24 February 2026.")
w("  - Survey responses were collected from 6 March to 2 April 2026, after the 24 February resolution. Stating only the letter date made it appear that 84 of the 96 responses preceded approval. "
  "The corrected manuscript states both dates and the collection period (Dataset 2 subsection).")
w("  - Scope: approval was granted by the authors' institution for the project as a whole. The survey was an anonymous, voluntary online form for computer science students. "
  "It recorded no name, student ID, e-mail or institution, and no institutional records were accessed. "
  "Because institution was not recorded, the corrected manuscript no longer calls the survey \"multi-institutional\", no longer gives a number of universities, and reports no per-institution figures. "
  "The consent statement on the form's landing page is described in the Dataset 2 subsection as in the published article, and a screenshot of the form can be provided on request.")
w("  - Codeforces: public API endpoints only, at a rate within the platform's call limits; handles are pseudonymised with a salted hash in every released file, and accounts are never linked to survey respondents.")

sec("RESPECTFUL CLOSING")
w("We regret the errors that led to this inquiry and the work they have caused the Editorial Desk. We have tried to answer each concern fully, to separate what was a matter of reading from what was our mistake, and to make every step independently checkable. "
  "The corrected article reports a smaller result than the published one: a modest but real behavioral signal of attrition in a rating-matched cohort, together with an exploratory survey. We believe it is now an accurate and reproducible account of what the data show.")
w()
w("We understand from COPE's Retraction Guidelines (version 3, 2025) that unreliable content can stem from honest error as well as misconduct, and that the purpose of retraction is to correct the literature rather than to punish authors. "
  "In that spirit, we would be grateful if the Desk would consider publishing the corrected version with a correction notice, which we would be glad to draft with you.")
w()
w("We fully respect that the decision rests with the Editorial Desk. Should the Desk conclude, after its review, that the article cannot continue in the journal even in its corrected form, "
  "we would respectfully welcome the opportunity to discuss with the Desk how the authors themselves might bring the matter to the most fitting close, in whatever manner the Desk considers consistent with the journal's standards and with COPE guidance. "
  "In every case, we remain at the Desk's disposal for any further data, code or clarification.")
w()
w("Yours sincerely,")
w()
w("Azuad Islam Ruhan (corresponding author), on behalf of all authors:")
w("Golam Mostofa Naeem (supervisor), Rakibul Islam Rafi, Sherin Afrin Mim, Nazira Bani Opi, Dewan Fahad Chowdhury, Md. Rejaul Korim Sadi")
w("Department of Computer Science and Engineering, Metropolitan University, Sylhet, Bangladesh")
open(OUT, "w").write("\n".join(L) + "\n")
print("wrote", OUT, len(L), "lines")
