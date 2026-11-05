"""Independent re-computation of the key numbers of the corrected (published-based) manuscript
straight from the raw files, without reusing r3 code; each is searched for in the manuscript / letter."""
import subprocess, numpy as np, pandas as pd
from scipy import stats
import os
from pathlib import Path
REPO = str(Path(__file__).resolve().parents[1]); OUTD = str(Path(__file__).resolve().parent / "output")
ms = subprocess.run(["pandoc", f"{OUTD}/AJSE_1999_Corrected_Manuscript_CLEAN.docx", "-t", "plain", "--wrap=none"], capture_output=True, text=True).stdout
let = open(f"{OUTD}/AJSE_1999_Response_to_Editorial_Inquiry.txt").read().replace("\n", " ")
both = ms + " " + let
fails = []
def check(label, s, where=both):
    ok = s in where; print(("OK   " if ok else "FAIL ") + f"{label:<44} [{s}]")
    if not ok: fails.append(label)
d = pd.read_csv(f"{REPO}/data/cf_attrition_features.csv")
check("released accounts", f"{len(d):,}")
p = d[d.max_rating < 2400]; check("after peak<2400", f"{len(p):,}", ms)
bad = (p.total_submissions < p.total_contests) | ((p.total_submissions >= p.total_contests) & (p.contests_per_month > 15))
c = p[~bad]; check("after data-quality", f"{len(c):,}", ms); check("dq removed (Table I base)", f"{bad.sum()}")
A, S = c[c.status_proxy == "Active"], c[c.status_proxy == "Stopped"]
check("active at T_obs", f"{len(A):,}", ms); check("inactive", f"{len(S):,}", ms)
check("true attrition", f"{(S.max_rating < 1500).sum()}"); check("intentional exits", f"{(S.max_rating >= 1500).sum()}", ms)
check("matching pool", f"{(A.max_rating < 1500).sum():,}")
# published Table I reproduced (no data-quality step)
pa, ps = p[p.status_proxy == "Active"], p[p.status_proxy == "Stopped"]
check("published T-I active/inactive", f"{len(pa):,} and {len(ps):,}", let); check("published pool", f"{(pa.max_rating < 1500).sum():,}", let)
# matched sample, drawn exactly as specified (pool after data-quality on the FULL file, seed 42)
full_bad = (d.total_submissions < d.total_contests) | ((d.total_submissions >= d.total_contests) & (d.contests_per_month > 15))
cf = d[~full_bad]; Af = cf[(cf.status_proxy == "Active") & (cf.max_rating < 1500)].sample(n=908, random_state=42); Sf = cf[(cf.status_proxy == "Stopped") & (cf.max_rating < 1500)]
for col, lab in [("contests_per_month", "contests"), ("problems_solved_per_month", "problems/month")]:
    a_, b_ = f"{np.median(Sf[col]):.2f}", f"{np.median(Af[col]):.2f}"   # abstract writes "versus" (template: no abbreviations)
    check(f"matched medians {lab}", f"{a_} vs. {b_}" if f"{a_} vs. {b_}" in ms else f"{a_} versus {b_}", ms)
check("burnout attrition", f"{Sf.burnout_flag.mean()*100:.1f} percent of attrition", ms)
check("burnout active", f"{Af.burnout_flag.mean()*100:.1f} percent of active", ms)
check("account age medians", f"median {np.median(Sf.account_age_months):.1f} vs. {np.median(Af.account_age_months):.1f} months", ms)
smd = (Af.max_rating.mean() - Sf.max_rating.mean()) / np.sqrt((Af.max_rating.var() + Sf.max_rating.var()) / 2); check("SMD", f"{smd:.3f}")
mw = stats.mannwhitneyu(Sf.upsolves_per_contest, Af.upsolves_per_contest); print("     upsolves MW raw p", round(mw.pvalue, 3))
# survey
sv = pd.read_csv(f"{REPO}/data/survey_responses.csv"); Sc = "6. Your current CP status? "
m = sv[sv[Sc] != "Never started CP"]; act = m[Sc].str.contains("Currently")
m64 = m[~((~act) & (m["31. Main reasons for quitting "] == "Interest in other tracks (Web Dev/ML)"))]; a64 = m64[m64[Sc].str.contains("Currently")]; s64 = m64[~m64[Sc].str.contains("Currently")]
check("survey split", f"n = {len(m64)}", ms); check("active n", f"(n = {len(a64)})", ms); check("attrition n", f"(n = {len(s64)})", ms)
k = (m.loc[~act, "31. Main reasons for quitting "] == "Rating not increasing/no progress").sum(); check("reason count", f"{k} of 51", ms)
ma, mst = a64["5. Mathematics skills rating "].mean(), s64["5. Mathematics skills rating "].mean(); check("math means", f"{mst:.2f} out of 5, against {ma:.2f}", ms)
t = stats.ttest_ind(s64["5. Mathematics skills rating "], a64["5. Mathematics skills rating "], equal_var=False); check("welch p", f"p = {t.pvalue:.3f}", ms)
holm = min(1, t.pvalue * 6); check("holm (smallest p x 6)", f"{holm:.3f}")
ct = pd.crosstab(m64[Sc].str.contains("Currently"), m64["22. Have a mentor/senior guide? "].fillna(m64["35. Had mentor/senior support? "]))
check("mentor Yates (published)", f"{stats.chi2_contingency(ct)[0]:.3f} (as published, Yates)", let)
check("mentor Pearson", f"{stats.chi2_contingency(ct, correction=False)[0]:.3f} (Pearson)", let)
XL = f"{REPO}/data/PRIVATE/Survey_ORIGINAL_with_timestamps.xlsx"
check("collection window", "between 6 March and 2 April 2026", ms)
if os.path.exists(XL):
    ts = pd.to_datetime(pd.read_excel(XL).Timestamp)
    print(f"     timestamps {ts.min().date()} .. {ts.max().date()}"); check("84 of 96", f"{(ts < '2026-03-17').sum()} of the 96", let)
else:
    dd = pd.read_csv(f"{REPO}/data/survey_response_dates.csv"); ts = pd.to_datetime(dd.response_date)
    print(f"     public response dates {ts.min().date()} .. {ts.max().date()}"); check("84 of 96", f"{(ts < '2026-03-17').sum()} of the 96", let)
for bad_s in ["{", "}", "_{", "^{", "nan "]: print(f"     artefact '{bad_s}':", ms.count(bad_s))
print("     placeholders: manuscript", ms.count("⟦"), "| letter", let.count("⟦"))
print("\nFAILS:", fails)
