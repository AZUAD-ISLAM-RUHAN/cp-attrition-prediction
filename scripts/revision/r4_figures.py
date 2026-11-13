"""Figures of the revised manuscript (v3), drawn from results/r4_results.json and results/r4_oof_predictions.csv.
Every figure shows uncertainty (reviewer item D7). AJSE template graphics rules: Arial (Liberation Sans where Arial is
absent), labels 7.5-9 pt at printed size, 400 dpi, one column = 3.45 in, sub-figures labelled (a), (b) in Times.
Run from the repository root:  python scripts/revision/r4_figures.py"""
import json, logging, os
import numpy as np, pandas as pd, matplotlib, matplotlib.ticker
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Liberation Sans", "Helvetica"],
                     "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
                     "legend.fontsize": 7.5, "axes.spines.top": False, "axes.spines.right": False, "figure.constrained_layout.use": True})
SERIF = ["Times New Roman", "Liberation Serif"]; W, DPI = 3.45, 400
NAVY, CORAL, GREY = "#1F3A5F", "#C8553D", "#8A8A8A"
R = json.load(open("results/r4_results.json")); OOF = pd.read_csv("results/r4_oof_predictions.csv")
os.makedirs("figures/v3", exist_ok=True)
def save(fig, name): fig.savefig(f"figures/v3/{name}.png", dpi=DPI); plt.close(fig)
def sublabel(ax, k, y=-0.22): ax.text(0.5, y, f"({'abcd'[k]})", transform=ax.transAxes, ha="center", va="top", fontsize=8, fontfamily=SERIF)

# ---- Fig. 1: effect sizes with 95% CIs
D = sorted(R["descriptives"], key=lambda d: d["r"])
D = [d for d in D if d["feature"] != "subs_per_contest"]
fig, ax = plt.subplots(figsize=(W, 3.8))
for i, d in enumerate(D):
    lo, hi = d["r_ci95"]; col = NAVY if d["in_model"] else GREY
    ax.plot([lo, hi], [i, i], color=col, lw=1.2)
    ax.plot(d["r"], i, "o", color=col, mfc=col if d["in_model"] else "white", ms=4.5)
ax.axvline(0, color="black", lw=0.6)
ax.set_yticks(range(len(D))); ax.set_yticklabels([d["label"] for d in D])
ax.set_xlabel("Rank-biserial r with 95% bootstrap CI\n(negative: lower in the attrition group)")
ax.plot([], [], "o", color=NAVY, label="Used in the models"); ax.plot([], [], "o", color=GREY, mfc="white", label="Descriptive only (depends on window)")
fig.legend(loc="outside lower center", ncol=1, frameon=False)
save(fig, "fig1_effect_sizes")

# ---- Fig. 2: calibration with bootstrap bands
y = OOF.label.values; rng = np.random.default_rng(42)
fig, ax = plt.subplots(figsize=(W, 2.9))
ax.plot([0, 0.6], [0, 0.6], ls="--", color="black", lw=0.7, label="Perfect calibration")
for col, name, c in [("p_lr", "Logistic regression", NAVY), ("p_rf", "Random forest", CORAL)]:
    p = OOF[col].values; edges = np.quantile(p, np.linspace(0, 1, 11)); b = np.clip(np.digitize(p, edges[1:-1]), 0, 9)
    mp = np.array([p[b == k].mean() for k in range(10)]); ob = np.array([y[b == k].mean() for k in range(10)])
    boots = []
    for _ in range(1000):
        ix = rng.integers(0, len(y), len(y)); yb, bb = y[ix], b[ix]
        boots.append([yb[bb == k].mean() if (bb == k).any() else np.nan for k in range(10)])
    lo, hi = np.nanpercentile(boots, 2.5, axis=0), np.nanpercentile(boots, 97.5, axis=0)
    ax.fill_between(mp, lo, hi, color=c, alpha=0.18, lw=0)
    ax.plot(mp, ob, "o-", color=c, ms=3, lw=1, label=name)
ax.axhline(R["cohort"]["prevalence"], color=GREY, lw=0.7, ls=":")
ax.text(0.6, R["cohort"]["prevalence"] + 0.01, f"base rate {R['cohort']['prevalence']:.2f}", ha="right", fontsize=7.5, color=GREY)
ax.set_xlim(0, 0.6); ax.set_ylim(0, 0.6)
ax.set_xlabel("Predicted probability of attrition (decile mean)"); ax.set_ylabel("Observed share of attrition")
ax.legend(loc="upper left", frameon=False)
save(fig, "fig2_calibration")

# ---- Fig. 3: robustness of ROC-AUC across analysis choices
rows = []
M = R["models"]
rows.append(("Primary: all eligible accounts", M["LR"]["auc_oof"], M["LR"]["auc_ci95"], M["RF"]["auc_oof"], M["RF"]["auc_ci95"], "95% CI"))
B2 = R["b2_balanced_resamples"]
rows.append((f"Balanced samples ({len(B2['RF']['values'])} draws)", B2["LR"]["mean"], [B2["LR"]["p2_5"], B2["LR"]["p97_5"]],
             B2["RF"]["mean"], [B2["RF"]["p2_5"], B2["RF"]["p97_5"]], "2.5-97.5%"))
for k, v in R["b3"]["rules"].items():
    if k.startswith("R0"): continue
    lab = {"R1": "At least 2 submissions per contest", "R2": "At least 3 submissions per contest", "R3": "At least 5 submissions per contest"}[k[:2]]
    sl, sr = v.get("lr_auc_sd", 0), v["rf_auc_sd"]
    rows.append((lab, v["lr_auc"], [v["lr_auc"] - sl, v["lr_auc"] + sl], v["rf_auc"], [v["rf_auc"] - sr, v["rf_auc"] + sr], "±SD"))
B5 = R["b5"]
rows.append(("Matched on account age and contests", B5["lr_auc_mean"], [B5["lr_auc_min"], B5["lr_auc_max"]], B5["rf_auc_mean"], [B5["rf_auc_min"], B5["rf_auc_max"]], "range"))
for d in R["b4"]:
    if d["rating_cut"] == 1500 and d["inactive_months_min"] == 3.0: continue
    sl, sr = d.get("lr_auc_sd", 0), d.get("rf_auc_sd", 0)
    rows.append((f"Peak < {d['rating_cut']}, inactive ≥ {int(d['inactive_months_min'])} months", d["lr_auc"], [d["lr_auc"] - sl, d["lr_auc"] + sl],
                 d["rf_auc"], [d["rf_auc"] - sr, d["rf_auc"] + sr], "±SD"))
fig, ax = plt.subplots(figsize=(W, 4.9))
n = len(rows)
for i, (lab, a, ca, b, cb, _) in enumerate(rows):
    yy = n - 1 - i
    ax.plot(ca, [yy + 0.16] * 2, color=NAVY, lw=1.1); ax.plot(a, yy + 0.16, "o", color=NAVY, ms=3.5)
    ax.plot(cb, [yy - 0.16] * 2, color=CORAL, lw=1.1); ax.plot(b, yy - 0.16, "s", color=CORAL, ms=3.5)
ax.axvline(0.5, color="black", lw=0.6, ls="--")
ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1])
ax.set_xlim(0.48, 0.7); ax.set_xlabel("ROC-AUC (0.5 = chance)")
ax.plot([], [], "o", color=NAVY, label="Logistic regression"); ax.plot([], [], "s", color=CORAL, label="Random forest")
fig.legend(loc="outside lower center", ncol=2, frameon=False)
save(fig, "fig3_robustness")

# ---- Fig. 4: (a) permutation importance across folds, (b) ablation
NICE = {d["feature"]: d["label"] for d in R["descriptives"]}
imp = sorted(R["importance_folds"].items(), key=lambda kv: kv[1]["mean"])
fig, axs = plt.subplots(2, 1, figsize=(W, 5.6), height_ratios=[1.5, 1])
ax = axs[0]
for i, (f, v) in enumerate(imp):
    ax.plot([v["p2_5"], v["p97_5"]], [i, i], color=NAVY, lw=1.1); ax.plot(v["mean"], i, "o", color=NAVY, ms=3.5)
ax.axvline(0, color="black", lw=0.6)
ax.set_yticks(range(len(imp))); ax.set_yticklabels([NICE[f] for f, _ in imp])
ax.set_xlabel("Drop in ROC-AUC when permuted\n(random forest; mean and 2.5-97.5%\nover cross-validation folds)")
sublabel(ax, 0, y=-0.42)
ax = axs[1]; A = R["b6_ablation"]; labs = ["without EDI", "without solved_per_contest", "without both"]
nice_ab = {"without EDI": "Without EDI", "without solved_per_contest": "Without problems per contest", "without both": "Without both"}
for i, k in enumerate(labs):
    yy = len(labs) - 1 - i
    for m, c, mk, off in [("LR", NAVY, "o", 0.14), ("RF", CORAL, "s", -0.14)]:
        v = A[k][m]; ax.plot([v["delta_p2_5"], v["delta_p97_5"]], [yy + off] * 2, color=c, lw=1.1); ax.plot(v["delta_vs_all"], yy + off, mk, color=c, ms=3.5)
ax.axvline(0, color="black", lw=0.6)
ax.set_yticks(range(len(labs))); ax.set_yticklabels([nice_ab[k] for k in labs][::-1])
ax.set_xlabel("Change in ROC-AUC vs. all 8 features\n(mean and 2.5-97.5% over paired folds)")
ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
ax.plot([], [], "o", color=NAVY, label="Logistic regression"); ax.plot([], [], "s", color=CORAL, label="Random forest")
fig.legend(loc="outside lower center", ncol=2, frameon=False)
sublabel(ax, 1, y=-0.62)
fig.get_layout_engine().set(h_pad=0.12, hspace=0.08)
save(fig, "fig4_importance_ablation")
print("figures written to figures/v3/")
