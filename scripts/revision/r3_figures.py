"""
r3_figures.py - draws every figure of the corrected manuscript from
results/r3_results.json, data/cf_matched_modelling_set.csv and
data/survey_analysis_set_n64.csv (all written by r3_inquiry_reanalysis.py).
No number on any figure is typed by hand.
    python scripts/revision/r3_figures.py
"""
import json, os
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use("Agg"); import matplotlib.ticker
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

R = json.load(open("results/r3_results.json"))
M = pd.read_csv("data/cf_matched_modelling_set.csv")
S = pd.read_csv("data/survey_analysis_set_n64.csv")
os.makedirs("figures/revised", exist_ok=True)
NAVY, CORAL, GREY, MID = "#1B2A4A", "#D9553F", "#9AA3B2", "#5B6E91"
# AJSE (IEEE) template, "Guidelines for Graphics Preparation": Times New Roman, Helvetica or Arial; labels about
# 8 to 10 pt at printed size; colour figures at least 300 dpi; one column = 3.5 in, page width = 7.16 in;
# sub-figure labels (a), (b), ... centred below each part in 8 pt Times New Roman; axis labels in words, units in ().
# Figures are drawn at their printed width, so the point sizes below are the printed sizes.
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Liberation Sans", "Helvetica"],
                     "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
                     "legend.fontsize": 7.5, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.constrained_layout.use": True})      # the saved image keeps exactly the printed width
import logging; logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)   # Times New Roman -> Liberation Serif fallback
SERIF = ["Times New Roman", "Liberation Serif"]
W, WIDE = 3.45, 7.0                               # printed widths (inches): one column, full page
DPI = 400
def sublabel(ax, k, y=-0.30):
    ax.text(0.5, y, f"({'abcdefgh'[k]})", transform=ax.transAxes, ha="center", va="top", fontsize=8, fontfamily=SERIF)
def fp(p): return "< 0.001" if p < 0.001 else f"= {p:.3f}"
def save(fig, name):
    fig.savefig(f"figures/revised/{name}.png", dpi=DPI); plt.close(fig)

def box(ax, x, y, w, h, text, fc="#EEF2F8", ec=NAVY, fs=8, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.008,rounding_size=0.015",
                                fc=fc, ec=ec, lw=0.8))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", wrap=True)
def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=0.8, mutation_scale=7))

# ---- Fig 1 study design ------------------------------------------------------------
sf, cf = R["survey_flow"], R["cf_cohorts"]["primary_matched_clean"]
fig, ax = plt.subplots(figsize=(WIDE, 4.1)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
ax.text(0.25, 0.975, "A: Codeforces logs", ha="center", fontsize=9, fontweight="bold", color=NAVY)
ax.text(0.75, 0.975, "B: Student survey", ha="center", fontsize=9, fontweight="bold", color=CORAL)
L = [(0.86, f"Public API, rating-stratified\nhandle pool; {R['cf_flow']['rows_in_released_file']:,} accounts\npassed collection gate"),
     (0.68, f"Data-quality checks\n-> {R['cf_flow']['rows_after_data_quality']:,} accounts"),
     (0.50, f"Labels at T_obs; peak rating\n< 1500 in BOTH classes\n(rating-matched)"),
     (0.32, f"Balanced cohort n = {cf['n']:,}\nleakage-audited features\n(window-invariant)"),
     (0.13, "Group comparisons +\n9 classifiers vs trivial\nbaselines (ROC-AUC)")]
Rr = [(0.86, f"Anonymous online form\n{sf['responses']} responses\n(REC-approved)"),
      (0.68, f"Exclude never started ({sf['excluded_never_started']})\n-> {sf['cp_experienced']} with CP experience"),
      (0.50, f"Exclude intentional exits ({sf['excluded_intentional_exit']})\n-> n = {sf['analysis_set']} ({sf['active']} active,\n{sf['true_attrition']} stopped)"),
      (0.32, "Items comparable across\nquestionnaire branches only"),
      (0.13, "Reasons for stopping +\nexploratory group tests\n(effect sizes, Holm/BH)")]
for col, items, ec in [(0.25, L, NAVY), (0.75, Rr, CORAL)]:
    for k, (y, t) in enumerate(items):
        box(ax, col, y, 0.40, 0.145, t, fs=8, ec=ec, fc="#EEF2F8" if ec == NAVY else "#FBEDEA")
        if k: arrow(ax, col, items[k - 1][0] - 0.07, col, y + 0.07)
ax.plot([0.5, 0.5], [0.05, 0.95], ls=":", color=GREY, lw=0.8)
ax.text(0.5, 0.015, "No shared subjects, features or labels: results are reported side by side, not merged.",
        ha="center", fontsize=8, style="italic")
save(fig, "fig01_study_design")

# ---- Fig 2 cohort flow ----------------------------------------------------------------
f, a = R["cf_flow"], R["cf_flow"]["after_dq"]
dq = sum(f["dq_q1_fewer_submissions_than_rated_contests"].values()) + sum(f["dq_q2_more_than_15_contests_per_month"].values())
fig, ax = plt.subplots(figsize=(WIDE, 4.2)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
FS2 = 8
box(ax, 0.5, 0.93, 0.92, 0.10, f"Released feature file: {f['rows_in_released_file']:,} accounts (current rating 1-2399,\n>= 5 rated contests, >= 1 accepted submission)", fs=FS2)
box(ax, 0.5, 0.77, 0.92, 0.10, f"Data-quality checks passed: {f['rows_after_data_quality']:,}  (excluded {dq:,}, all Active:\nretrieved submission history shorter than rated-contest history)", fs=FS2)
box(ax, 0.255, 0.58, 0.47, 0.10, f"Active at T_obs\n{a['active']:,}", fs=FS2)
box(ax, 0.745, 0.58, 0.47, 0.10, f"Stopped (>= 3 months idle)\n{a['stopped']:,}", fs=FS2)
box(ax, 0.255, 0.38, 0.47, 0.13, f"Peak rating < 1500\n{a['active_peak_lt1500_matched_pool']:,}\n(excluded >= 1500: {a['active_peak_ge1500_excluded_by_matching']:,})", fs=FS2)
box(ax, 0.745, 0.38, 0.47, 0.13, f"True attrition, peak < 1500\n{a['stopped_peak_lt1500_true_attrition']:,}\n(intentional exit excluded: {a['stopped_peak_ge1500_intentional_exit_excluded']:,})", fs=FS2)
box(ax, 0.5, 0.12, 0.92, 0.12, f"Rating-matched modelling cohort n = {cf['n']:,}\n{cf['active']:,} active (random sample, seed 42) + {cf['attrition']:,} true attrition", fc="#E6ECF5", bold=True, fs=FS2)
for x1, y1, x2, y2 in [(0.5, 0.88, 0.5, 0.82), (0.4, 0.72, 0.26, 0.63), (0.6, 0.72, 0.74, 0.63), (0.26, 0.53, 0.26, 0.445),
                       (0.74, 0.53, 0.74, 0.445), (0.26, 0.315, 0.40, 0.18), (0.74, 0.315, 0.60, 0.18)]:
    arrow(ax, x1, y1, x2, y2)
save(fig, "fig02_cf_cohort_flow")

# ---- Fig 3 distributions -------------------------------------------------------------------
D = {r["feature"]: r for r in R["cf_descriptives_matched"]}
show = [("contests_per_month", "Rated contests\nper month", True), ("problems_solved_per_month", "Problems solved\nper month", True),
        ("solved_per_contest", "Problems solved\nper contest", True), ("avg_struggle_minutes", "Struggle time\n(min)", True),
        ("math_solve_rate", "Math-tag\nacceptance rate", False), ("ds_solve_rate", "Data-structure\nacceptance rate", False)]
fig, axs = plt.subplots(3, 2, figsize=(W, 7.4))
for k, (ax, (c, t, lg)) in enumerate(zip(axs.ravel(), show)):
    a_, s_ = M.loc[M.label == 0, c], M.loc[M.label == 1, c]
    if lg: a_, s_ = a_ + 1, s_ + 1
    bp = ax.boxplot([a_, s_], tick_labels=["Active", "Attrition"], patch_artist=True, showfliers=False, widths=0.55,
                    medianprops=dict(color="white", lw=1.4), whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7))
    for p, col in zip(bp["boxes"], [NAVY, CORAL]): p.set_facecolor(col); p.set_linewidth(0.6)
    if lg:
        ax.set_yscale("log"); ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(base=10, subs=(1, 2, 5) if max(a_.max(), s_.max()) / max(min(a_.min(), s_.min()), 1) < 1000 else (1,))); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
        ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_title(f"{t}\nr = {D[c]['r_rb']:.2f}, Holm p {fp(D[c]['p_holm'])}", fontsize=7.5)
    sublabel(ax, k, y=-0.17)
fig.get_layout_engine().set(h_pad=0.06, hspace=0.04); save(fig, "fig03_cf_matched_distributions")

# ---- Fig 4 activity decay --------------------------------------------------------------------
b = R["cf_burnout"]["primary_matched_clean"]
fig, ax = plt.subplots(figsize=(W, 2.5))
vals = [b["active_pct"], b["attr_pct"]]; cis = [b["active_ci"], b["attr_ci"]]
ax.bar(["Active", "True attrition"], vals, color=[NAVY, CORAL], width=0.5,
       yerr=[[v - c[0] for v, c in zip(vals, cis)], [c[1] - v for v, c in zip(vals, cis)]], capsize=4, error_kw=dict(lw=0.8))
for i, v in enumerate(vals): ax.text(i + 0.27, v, f"{v:.1f}%", va="center", fontsize=8, fontweight="bold")
ax.set_ylabel("Users with activity decay (%)"); ax.set_ylim(0, 60)
ax.set_title(f"n = {b['active_n']} per class\ndifference {b['diff_pp']:.1f} percentage points, 95% CI [{b['diff_ci_pp'][0]:.1f}, {b['diff_ci_pp'][1]:.1f}]", fontsize=7.5)
save(fig, "fig04_cf_activity_decay")

# ---- Fig 5 model comparison -------------------------------------------------------------------
specs = [("B_matched_12f", "B: 12 original features"), ("C_matched_r1_9f", "C: earlier audit, 9 features"), ("D_matched_consistent_8f", "D: consistent audit, 8 features")]
names = [n for n in R["cf_models"]["D_matched_consistent_8f"] if not n.startswith("Baseline")]
short = {"Logistic Regression": "LR", "Decision Tree": "DT", "Random Forest": "RF", "KNN": "KNN", "SVM": "SVM",
         "XGBoost": "XGB", "LightGBM": "LGBM", "MLP": "MLP", "Soft-Voting Ensemble": "Vote"}
fig, axs = plt.subplots(2, 1, figsize=(W, 5.6), sharex=False)
for pk, (ax, metric, ylab) in enumerate([(axs[0], "rcv_auc", "ROC-AUC"), (axs[1], "rcv_f1", "F1")]):
    w = 0.26
    for k, (key, lab) in enumerate(specs):
        mu = [R["cf_models"][key][n][metric + "_mean"] for n in names]; sd = [R["cf_models"][key][n][metric + "_sd"] for n in names]
        ax.bar(np.arange(len(names)) + (k - 1) * w, mu, w, yerr=sd, capsize=1.5, label=lab,
               color=[GREY, MID, CORAL][k], error_kw=dict(lw=0.6))
    base = 0.5 if metric == "rcv_auc" else R["cf_models"]["D_matched_consistent_8f"]["Baseline: always 'attrition'"]["rcv_f1_mean"]
    bl = ax.axhline(base, color="black", ls="--", lw=0.8, label="Chance (AUC 0.5)" if metric == "rcv_auc" else f"Always 'attrition' baseline (F1 {base:.3f})")
    if metric == "rcv_f1": ax.legend(handles=[bl], loc="upper right", frameon=False)
    ax.set_ylim(0.45, 0.85); ax.set_ylabel(f"{ylab}, repeated 5-fold CV\n(mean ± SD)")
    ax.set_xticks(range(len(names))); ax.set_xticklabels([short[n] for n in names], rotation=35, ha="right")
    sublabel(ax, pk, y=-0.24)
axs[0].legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=1, frameon=False)
fig.get_layout_engine().set(h_pad=0.08); save(fig, "fig05_cf_model_comparison")

# ---- Fig 6 permutation importance -----------------------------------------------------------
imp = pd.DataFrame(R["cf_importance_D"]).sort_values("perm_auc_drop")
NICE = {"solved_per_contest": "Problems solved per contest", "math_solve_rate": "Math-tag acceptance rate",
        "ds_solve_rate": "Data-structure acceptance rate", "upsolves_per_contest": "Upsolves per contest",
        "avg_struggle_minutes": "Struggle time", "post_drop_recovery": "Post-drop rating recovery",
        "acceptance_rate": "Overall acceptance rate", "editorial_dependency_index": "Editorial dependency index"}
fig, ax = plt.subplots(figsize=(W, 2.9))
ax.barh([NICE.get(f, f) for f in imp.feature], imp.perm_auc_drop, xerr=imp.perm_sd, color=NAVY, capsize=2, error_kw=dict(lw=0.6))
ax.axvline(0, color="black", lw=0.6)
ax.set_xlabel("Drop in held-out ROC-AUC\nwhen the feature is permuted\n(mean ± SD, 30 repeats)")
save(fig, "fig06_cf_permutation_importance")

# ---- Fig 7 survey reasons ---------------------------------------------------------------------------
rs = pd.DataFrame(R["survey_reasons"]).sort_values("n")
INT = "Interest in other tracks (Web Dev/ML)"
lab = {"Rating not increasing/no progress": "Rating not increasing / no progress", "Others": "Other (unspecified)",
       INT: "Interest in other tracks (excluded)", "Lack of guidance or mentor": "Lack of guidance or mentor",
       "Academic pressure (CGPA focus)": "Academic pressure (CGPA)", "Mental stress or burnout": "Mental stress or burnout"}
fig, ax = plt.subplots(figsize=(W, 2.7))
ax.barh([lab.get(r, r) for r in rs.reason], rs.pct, color=[GREY if r == INT else NAVY for r in rs.reason],
        xerr=[rs.pct - rs.ci.str[0], rs.ci.str[1] - rs.pct], capsize=2, error_kw=dict(lw=0.6))
for i, (p, n) in enumerate(zip(rs.pct, rs.n)): ax.text(0.8, i, f"{n} ({p:.1f}%)", va="center", color="white", fontsize=7.5, fontweight="bold")
ax.set_xlabel(f"Stopped respondents (%), n = {int(rs.n.sum())}\n(95% Wilson confidence interval)")
save(fig, "fig07_survey_reasons")

# ---- Fig 8 survey self ratings --------------------------------------------------------------------
T = {r["feature"]: r for r in R["survey_tests_comparable"]}
fig, ax = plt.subplots(figsize=(W, 2.8))
for k, c in enumerate(["math_skill", "ds_understanding"]):
    for j, (g, col) in enumerate([(S.loc[S.label == 0, c], NAVY), (S.loc[S.label == 1, c], CORAL)]):
        se = g.std(ddof=1) / np.sqrt(len(g)); h = stats.t.ppf(0.975, len(g) - 1) * se
        x = k + (j - 0.5) * 0.3
        ax.errorbar(x, g.mean(), yerr=h, fmt="o", ms=4, color=col, capsize=3, lw=0.8,
                    label=([f"Active (n={len(g)})", f"Stopped, true attrition (n={len(g)})"][j] if k == 0 else None))
        ax.text(x + 0.05, g.mean(), f"{g.mean():.2f}", fontsize=7.5, va="center")
ax.set_xticks([0, 1]); ax.set_xticklabels([f"Math skill, Q5\nHolm p {fp(T['math_skill']['p_holm'])}",
                                           f"Data-structure understanding,\nQ14/Q37, Holm p {fp(T['ds_understanding']['p_holm'])}"])
ax.set_xlim(-0.6, 1.6); ax.set_ylim(2, 5); ax.set_ylabel("Self-rating, 1-5 (mean, 95% CI)")
ax.legend(frameon=False, loc="upper right")
save(fig, "fig08_survey_self_ratings")
print("figures written to figures/revised/")
