"""The four figures of the revised paper as pgfplots code, embedded in main.tex (no external image files).
Values come from results/r4_results.json and results/r4_oof_predictions.csv, with the same computations as
scripts/revision/r4_figures.py (calibration bands: same seed and bootstrap)."""
import json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
R = json.load(open(ROOT / "results" / "r4_results.json")); OOF = pd.read_csv(ROOT / "results" / "r4_oof_predictions.csv")
N = lambda x: f"{x:.4f}"

def ylabels(labels, tex): return "{" + ",".join("{" + tex(l) + "}" for l in labels) + "}"
def ebar(x, y, lo, hi): return f"({N(x)},{N(y)}) += ({N(hi - x)},0) -= ({N(x - lo)},0)"
BASE = (r"width=0.62\columnwidth, scale only axis, axis lines*=left, tick label style={font=\scriptsize}, label style={font=\scriptsize}, "
        r"xlabel style={align=center}, legend style={font=\scriptsize, draw=none, legend columns=2, /tikz/every even column/.append style={column sep=6pt}}, "
        r"legend cell align=left, clip=false, scaled x ticks=false, scaled y ticks=false")
EB = r"error bars/.cd, x dir=both, x explicit, error bar style={line width=0.7pt}, error mark=none"

def fig1(tex):
    D = sorted([d for d in R["descriptives"] if d["feature"] != "subs_per_contest"], key=lambda d: d["r"])
    mod = " ".join(ebar(d["r"], i, *d["r_ci95"]) for i, d in enumerate(D) if d["in_model"])
    des = " ".join(ebar(d["r"], i, *d["r_ci95"]) for i, d in enumerate(D) if not d["in_model"])
    n = len(D)
    return rf"""\begin{{tikzpicture}}
\begin{{axis}}[{BASE}, height=6.2cm, xmin=-0.3, xmax=0.55, ymin=-0.7, ymax={n - 0.3}, ytick={{0,...,{n - 1}}}, yticklabels={ylabels([d['label'] for d in D], tex)},
 xlabel={{Rank-biserial $r$ with 95\% bootstrap CI\\(negative: lower in the attrition group)}}, legend style={{at={{(0.25,-0.22)}}, anchor=north, legend columns=1}}]
\draw[black, line width=0.5pt] (axis cs:0,-0.7) -- (axis cs:0,{n - 0.3});
\addplot+[only marks, mark=*, mark size=1.8pt, color=ajnavy, {EB}] coordinates {{{mod}}};
\addlegendentry{{Used in the models}}
\addplot+[only marks, mark=o, mark size=1.8pt, color=ajgrey, mark options={{fill=white}}, {EB}] coordinates {{{des}}};
\addlegendentry{{Descriptive only (depends on window)}}
\end{{axis}}
\end{{tikzpicture}}"""

def fig2(tex):
    y = OOF.label.values; rng = np.random.default_rng(42); parts = []
    for col, name, c in [("p_lr", "Logistic regression", "ajnavy"), ("p_rf", "Random forest", "ajcoral")]:
        p = OOF[col].values; edges = np.quantile(p, np.linspace(0, 1, 11)); b = np.clip(np.digitize(p, edges[1:-1]), 0, 9)
        mp = np.array([p[b == k].mean() for k in range(10)]); ob = np.array([y[b == k].mean() for k in range(10)])
        boots = []
        for _ in range(1000):
            ix = rng.integers(0, len(y), len(y)); yb, bb = y[ix], b[ix]
            boots.append([yb[bb == k].mean() if (bb == k).any() else np.nan for k in range(10)])
        lo, hi = np.nanpercentile(boots, 2.5, axis=0), np.nanpercentile(boots, 97.5, axis=0)
        k = col[2:]
        parts.append(rf"\addplot[name path={k}lo, draw=none, forget plot] coordinates {{{' '.join(f'({N(a)},{N(v)})' for a, v in zip(mp, lo))}}};")
        parts.append(rf"\addplot[name path={k}hi, draw=none, forget plot] coordinates {{{' '.join(f'({N(a)},{N(v)})' for a, v in zip(mp, hi))}}};")
        parts.append(rf"\addplot[{c}, fill opacity=0.18, draw=none, forget plot] fill between[of={k}hi and {k}lo];")
        parts.append(rf"\addplot[color={c}, mark=*, mark size=1.2pt, line width=0.8pt] coordinates {{{' '.join(f'({N(a)},{N(v)})' for a, v in zip(mp, ob))}}};")
        parts.append(rf"\addlegendentry{{{name}}}")
    pr = R["cohort"]["prevalence"]
    return rf"""\begin{{tikzpicture}}
\begin{{axis}}[{BASE.replace('0.62', '0.78')}, height=4.6cm, xmin=0, xmax=0.6, ymin=0, ymax=0.6,
 xlabel={{Predicted probability of attrition (decile mean)}}, ylabel={{Observed share of attrition}},
 legend style={{at={{(0.02,0.98)}}, anchor=north west, legend columns=1}}]
\addplot[black, dashed, forget plot] coordinates {{(0,0) (0.6,0.6)}};
\addplot[ajgrey, dotted, forget plot] coordinates {{(0,{N(pr)}) (0.6,{N(pr)})}};
\node[anchor=south east, font=\scriptsize, text=ajgrey] at (axis cs:0.6,{N(pr)}) {{base rate {pr:.2f}}};
{chr(10).join(parts)}
\end{{axis}}
\end{{tikzpicture}}"""

def fig3(tex):
    M = R["models"]; rows = []
    rows.append(("Primary: all eligible accounts", M["LR"]["auc_oof"], M["LR"]["auc_ci95"], M["RF"]["auc_oof"], M["RF"]["auc_ci95"]))
    B2 = R["b2_balanced_resamples"]
    rows.append((f"Balanced samples ({len(B2['RF']['values'])} draws)", B2["LR"]["mean"], [B2["LR"]["p2_5"], B2["LR"]["p97_5"]], B2["RF"]["mean"], [B2["RF"]["p2_5"], B2["RF"]["p97_5"]]))
    lab = {"R1": "At least 2 submissions per contest", "R2": "At least 3 submissions per contest", "R3": "At least 5 submissions per contest"}
    for k, v in R["b3"]["rules"].items():
        if k.startswith("R0"): continue
        sl, sr = v["lr_auc_sd"], v["rf_auc_sd"]
        rows.append((lab[k[:2]], v["lr_auc"], [v["lr_auc"] - sl, v["lr_auc"] + sl], v["rf_auc"], [v["rf_auc"] - sr, v["rf_auc"] + sr]))
    B5 = R["b5"]
    rows.append(("Matched on account age and contests", B5["lr_auc_mean"], [B5["lr_auc_min"], B5["lr_auc_max"]], B5["rf_auc_mean"], [B5["rf_auc_min"], B5["rf_auc_max"]]))
    for d in R["b4"]:
        if d["rating_cut"] == 1500 and d["inactive_months_min"] == 3.0: continue
        rows.append((f"Peak < {d['rating_cut']}, inactive ≥ {int(d['inactive_months_min'])} months", d["lr_auc"], [d["lr_auc"] - d["lr_auc_sd"], d["lr_auc"] + d["lr_auc_sd"]],
                     d["rf_auc"], [d["rf_auc"] - d["rf_auc_sd"], d["rf_auc"] + d["rf_auc_sd"]]))
    n = len(rows); lr, rf = [], []
    for i, (l, a, ca, b, cb) in enumerate(rows):
        yy = n - 1 - i; lr.append(ebar(a, yy + 0.16, *ca)); rf.append(ebar(b, yy - 0.16, *cb))
    return rf"""\begin{{tikzpicture}}
\begin{{axis}}[{BASE.replace('0.62', '0.5')}, height=7.2cm, xmin=0.48, xmax=0.7, ymin=-0.7, ymax={n - 0.3}, ytick={{0,...,{n - 1}}},
 yticklabels={ylabels([r[0] for r in rows][::-1], tex)}, xlabel={{ROC-AUC (0.5 = chance)}}, xtick={{0.5,0.55,0.6,0.65,0.7}},
 x tick label style={{/pgf/number format/fixed, /pgf/number format/precision=2}}, legend style={{at={{(0.2,-0.13)}}, anchor=north}}]
\draw[black, dashed, line width=0.5pt] (axis cs:0.5,-0.7) -- (axis cs:0.5,{n - 0.3});
\addplot+[only marks, mark=*, mark size=1.5pt, color=ajnavy, {EB}] coordinates {{{' '.join(lr)}}};
\addlegendentry{{Logistic regression}}
\addplot+[only marks, mark=square*, mark size=1.4pt, color=ajcoral, {EB}] coordinates {{{' '.join(rf)}}};
\addlegendentry{{Random forest}}
\end{{axis}}
\end{{tikzpicture}}"""

def fig4(tex):
    NICE = {d["feature"]: d["label"] for d in R["descriptives"]}
    imp = sorted(R["importance_folds"].items(), key=lambda kv: kv[1]["mean"])
    pts = " ".join(ebar(v["mean"], i, v["p2_5"], v["p97_5"]) for i, (f, v) in enumerate(imp))
    A = R["b6_ablation"]; labs = ["without EDI", "without solved_per_contest", "without both"]
    nice = {"without EDI": "Without EDI", "without solved_per_contest": "Without problems per contest", "without both": "Without both"}
    lr = " ".join(ebar(A[k]["LR"]["delta_vs_all"], len(labs) - 1 - i + 0.14, A[k]["LR"]["delta_p2_5"], A[k]["LR"]["delta_p97_5"]) for i, k in enumerate(labs))
    rf = " ".join(ebar(A[k]["RF"]["delta_vs_all"], len(labs) - 1 - i - 0.14, A[k]["RF"]["delta_p2_5"], A[k]["RF"]["delta_p97_5"]) for i, k in enumerate(labs))
    xa = min(v["p2_5"] for _, v in imp); xb = max(v["p97_5"] for _, v in imp)
    da = min(min(A[k][m]["delta_p2_5"] for m in ("LR", "RF")) for k in labs); db = max(max(A[k][m]["delta_p97_5"] for m in ("LR", "RF")) for k in labs)
    return rf"""\begin{{tikzpicture}}
\begin{{axis}}[{BASE.replace('0.62', '0.52')}, height=4.4cm, xmin={N(min(xa, 0) - 0.005)}, xmax={N(xb + 0.005)}, ymin=-0.7, ymax={len(imp) - 0.3}, ytick={{0,...,{len(imp) - 1}}},
 yticklabels={ylabels([NICE[f] for f, _ in imp], tex)}, xlabel={{Drop in ROC-AUC when permuted (random forest;\\mean and 2.5--97.5\% over folds)}},
 x tick label style={{/pgf/number format/fixed, /pgf/number format/precision=2}}]
\draw[black, line width=0.5pt] (axis cs:0,-0.7) -- (axis cs:0,{len(imp) - 0.3});
\addplot+[only marks, mark=*, mark size=1.5pt, color=ajnavy, {EB}] coordinates {{{pts}}};
\end{{axis}}
\end{{tikzpicture}}\\[-1pt]{{\footnotesize (a)}}\\[4pt]
\begin{{tikzpicture}}
\begin{{axis}}[{BASE.replace('0.62', '0.52')}, height=2.4cm, xmin={N(da - 0.005)}, xmax={N(max(db, 0) + 0.005)}, ymin=-0.6, ymax={len(labs) - 0.4}, ytick={{0,...,{len(labs) - 1}}},
 yticklabels={ylabels([nice[k] for k in labs][::-1], tex)}, xlabel={{Change in ROC-AUC vs.\ all 8 features\\(mean and 2.5--97.5\% over paired folds)}},
 x tick label style={{/pgf/number format/fixed, /pgf/number format/precision=2}}, legend style={{at={{(0.2,-0.62)}}, anchor=north}}]
\draw[black, line width=0.5pt] (axis cs:0,-0.6) -- (axis cs:0,{len(labs) - 0.4});
\addplot+[only marks, mark=*, mark size=1.5pt, color=ajnavy, {EB}] coordinates {{{lr}}};
\addlegendentry{{Logistic regression}}
\addplot+[only marks, mark=square*, mark size=1.4pt, color=ajcoral, {EB}] coordinates {{{rf}}};
\addlegendentry{{Random forest}}
\end{{axis}}
\end{{tikzpicture}}\\[-1pt]{{\footnotesize (b)}}"""

FIGS = {"fig1_effect_sizes": fig1, "fig2_calibration": fig2, "fig3_robustness": fig3, "fig4_importance_ablation": fig4}
PREAMBLE = (r"\usepackage{pgfplots}" "\n" r"\pgfplotsset{compat=1.16}" "\n" r"\usepgfplotslibrary{fillbetween}" "\n"
            r"\definecolor{ajnavy}{HTML}{1F3A5F}\definecolor{ajcoral}{HTML}{C8553D}\definecolor{ajgrey}{HTML}{8A8A8A}")
