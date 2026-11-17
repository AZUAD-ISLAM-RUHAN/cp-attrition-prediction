"""Reviewer requirement 8.6: a table of every number, figure and claim of the PUBLISHED article (AJSE 25(2):231-243),
marked Kept, Changed (with the new value) or Withdrawn, for the journal's public notice.
New values are read from results/r4_results.json. Writes manuscript_build/v3/output/claims_table_v3.md (and .json)."""
import json
from pathlib import Path
V3 = Path(__file__).resolve().parent; ROOT = V3.parents[1]
R = json.load(open(ROOT / "results" / "r4_results.json")); D = {d["feature"]: d for d in R["descriptives"]}
CV3 = json.load(open(V3 / "output" / "content_v3.json")); NREF = len(CV3["refs"]); NDOI = sum("doi:" in r for r in CV3["refs"])
c = R["cohort"]; LR, RF = R["models"]["LR"], R["models"]["RF"]; B4 = R["b4"]
f2, f3 = (lambda x: f"{x:.2f}"), (lambda x: f"{x:.3f}")
def med(f, k=2): return f"{D[f]['attr_median']:.{k}f} vs. {D[f]['active_median']:.{k}f} (attrition vs. active, medians)"
B1 = json.load(open(ROOT / "results" / "r5_b1_results.json"))["windows"]
B1TXT = "; ".join(f"{k.split('_')[0]}-month window ending 3 months before the last submission: ROC-AUC {f3(w['models']['LR']['auc'])} (logistic regression), {f3(w['models']['RF']['auc'])} (random forest)" for k, w in B1.items())
SV = "The survey is removed from the revised paper (reviewer Option 1)."
rows = [
 # (published location, published claim or number, status, new value / reason, where in revised paper)
 ("Title", "Predicting Student Attrition in Competitive Programming: A Large-Scale Study Integrating Survey Insights and Global Behavioral Logs", "Changed",
  "Behavioral Differences Between Active and Inactive Users in Competitive Programming: A Rating-Restricted Analysis of Codeforces Activity", "Title"),
 ("Abstract; Sec. III", "6,927 Codeforces accounts retrieved", "Kept", "6,927", "Abstract; Table I"),
 ("Abstract; Sec. III", "Balanced set of 1,816 users matched on peak rating", "Changed",
  f"{c['n']:,} accounts ({c['active']:,} active, {c['attrition']} attrition), both restricted to peak rating < 1500, after removing 888 accounts with incomplete histories; all eligible active accounts used", "Sec. III-B, III-C; Table I"),
 ("Abstract; Fig. 4; Sec. IV; Conclusion", "Attrition follows an 83.7 percent fall in contest participation (7.27 vs. 1.19 contests per month)", "Withdrawn",
  f"Computed on the unmatched sample (Spec A), which also contained 4 accounts rated 2400 or more. Rating-restricted analysis cohort: {med('contests_per_month')} contests per month; a window-dependent, descriptive measure only", "Table II (descriptive)"),
 ("Abstract; Fig. 6; Sec. IV", "42.7 percent drop in problems solved per month (13.70 vs. 7.86)", "Withdrawn",
  f"Unmatched sample. Rating-restricted analysis cohort: {med('problems_solved_per_month')} problems per month; window-dependent, descriptive only", "Table II (descriptive)"),
 ("Abstract; Table III; Fig. 12; Conclusion", "Random Forest cross-validation F1 of 0.682 on the audited behavioral data", "Withdrawn",
  f"Replaced by ROC-AUC (primary measure): logistic regression {f3(LR['auc_oof'])} [{f3(LR['auc_ci95'][0])}, {f3(LR['auc_ci95'][1])}], random forest {f3(RF['auc_oof'])} [{f3(RF['auc_ci95'][0])}, {f3(RF['auc_ci95'][1])}]; no model exceeds the F1 of always predicting attrition", "Table III; Sec. IV-C"),
 ("Abstract; Table IV; Fig. 13; Conclusion", "Survey model cross-validation F1 of 0.832 (0.833 logistic regression)", "Withdrawn", SV + " The survey models predicted the majority class.", "-"),
 ("Abstract; Sec. I (contributions); Conclusion", "Skill-Application Paradox", "Withdrawn", "Not supported by any test that survives correction. " + SV, "-"),
 ("Abstract; Sec. IV; Fig. 15; Conclusion", "Early Warning System over 22 active students (six high, ten medium, six low risk; scores 68-97 percent)", "Withdrawn",
  "Without follow-up data the high-risk students are the classifier's false positives.", "-"),
 ("Sec. I (RQ1-RQ3)", "Three research questions (reasons for quitting; behavioral separation; survey models)", "Changed",
  "RQ1: size of behavioral differences at similar peak rating; RQ2: separability and its robustness; RQ3: whether a difference is already present in the activity recorded before users became inactive (" + B1TXT + ")", "Sec. I; Sec. IV-F; Table IV"),
 ("Sec. I (contributions)", "Intensity Ratio and Editorial Dependency Index as contributions", "Withdrawn",
  f"Intensity Ratio replaced by problems solved per contest (Spearman 0.99); the Editorial Dependency Index adds nothing (change in ROC-AUC {R['b6_ablation']['without EDI']['LR']['delta_vs_all']:+.3f} LR, {R['b6_ablation']['without EDI']['RF']['delta_vs_all']:+.3f} RF when removed). Neither is listed as a contribution", "Sec. IV-E; Fig. 4"),
 ("Sec. I (contributions)", "Empirical baseline linking global telemetry to localized survey data", "Withdrawn", "The two layers share no subjects, features or labels. " + SV, "-"),
 ("Sec. III", "4,047 active accounts below the threshold", "Changed", f"{c['active']:,} after the data-quality rule (4,047 before it)", "Table I"),
 ("Sec. III; Table I", "Peak rating below 2400 removed 35 accounts", "Kept", "35", "Table I"),
 ("Sec. III", "True Attrition: three months without a submission and never above 1500", "Changed",
  "Defined as a label (no submission for >= 90 days before T_obs, peak < 1500), not as proof of quitting; tested at 6 and 12 months and at 1400 and 1600", "Sec. III-B; Table IV"),
 ("Sec. III; Table I", "Table I stage counts", "Changed", "New stage: data-quality rule (888 accounts with incomplete histories, all active; 880 after the 2400 step)", "Table I"),
 ("Sec. III (Dataset 2); Abstract; Conclusion", "Survey at ten public and private universities in Bangladesh, 96 responses", "Withdrawn",
  "The form did not record institution; the link was shared with student groups at ten universities. " + SV, "-"),
 ("Sec. III (Dataset 2)", "Ethics approval on 17 March 2026", "Changed", "Application considered 24 Feb 2026 (verbal approval), letter 17 Mar 2026; documents sent to the Editor. " + SV, "Response A3"),
 ("Sec. III; Table II", "Survey tests: upsolving chi-square 23.18, p < 0.001, V = 0.60 [0.45, 0.77]", "Withdrawn",
  "Q11 and Q33 measure different constructs and cannot be compared. " + SV, "-"),
 ("Sec. IV; Table II; Fig. 9", "Mathematics self-rating 3.93 vs. 3.41, t = -2.31, p = 0.027, d = -0.65", "Withdrawn", "Does not survive correction (Holm 0.161). " + SV, "-"),
 ("Sec. IV; Fig. 9", "Data-structure understanding 3.52 vs. 3.09", "Withdrawn", SV, "-"),
 ("Table II", "dsa_grade, mentor_support, ds_understanding, thought_quit, prior_exp, long_break tests", "Withdrawn", SV, "-"),
 ("Sec. IV (long break)", "73 percent of the attrition group reported a long break vs. 59 percent of active", "Withdrawn",
  "Error: 73% = 37/51 included the 9 respondents removed from the analysis; the correct figure is 28/42 = 67%. " + SV, "-"),
 ("Sec. IV", "Statistics 73.00 and 60.46 (break history, peer circle)", "Withdrawn", "Artifacts of unpaired branches. " + SV, "-"),
 ("Sec. IV; Fig. 10", "Upsolving habit 35.5 percent of survey Random Forest importance; data structures 17.2, mathematics 11.0, grade 8.7 percent", "Withdrawn", SV, "-"),
 ("Sec. IV; Fig. 11", "Stalled progress most common reason (12 of 51), others 9, other tracks 9, guidance 8, pressure 7, burnout 6", "Withdrawn",
  "Confidence intervals overlap; reasons cannot be ranked. " + SV, "-"),
 ("Sec. IV; Fig. 5", "Struggle time 2,646 vs. 3,059 minutes, 15.6 percent increase, p = 0.213", "Changed",
  f"Unmatched means. Analysis cohort: {med('avg_struggle_minutes', 1)} minutes, r = {f2(D['avg_struggle_minutes']['r'])}, Holm p = {D['avg_struggle_minutes']['p_holm']:.2f}", "Table II"),
 ("Sec. IV", "Math solve rate 0.469 vs. 0.538", "Changed", f"{med('math_solve_rate', 3)}, r = {f2(D['math_solve_rate']['r'])}", "Table II; Fig. 1"),
 ("Sec. IV", "Data-structure solve rate 0.400 vs. 0.480", "Changed", f"{med('ds_solve_rate', 3)}, r = {f2(D['ds_solve_rate']['r'])}", "Table II; Fig. 1"),
 ("Sec. IV; Fig. 7", "Burnout 45.0 vs. 29.8 percent, 51 percent higher", "Withdrawn",
  "Unmatched sample; the activity-decay measure partly follows from the definition of the label (reviewer B8). Removed", "-"),
 ("Sec. IV; Fig. 8", "Upsolving: 68.0 vs. 67.2 percent in the never band; among upsolvers 2.94 vs. 2.81", "Withdrawn",
  f"2.94 vs. 2.81 were averages over all users, not over upsolvers (error). Analysis cohort: upsolves per contest {med('upsolves_per_contest', 3)}, Holm p = {D['upsolves_per_contest']['p_holm']:.2f}", "Table II"),
 ("Sec. IV; Table III", "Spec A/B/C cross-validation F1 for nine classifiers (e.g. ensemble 0.737, 0.767, 0.679; RF 0.731, 0.775, 0.682)", "Withdrawn",
  "Reproduced within 0.008 by the deposited script, but F1 on balanced data is not informative (always-attrition F1 = 0.667). Replaced by two pre-specified models with ROC-AUC, PR-AUC and calibration", "Table III"),
 ("Table III (test set)", "Spec C test-set accuracy, F1 and recall (e.g. RF 0.613, 0.650, 0.720)", "Withdrawn",
  "Re-run: identical for 7 of 9 classifiers; RF 0.643, 0.681, 0.764 and ensemble 0.624, 0.655, 0.714 differ (library-version randomness). Single 20% test set no longer used", "Response B9"),
 ("Sec. IV", "Temporal features worth roughly 0.09 F1 (0.775 vs. 0.682)", "Withdrawn", "F1 replaced; window-dependent features excluded from all models by design", "Sec. III-D"),
 ("Sec. IV", "Per-fold standard deviations 0.011-0.043", "Changed", f"ROC-AUC fold SD {f3(LR['auc_fold_sd'])} (LR), {f3(RF['auc_fold_sd'])} (RF)", "Table III"),
 ("Sec. IV", "Earlier survey specification RF 0.924", "Withdrawn", SV, "-"),
 ("Sec. IV; Fig. 14", "Account tenure 14.3, contest frequency 12.4, Intensity Ratio 11.3 percent importance (unaudited, unmatched model)", "Withdrawn",
  "Unmatched, window-dependent features. New: permutation importance over all folds", "Fig. 4(a)"),
 ("Sec. IV; Conclusion", "Intensity Ratio becomes the top-ranked feature after the audit", "Changed",
  f"Its window-invariant form, problems solved per contest, ranks first in {100 * R['importance_folds']['solved_per_contest']['share_of_folds_ranked_first']:.0f}% of folds; math-tag acceptance rate in {100 * R['importance_folds']['math_solve_rate']['share_of_folds_ranked_first']:.0f}%; ranking below the first is not reliable", "Sec. IV-E; Fig. 4"),
 ("Sec. V (Practical implications)", "Recommend upsolving discipline, review sessions, mentor pairings", "Withdrawn", "Not supported by any analysis (reviewer D5)", "-"),
 ("Sec. V; Conclusion", "Two layers point the same way (replication of direction)", "Withdrawn", SV, "-"),
 ("Conclusion", "Differences persist when cohorts are held to the same peak-rating ceiling", "Changed",
  f"Small differences persist (absolute rank-biserial r ≤ {max(abs(D[f]['r']) for f in R['settings']['features']):.2f} for model features); ROC-AUC {min(d['rf_auc'] for d in B4 + [{'rf_auc': R['b5']['rf_auc_mean']}]):.2f}-{max(d['lr_auc'] for d in B4):.2f} across analyses", "Sec. IV-B, IV-D"),
 ("Fig. 1", "Two-layer research framework", "Withdrawn", SV, "-"),
 ("Fig. 2, Fig. 3", "MLP architecture; soft-voting ensemble diagrams", "Withdrawn", "These models are no longer used", "-"),
 ("Table V", "Feature specification for both layers", "Changed", "Codeforces measures only, as implemented", "Table V (Appendix A)"),
 ("Appendix B", "Survey instrument", "Withdrawn", SV, "-"),
 ("References", "Reference list (35 entries; [5], [9], [10] with errors and the title of [6] truncated; [23] Dunn used for Bonferroni)", "Changed",
  f"{NREF} references cited in the revised paper, all checked against Crossref/DataCite; DOIs added for {NDOI} (the other {NREF - NDOI} have none); Dunn 1961 removed", "References"),
 ("Author contributions", "Three authors described as giving general support, supporting tasks or limited support", "Changed", "Same seven authors in the same order; each author's specific contribution to the revised version is stated (reviewer A10) and confirmed in the signed statement", "Author Contributions"),
]
md = ["# Claims of the published article and their status in the revised paper", "",
      "Published article: AJSE 25(2):231-243, DOI 10.53799/vka5w161. New values from `results/r4_results.json` and `results/r5_b1_results.json` (release v3.0; checked by `reproduce_all.sh`).", "",
      "| # | Where (published) | Published number or claim | Status | New value or reason | Where (revised) |", "|---|---|---|---|---|---|"]
for i, r in enumerate(rows, 1): md.append(f"| {i} | " + " | ".join(x.replace("|", "/") for x in r) + " |")
n = {s: sum(r[2] == s for r in rows) for s in ["Kept", "Changed", "Withdrawn"]}
md += ["", f"Totals: {len(rows)} items; Kept {n['Kept']}, Changed {n['Changed']}, Withdrawn {n['Withdrawn']}."]
(V3 / "output").mkdir(exist_ok=True)
(V3 / "output" / "claims_table_v3.md").write_text("\n".join(md))
json.dump([dict(zip(["where_published", "published", "status", "new_value_or_reason", "where_revised"], r)) for r in rows],
          open(V3 / "output" / "claims_table_v3.json", "w"), ensure_ascii=False, indent=1)
print(f"claims table: {len(rows)} rows {n}")
