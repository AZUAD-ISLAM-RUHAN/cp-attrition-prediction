"""
r5_t_obs_reconstruction.py  (reviewer items A6 and E4)
The collection notebook built the feature file at datetime.now() (T_obs) without recording it. Each released row has
account_age_months = round((T_obs - registrationTimeSeconds) / 30 days, 1), and registrationTimeSeconds is in the raw
user.info records, so every row bounds T_obs; the intersection over all 6,927 rows gives T_obs to within minutes.
It also checks that the published file and the private copy with real handles are the same records in the same order.
Usage: python scripts/revision/r5_t_obs_reconstruction.py --features-with-handles <private csv> --users-info <users_info.jsonl>
Writes results/r5_t_obs.json (no handles).
"""
import argparse, json, os
import numpy as np, pandas as pd
from datetime import datetime, timezone
ap = argparse.ArgumentParser(); ap.add_argument("--features-with-handles", required=True); ap.add_argument("--users-info", required=True)
a = ap.parse_args(); M = 30 * 24 * 3600
priv, pub = pd.read_csv(a.features_with_handles), pd.read_csv("data/cf_attrition_features.csv")
info = {}
for line in open(a.users_info, encoding="utf-8"):
    o = json.loads(line); info[o["handle"]] = o["info"]
time_cols = ["account_age_months", "months_since_last_submission"]   # depend on T_obs (status_proxy follows the second)
other = [c for c in pub.columns if c not in ["handle", "status_proxy"] + time_cols]
def eq(x, y): return np.isclose(x, y, equal_nan=True).all() if pd.api.types.is_numeric_dtype(x) else (x.astype(str) == y.astype(str)).all()
same = all(eq(priv[c], pub[c]) for c in other)
flips = int((priv.status_proxy != pub.status_proxy).sum())
diff = {c: int((~np.isclose(priv[c], pub[c])).sum()) for c in time_cols}
def window(df):
    lo, hi = -1e18, 1e18
    for h, age in zip(priv.handle, df.account_age_months):
        reg = info[h]["registrationTimeSeconds"]; lo = max(lo, reg + (age - 0.05) * M); hi = min(hi, reg + (age + 0.05) * M)
    f = lambda t: datetime.fromtimestamp(t, timezone.utc).isoformat()
    return [f(lo), f(hi)]
out = {"rows": len(pub), "all_non_time_columns_identical_in_same_order": bool(same), "rows_differing_by_0.1_in_time_columns": diff, "status_label_changes_between_the_two_builds": flips,
       "ratings_match_user_info": bool(all(info[h]["rating"] == r for h, r in zip(priv.handle, pub.current_rating))),
       "T_obs_published_file_utc": window(pub), "T_obs_private_copy_utc": window(priv)}
os.makedirs("results", exist_ok=True); json.dump(out, open("results/r5_t_obs.json", "w"), indent=1); print(json.dumps(out, indent=1))
