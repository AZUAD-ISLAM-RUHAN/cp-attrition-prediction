"""
r0_rebuild_from_raw_jsonl.py
============================
Rebuilds the Codeforces cohort directly from the raw API dumps written by
01_collect_and_build_features.ipynb (users_info.jsonl, users_dynamic.jsonl,
handle_pool.txt), so that the editorial desk can verify every stage count.

It answers three questions the derived CSV cannot:
  (1) How many accounts were removed at EACH gate (pool -> fetched -> gate -> labels).
  (2) What the observation date T_obs was (the original notebook used datetime.now()
      at run time and did not record it). Here T_obs is a fixed, explicit argument.
  (3) Which accounts have an incomplete submission history (fewer submissions than
      rated contests, or rated contests before the earliest retrieved submission),
      and whether re-fetching them with pagination repairs the history.

It also writes a FIXED-WINDOW feature file: all features are computed only from
activity strictly before T_cut = T_obs - 3 months, for every account, and the label
is whether the account submitted anything in (T_cut, T_obs]. This removes the
window asymmetry between active and stopped accounts by construction.

Usage (from repository root; raw files are NOT redistributed, they stay with the authors
and are provided privately to the editorial desk):
    python scripts/revision/r0_rebuild_from_raw_jsonl.py \
        --raw-dir /path/to/cf_attrition_data --t-obs 2026-06-20T00:00:00Z \
        [--salt-file salt.txt]   # same salt as used for the released hashed handles
Outputs: results/r0_flow.json, results/r0_incomplete_histories.csv,
         data/cf_fixed_window_features.csv
"""
import argparse, json, os, statistics, hashlib
from datetime import datetime, timezone

MAX_RATING, MIN_CONTESTS, IDLE_MONTHS = 2400, 5, 3
MONTH = 30 * 24 * 3600
DS_TAGS = {"data structures", "trees", "graphs", "dsu"}
MATH_TAGS = {"math", "number theory", "combinatorics", "probabilities"}

def load_jsonl(path, key="handle"):
    out = {}
    with open(path) as f:
        for line in f:
            try:
                o = json.loads(line); out[o[key]] = o          # last record per handle wins (as in the notebook)
            except Exception:
                pass
    return out

def hashed(h, salt):
    return hashlib.sha256((salt + h).encode()).hexdigest()[:16] if salt is not None else h

def features(subs, rating, t_end):
    """Features from activity strictly before t_end. Returns None if not computable."""
    subs = [s for s in subs if s["creationTimeSeconds"] < t_end]
    rating = [c for c in rating if c["ratingUpdateTimeSeconds"] < t_end]
    acc = [s for s in subs if s.get("verdict") == "OK"]
    if len(rating) < MIN_CONTESTS or not subs or not acc:
        return None
    r = {"total_contests": len(rating), "total_submissions": len(subs)}
    r["acceptance_rate"] = len(acc) / len(subs)
    def tag_rate(tags):
        att = [s for s in subs if tags & set(s.get("problem", {}).get("tags", []))]
        return (sum(s.get("verdict") == "OK" for s in att) / len(att)) if att else None
    r["math_solve_rate"] = tag_rate(MATH_TAGS); r["ds_solve_rate"] = tag_rate(DS_TAGS)
    solved = {(s["problem"].get("contestId"), s["problem"].get("index")) for s in acc}
    r["total_problems_solved"] = len(solved)
    r["solved_per_contest"] = len(solved) / len(rating)
    attended = {c["contestId"] for c in rating}
    up = sum(1 for s in acc if s.get("author", {}).get("participantType") == "PRACTICE"
             and s["problem"].get("contestId") in attended)
    r["upsolves_per_contest"] = up / len(rating)
    first, ac = {}, {}
    for s in sorted(subs, key=lambda x: x["creationTimeSeconds"]):
        k = (s["problem"].get("contestId"), s["problem"].get("index"))
        first.setdefault(k, s["creationTimeSeconds"])
        if s.get("verdict") == "OK" and k not in ac: ac[k] = s["creationTimeSeconds"]
    st = [(ac[k] - first[k]) / 60 for k in ac]
    r["avg_struggle_minutes"] = statistics.mean(st) if st else 0.0
    r["median_struggle_minutes"] = statistics.median(st) if st else 0.0
    d = [c["newRating"] - c["oldRating"] for c in rating]
    drops = [d[i] for i in range(1, len(d)) if d[i - 1] < 0]
    r["post_drop_recovery"] = statistics.mean(drops) if drops else 0.0
    r["editorial_dependency_index"] = r["upsolves_per_contest"] * r["avg_struggle_minutes"]
    r["peak_rating_before_t_end"] = max(c["newRating"] for c in rating)
    return r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", required=True); ap.add_argument("--t-obs", required=True)
    ap.add_argument("--salt-file", default=None)
    a = ap.parse_args()
    t_obs = datetime.fromisoformat(a.t_obs.replace("Z", "+00:00")).timestamp()
    t_cut = t_obs - IDLE_MONTHS * MONTH
    salt = open(a.salt_file).read().strip() if a.salt_file else None
    pool = [h.strip() for h in open(os.path.join(a.raw_dir, "handle_pool.txt")) if h.strip()]
    info = {h: o["info"] for h, o in load_jsonl(os.path.join(a.raw_dir, "users_info.jsonl")).items()}
    dyn = load_jsonl(os.path.join(a.raw_dir, "users_dynamic.jsonl"))
    os.makedirs("results", exist_ok=True)

    flow = {"T_obs_utc": a.t_obs, "T_cut_utc": datetime.fromtimestamp(t_cut, timezone.utc).isoformat(),
            "pool": len(pool), "pool_with_user_info": sum(h in info for h in pool),
            "pool_with_dynamic_record": sum(h in dyn for h in pool)}
    gate = {"suspicious_empty_submissions": 0, "current_rating_not_in_1_2399": 0, "fewer_than_5_rated_contests": 0,
            "no_submission_or_no_accepted": 0, "passed_gate": 0}
    incomplete, rows = [], []
    for h in pool:
        if h not in dyn or h not in info: continue
        dd, inf = dyn[h], info[h]
        subs, rating = dd.get("submissions") or [], dd.get("rating") or []
        if dd.get("suspicious"): gate["suspicious_empty_submissions"] += 1; continue
        if not (0 < inf.get("rating", 0) < MAX_RATING): gate["current_rating_not_in_1_2399"] += 1; continue
        if len(rating) < MIN_CONTESTS: gate["fewer_than_5_rated_contests"] += 1; continue
        if not subs or not any(s.get("verdict") == "OK" for s in subs): gate["no_submission_or_no_accepted"] += 1; continue
        gate["passed_gate"] += 1
        first_sub = min(s["creationTimeSeconds"] for s in subs)
        first_contest = min(c["ratingUpdateTimeSeconds"] for c in rating)
        rated_before_first_sub = sum(c["ratingUpdateTimeSeconds"] < first_sub for c in rating)
        if len(subs) < len(rating) or rated_before_first_sub > 0:
            incomplete.append({"handle": hashed(h, salt), "n_submissions": len(subs), "n_rated": len(rating),
                               "rated_contests_before_first_retrieved_submission": rated_before_first_sub,
                               "hit_10000_cap": len(subs) >= 10000})
            continue
        f = features(subs, rating, t_cut)
        if f is None: continue
        f["handle"] = hashed(h, salt)
        f["label_stopped"] = int(not any(t_cut <= s["creationTimeSeconds"] < t_obs for s in subs))
        rows.append(f)
    flow["gate"] = gate
    flow["incomplete_submission_history_excluded"] = len(incomplete)
    flow["fixed_window_rows"] = len(rows)
    flow["fixed_window_stopped"] = sum(r["label_stopped"] for r in rows)
    flow["fixed_window_stopped_peak_lt1500"] = sum(r["label_stopped"] and r["peak_rating_before_t_end"] < 1500 for r in rows)
    flow["fixed_window_active_peak_lt1500"] = sum((not r["label_stopped"]) and r["peak_rating_before_t_end"] < 1500 for r in rows)
    json.dump(flow, open("results/r0_flow.json", "w"), indent=1)
    import csv
    if incomplete:
        with open("results/r0_incomplete_histories.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(incomplete[0])); w.writeheader(); w.writerows(incomplete)
    if rows:
        cols = sorted({k for r in rows for k in r})
        with open("data/cf_fixed_window_features.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(json.dumps(flow, indent=1))

if __name__ == "__main__":
    main()
