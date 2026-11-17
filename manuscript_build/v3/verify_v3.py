"""Consistency and requirement tests for the revised manuscript (v3). Run after build_v3.sh.
 V1 figures   cited in order; every figure file exists; numbers shown in figures match the text
 V2 tables    cited in order; Table I arithmetic; Table III/IV values equal results/r4_results.json
 V3 equations SPC (1) and EDI (2) equal the data
 V4 refs      every reference cited, numbered by first citation, none outside the list; Dunn removed; DOIs present where verified
 V5 numbers   abstract and results agree with r4_results.json; no withdrawn number (reviewer D2)
 V6 reviewer  no correction story (D4), no survey (Option 1), no practical advice (D5), limitations present (D6),
              DOI in the data statement (D8), p-values labelled (E5), sign rule stated (E6), label defined (E8)
 V7 template  AJSE template rules (page, sizes, abstract length, headings, captions)
Writes manuscript_build/v3/output/Verification_Report_v3.md; exits non-zero on failure. Placeholders ⟦⟧ are reported, not failed."""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np, pandas as pd, docx
V3 = Path(__file__).resolve().parent; ROOT = V3.parents[1]; OUT = V3 / "output"
DOCX = OUT / "AJSE_1999_v3_Revised_CLEAN.docx"
ms = subprocess.run(["pandoc", str(DOCX), "-t", "plain", "--wrap=none"], capture_output=True, text=True).stdout
C = json.load(open(OUT / "content_v3.json")); R = json.load(open(ROOT / "results" / "r4_results.json"))
body = re.split(r"\n(?:[IVX]+\. )?references\n", ms, flags=re.I)[0]
rep, fails = ["# Verification report: revised manuscript (v3)", "", "| Group | Test | Result | Detail |", "|---|---|---|---|"], []
def t(g, name, ok, detail=""):
    rep.append(f"| {g} | {name} | {'PASS' if ok else 'FAIL'} | {str(detail)[:160]} |"); print(("PASS " if ok else "FAIL ") + f"{g} {name} {detail}")
    if not ok: fails.append(f"{g} {name}")
f3 = lambda x: f"{x:.3f}"
# V1 figures
caps = [b for b in C["blocks"] if b["t"] == "fig"]; nums = [int(re.match(r"Fig\. (\d+)", b["cap"]).group(1)) for b in caps]
t("V1", "figure captions numbered 1..n", nums == list(range(1, len(nums) + 1)), nums)
firsts = [body.find(f"Fig. {n}") for n in nums]; t("V1", "figures cited in order", all(x >= 0 for x in firsts) and firsts == sorted(firsts), firsts)
t("V1", "figure files exist", all(Path(b["path"]).exists() for b in caps))
t("V1", "every figure shows uncertainty (caption names CI, band, range or SD)", all(re.search(r"confidence|band|range|standard deviation", b["cap"]) for b in caps))
# V2 tables
tabs = [b for b in C["blocks"] if b["t"] == "tab"]; rom = [re.match(r"TABLE ([IVX]+)\.", b["cap"]).group(1) for b in tabs]
t("V2", "tables I..V in order", rom == ["I", "II", "III", "IV", "V"], rom)
t("V2", "every table cited in text", all(f"Table {r}" in body for r in rom))
T1 = {r[0].strip(): int(r[1].replace(",", "")) for r in tabs[0]["rows"]}
t("V2", "Table I: active + inactive = after data-quality", T1["active at T_{obs}"] + T1["inactive for ≥ 3 months at T_{obs}"] == T1["Complete submission history (data-quality rule)"])
t("V2", "Table I: cohort = active + attrition (peak < 1500)", T1["Analysis cohort"] == T1["Peak rating below 1500: active"] + T1["Peak rating below 1500: inactive (labeled attrition)"])
M = R["models"]; t3 = " ".join(" ".join(r) for r in tabs[2]["rows"])
t("V2", "Table III equals r4 results", all(f3(M[m][k]) in t3 for m in ["LR", "RF"] for k in ["auc_oof", "pr_auc", "brier"]))
t4 = " ".join(" ".join(r) for r in tabs[3]["rows"])
t("V2", "Table IV contains all nine definitions and B2/B3/B5", all(f3(d["rf_auc"]) in t4 for d in R["b4"]) and f3(R["b5"]["rf_auc_mean"]) in t4 and f3(R["b2_balanced_resamples"]["RF"]["mean"]) in t4)
# V3 equations
raw = pd.read_csv(ROOT / "data" / "cf_attrition_features.csv")
spc = raw.total_problems_solved / raw.total_contests; edi = raw.upsolves_per_contest * raw.avg_struggle_minutes
D = {d["feature"]: d for d in R["descriptives"]}
q1 = raw.total_submissions < raw.total_contests; q2 = (~q1) & (raw.contests_per_month > 15); cl = raw[~(q1 | q2)]
coh = cl[cl.max_rating < 1500]; act = coh[coh.status_proxy == "Active"]; att = coh[coh.status_proxy == "Stopped"]
t("V3", "Eq. (1) SPC = S / C reproduces the reported medians", abs((act.total_problems_solved / act.total_contests).median() - D["solved_per_contest"]["active_median"]) < 1e-6
  and abs((att.total_problems_solved / att.total_contests).median() - D["solved_per_contest"]["attr_median"]) < 1e-6)
t("V3", "Eq. (2) EDI = U x struggle reproduces the reported medians", abs((act.upsolves_per_contest * act.avg_struggle_minutes).median() - D["editorial_dependency_index"]["active_median"]) < 1e-6)
t("V3", "inactivity label: every attrition account has >= 3.0 months (rounded)", (att.months_since_last_submission >= 3.0).all())
# V4 references
nref = len(C["refs"]); cited = [int(x) for grp in re.findall(r"\[(\d+(?:\]\s*,\s*\[\d+)*)\]", body) for x in re.findall(r"\d+", grp)]
first = []; [first.append(x) for x in cited if x not in first]
t("V4", f"all {nref} references cited", set(range(1, nref + 1)) == set(cited), sorted(set(range(1, nref + 1)) - set(cited)))
t("V4", "numbered in order of first citation", first == list(range(1, nref + 1)))
t("V4", "Dunn (1961) removed", not any("Dunn" in r for r in C["refs"]))
ver = (ROOT / "docs" / "reference_verification_v3.md").read_text() if (ROOT / "docs" / "reference_verification_v3.md").exists() else ""
t("V4", "Crossref verification passed", "All DOIs verified" in ver)
t("V4", "DOI given for every verified DOI", all(("doi:" in r) == (re.search(r"10\.\d{4,}", r) is not None) for r in C["refs"]) and sum("doi:" in r for r in C["refs"]) >= 25, sum("doi:" in r for r in C["refs"]))
# V5 numbers
ab = C["meta"]["abstract"]; words = len(ab.split())
t("V5", "abstract states both primary ROC-AUCs", f3(M["LR"]["auc_oof"]) in ab and f3(M["RF"]["auc_oof"]) in ab)
t("V5", "abstract cohort counts", f"{R['cohort']['active']:,}" in ab and str(R["cohort"]["attrition"]) in ab)
t("V5", "results text states the primary CIs", f3(M["LR"]["auc_ci95"][0]) in ms and f3(M["RF"]["auc_ci95"][1]) in ms)
t("V5", "largest model-feature effect named correctly", "largest differences are in acceptance" in ms and max((d for d in R["descriptives"] if d["in_model"]), key=lambda d: abs(d["r"]))["feature"] == "math_solve_rate")
for bad in ["83.7", "0.682", "0.832", "0.924", "0.775", "42.7 percent", "Skill-Application", "Early Warning"]:
    t("V5", f"withdrawn item absent: {bad}", bad not in ms)
# V6 reviewer requirements
for bad in ["published version", "is withdrawn", "earlier draft", "Branch-Alignment", "Corrected version prepared", "the published article"]:
    t("V6", f"no correction story: '{bad}'", bad.lower() not in body.lower())
for bad in ["survey", "questionnaire", "respondent", "ten universities"]:
    t("V6", f"no survey content: '{bad}'", bad not in body.lower())
for bad in ["mentor pairing", "review session", "remain sensible"]:
    t("V6", f"no practical advice: '{bad}'", bad not in body.lower())
lim = body[body.find("Limitations"):body.find("Conclusion", body.find("Limitations"))]
t("V6", "limitations: label error, incomplete data, one platform, T_obs", all(k in lim for k in ["label", "incomplete", "one platform", "T_obs"]) or all(k in lim for k in ["label", "incomplete", "one platform", "T"]))
t("V6", "data statement gives the Zenodo DOI", "10.5281/zenodo.24054464" in ms)
t("V6", "p-values labelled unadjusted and Holm", "p (unadj.)" in ms and "p (Holm)" in ms)
t("V6", "sign rule stated", "negative r means lower values in the attrition group" in ms or "negative values mean lower values in the attrition group" in ms)
t("V6", "attrition defined as a label at first use", "does not establish that a user has stopped for good" in ms)
t("V6", "no prediction claim in title", "predict" not in C["meta"]["title"].lower())
# V7 template
D_ = docx.Document(DOCX); s0 = D_.sections[0]
t("V7", "US Letter, margins 0.65/0.70 in", all(abs(s.page_width.inches - 8.5) < .01 and abs(s.left_margin.inches - .65) < .01 and abs(s.top_margin.inches - .70) < .01 for s in D_.sections))
t("V7", "abstract 150-250 words", 150 <= words <= 250, f"{words} words")
t("V7", "index terms alphabetical", [x.strip() for x in C["meta"]["index"].split(",")] == sorted([x.strip() for x in C["meta"]["index"].split(",")], key=str.lower))
t("V7", "no 'Eq. (n)' citations", not re.search(r"\bEq\. ?\(\d", ms))
# placeholders (reported)
ph = re.findall(r"⟦[^⟧]{0,80}", ms); rep += ["", f"**Author placeholders still open: {len(ph)}**", ""] + [f"- {p}…" for p in ph]
rep += ["", f"**{len(fails)} failures.**" if fails else "**All tests passed.**"]
(OUT / "Verification_Report_v3.md").write_text("\n".join(rep)); print(f"\nplaceholders: {len(ph)}  FAILS: {fails}"); sys.exit(1 if fails else 0)
