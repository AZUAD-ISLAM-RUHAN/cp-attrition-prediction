"""
r3_table1_cohort.py - stage-by-stage cohort counts (Table I of the corrected manuscript),
following the stage order of the published Table I and adding the data-quality stage.
Pure counting; runs in seconds. Writes results/r3_table1_cohort.json.
    python scripts/revision/r3_table1_cohort.py
"""
import json, os
import pandas as pd
d = pd.read_csv("data/cf_attrition_features.csv")
os.makedirs("results", exist_ok=True)
rows = []
def add(stage, n, note=""):
    rows.append({"stage": stage, "accounts": int(n), "note": note}); print(f"{stage:<62}{n:>7,}  {note}")
add("Released feature file (>=5 rated contests, current rating 1-2399)", len(d))
p = d[d.max_rating < 2400]
add("After peak rating < 2400", len(p), f"removed {len(d) - len(p)}")
q1 = p.total_submissions < p.total_contests
q2 = (~q1) & (p.contests_per_month > 15)
c = p[~(q1 | q2)]
add("After data-quality check (complete submission history)", len(c),
    f"removed {int(q1.sum())} (fewer submissions than rated contests) + {int(q2.sum())} (>15 contests/month); "
    f"all Active: {bool((p[q1 | q2].status_proxy == 'Active').all())}")
A, S = c[c.status_proxy == "Active"], c[c.status_proxy == "Stopped"]
add("Active at T_obs", len(A)); add("Inactive >= 3 months at T_obs", len(S))
add("True Attrition (peak < 1500)", (S.max_rating < 1500).sum()); add("Intentional Exit (excluded)", (S.max_rating >= 1500).sum())
add("Matching pool: active, peak < 1500", (A.max_rating < 1500).sum())
add("Sampled from pool (seed 42)", (S.max_rating < 1500).sum())
add("Rating-matched modelling set", 2 * (S.max_rating < 1500).sum())
# consistency with the cohort used by r3 (which applies the data-quality rule to the full file)
m = pd.read_csv("data/cf_matched_modelling_set.csv") if os.path.exists("data/cf_matched_modelling_set.csv") else None
if m is not None:
    print("matched set in r3 identical size:", len(m) == rows[-1]["accounts"], "| max peak in matched set:", int(m.max_rating.max()))
json.dump(rows, open("results/r3_table1_cohort.json", "w"), indent=1)
