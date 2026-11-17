"""
r5_b3_completeness.py  (reviewer item B3)
Compares the submission and rated-contest counts of the released feature file (built at T_obs, 23 June 2026) with the
same accounts' histories retrieved again from the public Codeforces API in November 2026 and cut at T_obs.
  equal counts          -> the June retrieval was complete;
  more now than in June -> the June retrieval missed records (incomplete history). For inactive accounts this is
                           unambiguous; an active account may also have submitted between its retrieval in June
                           (22-23 June) and T_obs, so for active accounts "more now" is an upper bound;
  fewer now             -> records removed from the platform since June.
Groups: the 908 attrition and 3,421 active accounts of the analysis cohort, and the 888 accounts removed by the
data-quality rule. Writes results/r5_b3_completeness.json (counts only, no handles).
Usage: python scripts/revision/r5_b3_completeness.py --features-with-handles <private csv> --refetched <jsonl> [<jsonl> ...]
"""
import argparse, json, os
import pandas as pd
from datetime import datetime, timezone
ap = argparse.ArgumentParser(); ap.add_argument("--features-with-handles", required=True); ap.add_argument("--refetched", nargs="+", required=True)
a = ap.parse_args()
T_OBS = datetime(2026, 6, 23, 13, 44, 17, tzinfo=timezone.utc).timestamp()
priv, pub = pd.read_csv(a.features_with_handles), pd.read_csv("data/cf_attrition_features.csv")
pub["real"] = priv.handle.values
q1 = pub.total_submissions < pub.total_contests; q2 = (~q1) & (pub.contests_per_month > 15); dq = q1 | q2
c = pub[~dq]
groups = {"attrition (cohort)": c[(c.status_proxy == "Stopped") & (c.months_since_last_submission >= 3.0) & (c.max_rating < 1500)],
          "active (cohort)": c[(c.status_proxy == "Active") & (c.max_rating < 1500)],
          "removed by the data-quality rule": pub[dq]}
rec = {}
for f in a.refetched:
    for line in open(f, encoding="utf-8"):
        try:
            o = json.loads(line)
            if o.get("status") == "ok" and o["submissions"]:
                t = [x["creationTimeSeconds"] for x in o["submissions"]]
                span = max((max(t) - min(t)) / (30 * 24 * 3600), 1)
                rec[o["handle"]] = (len(o["submissions"]), len(o["rating"]), len(o["rating"]) / span)
        except Exception:
            pass
out = {"T_obs_utc": datetime.fromtimestamp(T_OBS, timezone.utc).isoformat(), "groups": {}}
for g, d in groups.items():
    s = [(r.total_submissions, r.total_contests) + rec[r.real][:2] for r in d.itertuples() if r.real in rec]
    cpm_now = [rec[r.real][2] for r in d.itertuples() if r.real in rec]
    if not s: continue
    out["groups"][g] = {"accounts": len(d), "retrieved_again": len(s),
        "submissions_equal": sum(a_ == b_ for a_, _, b_, _ in s), "submissions_more_now": sum(b_ > a_ for a_, _, b_, _ in s),
        "submissions_fewer_now": sum(b_ < a_ for a_, _, b_, _ in s),
        "rated_contests_equal": sum(a_ == b_ for _, a_, _, b_ in s),
        "now_fewer_submissions_than_rated_contests": sum(b_ < c_ for _, _, b_, c_ in s),
        "now_more_than_15_rated_contests_per_month": sum(x > 15 for x in cpm_now),
        "now_failing_the_data_quality_rule": sum((b_ < c_) or (x > 15) for (_, _, b_, c_), x in zip(s, cpm_now))}
os.makedirs("results", exist_ok=True); json.dump(out, open("results/r5_b3_completeness.json", "w"), indent=1); print(json.dumps(out, indent=1))
