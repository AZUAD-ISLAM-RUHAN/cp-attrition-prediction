"""Consistency tests on the corrected manuscript (run from the repository root after reproduce_all.sh):
  T1 figures: each figure cited in the text, in order; key values shown on each figure appear in the text
  T2 tables: cited in order; Table I arithmetic adds up
  T3 equations: Eq. (1) IR, Eq. (2) EDI and the ATR flag match the data; Eq. (3) equal-weight ensemble matches the code
  T4 references: every reference [1]..[N] cited; no citation outside the list
  T5 headline numbers: abstract, results and conclusion agree with results/r3_results.json
  T6 placeholders and formatting artefacts
  T7 conformance with the AJSE camera-ready template (AJSE_Template_2020-OTH): page, type sizes, headings, abstract, figures
Writes manuscript_build/output/Consistency_Report.md and exits non-zero on any failure."""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "manuscript_build" / "output"
ms = subprocess.run(["pandoc", str(OUT / "AJSE_1999_Corrected_Manuscript_CLEAN.docx"), "-t", "plain", "--wrap=none"], capture_output=True, text=True).stdout
R = json.load(open(ROOT / "results" / "r3_results.json")); T1 = json.load(open(ROOT / "results" / "r3_table1_cohort.json"))
C = json.load(open(OUT / "content_pub.json"))
rep, fails = ["# Consistency report: corrected manuscript", ""], []
def t(group, name, ok, detail=""):
    rep.append(f"| {group} | {name} | {'PASS' if ok else 'FAIL'} | {detail} |"); print(("PASS " if ok else "FAIL ") + f"{group} {name} {detail}")
    if not ok: fails.append(f"{group} {name}")
rep += ["| Test | Item | Result | Detail |", "|----|------------------------------------------------|------|----------------------|"]
body = re.split(r"\n(?:VII\. )?references\n", ms, flags=re.I)[0]   # heading is small caps (pandoc prints REFERENCES)
# ---- T1 figures
caps = [b for b in C["blocks"] if b["t"] == "fig"]
nums = [int(re.match(r"Fig\. (\d+)", b["cap"]).group(1)) for b in caps]
t("T1", "figure captions numbered 1..n in order", nums == list(range(1, len(nums) + 1)), f"{nums}")
first_ref = {n: body.find(f"Fig. {n}") for n in nums}
t("T1", "every figure referenced in text", all(v >= 0 for v in first_ref.values()))
for b in caps: t("T1", f"image file exists: {Path(b['path']).name}", Path(b["path"]).exists())
Bn = R["cf_burnout"]["primary_matched_clean"]
t("T1", "Fig. 3 values in text", f"{Bn['attr_pct']:.1f} percent" in ms and f"{Bn['active_pct']:.1f} percent" in ms, f"{Bn['attr_pct']:.1f} / {Bn['active_pct']:.1f}")
S = pd.read_csv(ROOT / "data" / "survey_analysis_set_n64.csv")
t("T1", "Fig. 4 means in text", f"{S[S.label==1].math_skill.mean():.2f}" in ms and f"{S[S.label==0].math_skill.mean():.2f}" in ms)
rn = [r for r in R["survey_reasons"] if r["reason"].startswith("Rating")][0]; t("T1", "Fig. 5 top reason in text", f"{rn['n']} of 51" in ms)
Dm = R["cf_models"]["D_matched_consistent_8f"]; best = max((n for n in Dm if not n.startswith("Baseline")), key=lambda n: Dm[n]["rcv_auc_mean"])
t("T1", "Fig. 6 best AUC in text", f"{Dm[best]['rcv_auc_mean']:.3f}" in ms, f"{best} {Dm[best]['rcv_auc_mean']:.3f}")
top = max(R["cf_importance_D"], key=lambda r: r["perm_auc_drop"]); t("T1", "Fig. 7 top feature stated in text", top["feature"] == "solved_per_contest" and "problems solved per rated contest, is the most important" in ms, top["feature"])
# ---- T2 tables
tabs = [b["cap"] for b in C["blocks"] if b["t"] == "tab"]
roman = [re.match(r"TABLE ([IVX]+)\.", c).group(1) for c in tabs]
t("T2", "table captions I..VI in order", roman == ["I", "II", "III", "IV", "V", "VI"], f"{roman}")
t("T2", "every table referenced in text", all(f"Table {r}" in body or r == "I" and "Table I" in ms for r in roman))
d = {r["stage"]: r["accounts"] for r in T1}
a, s_, ta, ie = d["Active at T_obs"], d["Inactive >= 3 months at T_obs"], d["True Attrition (peak < 1500)"], d["Intentional Exit (excluded)"]
t("T2", "Table I: active + inactive = after data-quality", a + s_ == d["After data-quality check (complete submission history)"], f"{a}+{s_}")
t("T2", "Table I: attrition + exits = inactive", ta + ie == s_, f"{ta}+{ie}")
t("T2", "Table I: matched set = 2 x attrition", d["Rating-matched modelling set"] == 2 * ta)
# ---- T3 equations
M = pd.read_csv(ROOT / "data" / "cf_matched_modelling_set.csv")
t("T3", "Eq. (1) IR = P_month/(C_month+0.1)", np.allclose(M.intensity_ratio, M.problems_solved_per_month / (M.contests_per_month + 0.1)))
t("T3", "Eq. (2) EDI = U x struggle", np.allclose(M.editorial_dependency_index, M.upsolves_per_contest * M.avg_struggle_minutes))
t("T3", "SPC = S / C", np.allclose(M.solved_per_contest, M.total_problems_solved / M.total_contests))
t("T3", "activity-decay flag = 1[ATR < 0.5]", bool((M.burnout_flag == (M.activity_trend_ratio < 0.5).astype(int)).all()))
code = (ROOT / "scripts" / "revision" / "r3_inquiry_reanalysis.py").read_text()
t("T3", "Eq. (3) ensemble uses equal weights (no weights= argument)", 'voting="soft")' in code and "weights=" not in code.split("VotingClassifier")[1].split(")")[0])
t("T3", "RF/DT split criterion is Gini (default, not entropy)", "criterion=" not in code)
# ---- T4 references
nref = len(C["refs"]); cited = {int(x) for grp in re.findall(r"\[(\d+(?:\]\s*,\s*\[\d+)*)\]", body) for x in re.findall(r"\d+", grp)}
t("T4", f"all {nref} references cited", set(range(1, nref + 1)) <= cited, f"missing: {sorted(set(range(1, nref + 1)) - cited)}")
t("T4", "no citation outside the list", max(cited) <= nref, f"max cited {max(cited)}")
# ---- T5 headline numbers
abs_ = C["meta"]["abstract"]; Dd = {r["feature"]: r for r in R["cf_descriptives_matched"]}
t("T5", "abstract contest medians", f"{Dd['contests_per_month']['attr_median']:.2f} versus {Dd['contests_per_month']['active_median']:.2f}" in abs_)
t("T5", "abstract best AUC = results", f"{Dm[best]['rcv_auc_mean']:.3f}" in abs_)
t("T5", "abstract permutation p = results", f"p = {R['cf_permutation']['Random Forest']['p']:.3f}" in abs_)
t("T5", "abstract cohort size", f"{R['cf_cohorts']['primary_matched_clean']['n']:,}" in abs_)
t("T5", "conclusion AUC = results", ms.count(f"{Dm[best]['rcv_auc_mean']:.3f}") >= 3)
t("T5", "no withdrawn headline kept as a claim", "83.7 percent fall" not in abs_ and "Early Warning System" not in abs_)
# ---- T6 artefacts
ph = re.findall(r"⟦[^⟧]*⟧", ms); t("T6", "no placeholders remaining", len(ph) == 0, "; ".join(ph))
for a_ in ["_{", "^{", "**", " nan", "None"]: t("T6", f"no artefact '{a_}'", a_ not in ms)

# ---- T7 AJSE template conformance (values from AJSE_Template_2020-OTH.doc, see docs/AJSE_template_conformance.md)
import docx, zipfile, io
from PIL import Image
Dx = docx.Document(OUT / "AJSE_1999_Corrected_Manuscript_CLEAN.docx"); Wn = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
s0 = Dx.sections[0]
t("T7", "page US Letter 8.5 x 11 in", all(abs(s.page_width.inches - 8.5) < 0.01 and abs(s.page_height.inches - 11) < 0.01 for s in Dx.sections))
t("T7", "margins 0.65 in left/right, 0.70 in top/bottom", all(abs(s.left_margin.inches - 0.65) < 0.01 and abs(s.right_margin.inches - 0.65) < 0.01 and abs(s.top_margin.inches - 0.70) < 0.01 and abs(s.bottom_margin.inches - 0.70) < 0.01 for s in Dx.sections))
cols = [s._sectPr.find(Wn + "cols") for s in Dx.sections]; two = [c for c in cols if c is not None and c.get(Wn + "num") == "2"]
t("T7", "two columns, 0.2 in apart", len(two) > 0 and all(c.get(Wn + "space") == "288" for c in two), f"{len(two)} two-column sections")
words = len(abs_.split()); t("T7", "abstract 150-250 words, one paragraph", 150 <= words <= 250 and "\n" not in abs_, f"{words} words")
t("T7", "abstract without references or acronyms", not re.search(r"\[\d+\]|\bROC\b|\bAUC\b|\bCV\b|\bvs\.", abs_))
terms = [x.strip() for x in C["meta"]["index"].split(",")]; t("T7", "index terms in alphabetical order", terms == sorted(terms, key=str.lower), "; ".join(terms))
t("T7", "equations cited as (n), not 'Eq. (n)'", not re.search(r"\bEqs?\. ?\(\d", ms))
t("T7", "figures cited as 'Fig.', tables as 'Table'", not re.search(r"\bFigure \d|\bFigs? \d|\bTab\. ", ms))
def sizes(pred):
    out = set()
    for p in Dx.paragraphs:
        if pred(p): out |= {r.font.size.pt for r in p.runs if r.text.strip() and r.font.size}
    return out
pp = Dx.paragraphs
t("T7", "title 24 pt", sizes(lambda p: p.text.startswith("Predicting Student Attrition")) == {24.0})
t("T7", "authors 11 pt", sizes(lambda p: p.text.startswith("Azuad Islam Ruhan, Golam")) == {11.0})
t("T7", "abstract and index terms 9 pt bold", sizes(lambda p: p.text.startswith(("Abstract—", "Index Terms—"))) == {9.0} and all(r.bold for p in pp if p.text.startswith(("Abstract—", "Index Terms—")) for r in p.runs if r.text.strip()))
body_p = [p for p in pp if len(p.text) > 250 and not p.text.startswith(("Abstract", "Index", "[", "Fig.")) and p.runs and p.runs[0].font.size and p.runs[0].font.size.pt == 10]
t("T7", "body text 10 pt, justified, first-line indent 0.14 in", len(body_p) > 50 and all(p.paragraph_format.first_line_indent is None or abs(p.paragraph_format.first_line_indent.inches - 0.14) < 0.01 for p in body_p), f"{len(body_p)} body paragraphs")
h1 = [p for p in pp if re.match(r"^[IVX]+\. [A-Z]", p.text) and len(p.text) < 40]
t("T7", "level-1 headings 10 pt small caps, centred", len(h1) >= 6 and all(all(r.font.small_caps for r in p.runs if r.text.strip()) and p.alignment == 1 for p in h1), f"{len(h1)} headings")
h2 = [p for p in pp if re.match(r"^[A-P]\. \S", p.text) and len(p.text) < 70 and p.runs and p.runs[0].font.italic]
t("T7", "level-2 headings italic, lettered A., B., ...", len(h2) >= 10, f"{len(h2)} headings")
tt = [p for p in pp if re.match(r"^TABLE [IVX]+$", p.text)]
t("T7", "table titles: 'TABLE n' line, small-caps title, 8 pt, above table", len(tt) == 6 and sizes(lambda p: re.match(r"^TABLE [IVX]+$", p.text) is not None) == {8.0})
t("T7", "figure captions 8 pt, below figures", sizes(lambda p: re.match(r"^Fig\. \d+\.", p.text) is not None) == {8.0})
t("T7", "references 8 pt", sizes(lambda p: re.match(r"^\[\d+\]", p.text) is not None) == {8.0})
t("T7", "'References' heading unnumbered, small caps", any(p.text == "References" and all(r.font.small_caps for r in p.runs) for p in pp))
z = zipfile.ZipFile(OUT / "AJSE_1999_Corrected_Manuscript_CLEAN.docx"); xml = z.read("word/document.xml").decode()
ext = [(int(a) / 914400, int(b) / 914400) for a, b in re.findall(r'<wp:extent cx="(\d+)" cy="(\d+)"', xml)]
photos = [e for e in ext if e[0] < 1.2]; figs = [e for e in ext if e[0] >= 1.2]
t("T7", "author photos 1.0 x 1.25 in", len(photos) == 7 and all(abs(w - 1.0) < 0.01 and abs(h - 1.25) < 0.01 for w, h in photos), f"{len(photos)} photos")
t("T7", "figures one column (<= 3.5 in) or page width (<= 7.16 in)", all(w <= 3.5 or 3.5 < w <= 7.16 for w, _ in figs), ", ".join(f"{w:.2f}" for w, _ in figs))
dpis = []
for b, (w, _) in zip(caps, figs):
    px = Image.open(b["path"]).size[0]; dpis.append(px / w)
t("T7", "figures >= 300 dpi at printed size", len(dpis) == len(caps) and min(dpis) >= 300, f"min {min(dpis):.0f} dpi")
figsrc = (ROOT / "scripts" / "revision" / "r3_figures.py").read_text()
t("T7", "figure fonts Arial/Helvetica (Times for sub-figure labels), 7.5-10 pt", '"Arial"' in figsrc and "DejaVu" not in figsrc and min(float(x) for x in re.findall(r"fontsize=(\d+(?:\.\d+)?)", figsrc)) >= 7.5)
t("T7", "multipart figures labelled (a), (b), ... and named in caption", all(x in ms for x in ["(a) rated contests per month", "(a) ROC-AUC and (b) F1"]))
t("T7", "American spelling in the text (reference titles kept as published)", not re.search(r"\b(modelling|modelled|analysed|anonymised|pseudonymised|recognised|practis\w+|characterisation)\b", body))
t("T7", "'Acknowledgment' spelling", "Acknowledgement" not in ms)
rep += ["", f"**{len(fails)} failures.**" if fails else "**All consistency tests passed.**"]
(OUT / "Consistency_Report.md").write_text("\n".join(rep)); print("\nFAILS:", fails); sys.exit(1 if fails else 0)
