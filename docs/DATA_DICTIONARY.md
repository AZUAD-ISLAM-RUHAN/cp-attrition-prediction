# Data dictionary

All definitions below are taken from the code that produced the column: `scripts/01_collect_and_build_features.ipynb` (cell 5), and for the derived columns `scripts/revision/r3_inquiry_reanalysis.py`. Times come from Codeforces API `creationTimeSeconds` and `ratingUpdateTimeSeconds`. One month is 30 days.

## data/cf_attrition_features.csv (6,927 rows, one per account)

| Column | Definition as implemented | Notes |
|---|---|---|
| handle | Salted SHA-256 prefix of the Codeforces handle | Mapping not distributed |
| current_rating | `user.info` rating at collection | Collection gate: 0 < rating < 2400 |
| max_rating | `user.info` maxRating (peak rating) | Used for labels and matching; never a model feature |
| account_age_months | (T_obs − registration time) / 30 days | Includes idle time for inactive accounts, so window-dependent |
| total_contests | Number of rated contests (`user.rating` entries) | Collection gate: ≥ 5 |
| total_submissions | Number of retrieved submissions (`user.status`, count = 10,000) | Fewer than total_contests means an incomplete history |
| total_problems_solved | Distinct (contestId, index) with at least one OK verdict | |
| acceptance_rate | OK submissions / all submissions | |
| math_solve_rate | OK / attempted submissions on problems tagged math, number theory, combinatorics or probabilities | Falls back to acceptance_rate if no such attempts |
| ds_solve_rate | Same, for tags data structures, trees, graphs, dsu | Same fallback |
| problems_solved_per_month | total_problems_solved / span, where span = months between first and last retrieved submission (minimum 1) | Window-dependent |
| contests_per_month | total_contests / span (same span) | Window-dependent; > 15 indicates a truncated history |
| upsolves_per_contest | OK submissions with participantType = PRACTICE on contests the user was rated in, / total_contests | |
| avg_struggle_minutes | Mean over solved problems of (first OK time − first attempt time), in minutes | Heavy-tailed |
| rating_volatility | Population SD of rating changes | |
| post_drop_recovery | Mean rating change in the contest immediately following a negative rating change | |
| activity_trend_ratio (ATR) | Submissions in the second half of the user's own span / submissions in the first half; 1.0 if the first half is empty | Not a calendar window |
| burnout_flag | 1 if ATR < 0.5 | Called "activity decay" in the corrected paper |
| months_since_last_submission | (T_obs − last submission) / 30 days | Defines the label; never a feature |
| status_proxy | "Stopped" if months_since_last_submission ≥ 3, else "Active" | Measured at T_obs |
| *_1to5 | Percentile bins (quintiles over all 6,927 rows) of math, ds, upsolves, struggle (reversed), rating_volatility and ATR | Used only in descriptive charts of the first submission |

Derived in r3 (modelling set only): `intensity_ratio` = problems_solved_per_month / (contests_per_month + 0.1); `editorial_dependency_index` = upsolves_per_contest × avg_struggle_minutes; `solved_per_contest` = total_problems_solved / total_contests; `label` = 1 for true attrition, 0 for active.

## data/cf_matched_modelling_set.csv (1,816 rows)
The rating-matched modelling cohort exactly as analysed. It contains 908 true-attrition accounts (Stopped, max_rating < 1500) and 908 Active accounts with max_rating < 1500, drawn with `random_state = 42` after the data-quality rule. Columns: handle, label, status_proxy, max_rating, current_rating, totals, months_since_last_submission, burnout_flag, and every feature of Specifications B, C and D.

## data/survey_responses.csv (96 rows, 49 columns)
The Google Forms response sheet with the Timestamp column removed. Column headers are the item texts Q1–Q49 (see `survey_instrument.md`). Branch columns are empty for respondents routed elsewhere.

## data/survey_response_dates.csv (96 rows)
`row` (1–96, same order as survey_responses.csv) and `response_date` (calendar date of submission, YYYY-MM-DD; time of day removed). Written by `scripts/revision/r3_export_survey_dates.py` from the private original.

## data/survey_analysis_set_n64.csv (64 rows)
`label` (1 = stopped, true attrition; 0 = currently active), `math_skill` (Q5), `ds_understanding` (Q14 or Q37), `dsa_grade` (Q4), `prior_exp` (Q3), `mentor_support` (Q22 or Q35), `thought_quit` (Q28 or Q34).
