"""
r5_b4_e4_return_check.py  (reviewer items B4 "return check" and E4 "unrounded values")
For the published cohort (3,421 active, 908 attrition) it asks the public Codeforces API
  B4: whether each attrition account has submitted again since T_obs (user.status, newest submission);
  E4: the exact idle time at T_obs of every account whose released inactivity value is exactly 3.0 (full user.status).
Needs the PRIVATE copy of the feature file with real handles (same rows and order as data/cf_attrition_features.csv).
Writes only aggregates: results/r5_b4_e4_results.json (no handles).
Usage: python scripts/revision/r5_b4_e4_return_check.py --features-with-handles <private csv>
"""
import json, time, urllib.request, urllib.parse, sys, argparse, os
import pandas as pd, numpy as np
from datetime import datetime, timezone
ap = argparse.ArgumentParser(); ap.add_argument("--features-with-handles", required=True); a = ap.parse_args()
raw = pd.read_csv(a.features_with_handles)                                   # private: real handles
pub = pd.read_csv("data/cf_attrition_features.csv")                          # published, hashed handles
assert len(raw) == len(pub) and (raw.max_rating.values == pub.max_rating.values).all()
pub["real"] = raw.handle.values                                        # row-aligned (verified: identical except time columns)
q1 = pub.total_submissions < pub.total_contests; q2 = (~q1) & (pub.contests_per_month > 15)
clean = pub[~(q1 | q2)]
A = clean[(clean.status_proxy == "Active") & (clean.max_rating < 1500)]
S = clean[(clean.status_proxy == "Stopped") & (clean.months_since_last_submission >= 3.0) & (clean.max_rating < 1500)]
print("cohort", len(A), len(S), flush=True); assert (len(A), len(S)) == (3421, 908)
E4 = pub[pub.months_since_last_submission == 3.0]
T_LO = datetime(2026, 6, 23, 13, 41, 18, tzinfo=timezone.utc).timestamp(); T_HI = datetime(2026, 6, 23, 13, 44, 17, tzinfo=timezone.utc).timestamp()
M = 30 * 24 * 3600
def api(method, **kw):
    url = f"https://codeforces.com/api/{method}?" + urllib.parse.urlencode(kw); d = 2.0
    for _ in range(8):
        try:
            with urllib.request.urlopen(url, timeout=60) as r: o = json.loads(r.read().decode())
            time.sleep(2.0)
            if o.get("status") == "OK": return o["result"]
            if "not found" in (o.get("comment") or "").lower(): return None
        except urllib.error.HTTPError as e:
            if e.code == 400:
                try:
                    o = json.loads(e.read().decode())
                    if "not found" in (o.get("comment") or "").lower(): time.sleep(2.0); return None
                except Exception: pass
        except Exception: pass
        time.sleep(d); d = min(60, d * 2)
    return "error"
# E4: full history -> last submission at or before T_obs -> unrounded idle months
e4 = []
for _, r in E4.iterrows():
    res = api("user.status", handle=r.real)
    if res in (None, "error"): e4.append({"status": r.status_proxy, "result": str(res)}); continue
    ts = [s["creationTimeSeconds"] for s in res if s["creationTimeSeconds"] <= T_HI]
    if not ts: e4.append({"status": r.status_proxy, "result": "no submission before T_obs"}); continue
    last = max(ts)
    e4.append({"status": r.status_proxy, "idle_months_at_T_obs": [round((T_LO - last) / M, 4), round((T_HI - last) / M, 4)],
               "idle_days_at_T_obs": [round((T_LO - last) / 86400, 2), round((T_HI - last) / 86400, 2)]})
print("E4 done", flush=True)
# B4: newest submission now
ret = gone = err = 0; per = []
for i, h in enumerate(S.real, 1):
    res = api("user.status", handle=h, **{"from": 1, "count": 1})
    if res is None: gone += 1; per.append((h, "not_found"))
    elif res == "error": err += 1; per.append((h, "error"))
    else:
        t = res[0]["creationTimeSeconds"] if res else 0
        back = t > T_HI; ret += back; per.append((h, int(t)))
    if i % 100 == 0: print(f"B4 {i}/{len(S)} returned {ret}", flush=True)
checked = len(S) - gone - err
out = {"T_obs_utc_window": [datetime.fromtimestamp(T_LO, timezone.utc).isoformat(), datetime.fromtimestamp(T_HI, timezone.utc).isoformat()],
       "checked_on_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
       "b4_return_check": {"attrition_accounts": len(S), "account_not_found": gone, "api_errors": err,
                           "submitted_again_after_T_obs": ret, "share_submitted_again": round(ret / checked, 4) if checked else None},
       "e4_accounts_shown_as_3_0": sorted(e4, key=lambda x: (x["status"], str(x.get("idle_months_at_T_obs"))))}
os.makedirs("results", exist_ok=True); json.dump(out, open("results/r5_b4_e4_results.json", "w"), indent=1)
print(json.dumps(out, indent=1), flush=True)
