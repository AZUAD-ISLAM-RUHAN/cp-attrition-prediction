# Reproduce the whole paper from scratch

This folder is enough to rebuild **every component** of AJSE Paper 1999 from the raw data, even if everything else is lost. The components are: every statistic, test and model; Table I; every figure; the corrected manuscript in two versions (clean, and with tracked changes against the published article); and the response letter. The run then checks its own output.

## 1. Install (once)

| Need | Version used | Install |
|---|---|---|
| Python | 3.13 | python.org |
| Python packages | pinned in `requirements.txt` | `pip install -r requirements.txt` |
| Node.js | 18 or later (22 used) | nodejs.org |
| Node package `docx` | 9.8.1 (pinned in `package.json`) | `npm install` |
| pandoc | 3.x (3.1.3 used) | pandoc.org (used by the checks) |
| LibreOffice | any recent | optional, only for PDF export |

## 2. Run (one command)

```bash
bash reproduce_all.sh          # full run, about 45 minutes on 2 CPU cores
bash reproduce_all.sh --docs   # documents only, re-using results/ (about 1 minute)
bash reproduce_all.sh --fast   # quick smoke test (fewer permutations, so slightly different numbers)
```

On Windows, run it in Git Bash or WSL, or run the commands in the steps below one by one.

## 3. What each step does

| Step | Command | Reads | Writes |
|---|---|---|---|
| 1 | `python scripts/revision/r3_inquiry_reanalysis.py` | `data/cf_attrition_features.csv`, `data/survey_responses.csv` | `results/r3_results.json`, `results/r3_report.md`, `data/cf_matched_modelling_set.csv`, `data/survey_analysis_set_n64.csv` |
| 2 | `python scripts/revision/r3_table1_cohort.py` | feature file | `results/r3_table1_cohort.json` |
| 3 | `python scripts/revision/r3_figures.py` | results and analysis sets | `figures/revised/*.png` |
| 4 | `python manuscript_build/content_pub.py`, then `diff_prep.py` | published text (`manuscript_build/inputs/`), results | `manuscript_build/output/content_pub.json` |
| 4 | `node manuscript_build/render_pub.js clean\|tracked <out.docx>` | content JSON, figures, author photos | corrected manuscript, clean and tracked |
| 5 | `python manuscript_build/response_pub.py` | results | response letter (.txt) |
| 7 | `python manuscript_build/independent_check_pub.py` | raw files and documents | recomputes key numbers without r3 code and checks they appear in the documents |
| 7c | `r4_check_reviewer_claims.py`, `r4_revision_analyses.py` (full run only), `r4_figures.py`; from release v3.0 also `bash manuscript_build/v3/build_v3.sh` | data, results | reviewer-claim checks, v3 results and figures; from v3.0 the revised manuscript v3 (clean; tracked against 6 Nov), claim table and 53 tests (`verify_v3.py`) |
| 7b | `python manuscript_build/verify_manuscript_consistency.py` | documents, results, figures | 64 tests: figures, tables, equations, references, headline numbers, AJSE template conformance (T7) |
| 8 | `python manuscript_build/verify_against_reference.py` | `reference_outputs/` | checks that the new run matches the submitted outputs (numbers to 3 decimals; document text exact) |

The last line of a successful run is `RESULT: ALL OUTPUTS REPRODUCED`.

## 4. Folder map

```
data/                         raw feature file + public survey copy (+ analysis sets written by step 1)
data/PRIVATE/                 timestamped survey sheet (never publish; the timestamp check is skipped if absent)
scripts/01_...ipynb           Codeforces API collection and feature building (original, run on Colab)
scripts/02_..., 03_...        first-submission analyses (kept unchanged for traceability)
scripts/revision/r1, r2       first-round revision (produce the published Tables III-IV)
scripts/revision/r0           rebuild of stage counts from the RAW API records (T_obs, completeness audit)
scripts/revision/r3*          inquiry re-analysis: produces every number of the corrected paper
manuscript_build/             generators for the corrected manuscript and the response letter
manuscript_build/inputs/      published camera-ready (docx), its text and tables as JSON, survey instrument, author photos
reference_outputs/            the outputs behind the submitted documents, used for verification
results/, figures/            outputs (figures/original = as printed in the published article)
docs/                         ethics record, data dictionary, survey instrument, reference verification, AJSE template conformance
```

## 5. Starting from the raw Codeforces records

`data/cf_attrition_features.csv` is the feature file built in June 2026. To rebuild it, or to audit it, from the raw API records (`users_info.jsonl`, `users_dynamic.jsonl`, `handle_pool.txt`, kept privately), run:

```bash
python scripts/revision/r0_rebuild_from_raw_jsonl.py --raw-dir <folder> --t-obs <UTC timestamp>
```

If the raw records are lost, `scripts/01_collect_and_build_features.ipynb` re-collects them from the public Codeforces API. Live data change over time, so truncate every history at the original T_obs.

## 6. Reproducibility notes

- Seed 42 everywhere. With the pinned versions, two independent full runs produced identical results.
- Tree ensembles (Random Forest, XGBoost and the voting ensemble) can differ in the third decimal under other library versions. The published Tables III-IV came from earlier versions, as documented in `reference_outputs/` and the response letter.
- No placeholders remain. The public repository is https://github.com/AZUAD-ISLAM-RUHAN/cp-attrition-prediction.
