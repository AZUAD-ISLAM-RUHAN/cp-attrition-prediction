# Predicting Student Attrition in Competitive Programming

Data and code for:

> A. I. Ruhan, G. M. Naeem, R. I. Rafi, S. A. Mim, N. B. Opi, D. F. Chowdhury, and M. R. K. Sadi, "Predicting Student Attrition in Competitive Programming: A Large-Scale Study Integrating Survey Insights and Global Behavioral Logs," *AIUB Journal of Science and Engineering (AJSE)*, vol. 25, no. 2, pp. 231–243, 2026. DOI: [10.53799/vka5w161](https://doi.org/10.53799/vka5w161)

Public repository: https://github.com/AZUAD-ISLAM-RUHAN/cp-attrition-prediction

> **Status (13 November 2026).** The article is temporarily retracted while the AJSE Editorial Desk reviews it: an editorial inquiry of 3 November 2026 (answered on 6 November; that version is tagged `v2.0-reviewed`, DOI [10.5281/zenodo.24054465](https://doi.org/10.5281/zenodo.24054465)) and a reviewer report of 8 November 2026. This commit adds the analyses that answer the report (scripts `r4_*`, `results/r4_*`, `figures/v3/`). The survey is removed from the revised paper (the reviewer's preferred option), which reports a rating-restricted comparison of Codeforces activity. The revised manuscript and the response are with the journal and are not posted here; the manuscript generators will be added with release v3.0, when the paper is final, so that the release matches the paper exactly.
>
> **Archive of all versions:** [10.5281/zenodo.24054464](https://doi.org/10.5281/zenodo.24054464). The history of 19 September 2026 is in branch `history-2026-09`; see [`docs/REPOSITORY_HISTORY.md`](docs/REPOSITORY_HISTORY.md).

---

## Verify the paper in one command

```bash
git clone https://github.com/AZUAD-ISLAM-RUHAN/cp-attrition-prediction
cd cp-attrition-prediction
pip install -r requirements.txt     # Python 3.13, pinned versions
npm install                         # Node.js >= 18, for the manuscript build
bash reproduce_all.sh               # about 45 min on 2 CPU cores
```

The last line of a successful run is `RESULT: ALL OUTPUTS REPRODUCED`. The run:

1. computes every statistic, test and model from the raw data (`scripts/revision/r3_inquiry_reanalysis.py` for the 6 November version; `r4_check_reviewer_claims.py` and `r4_revision_analyses.py` for v3);
2. builds Table I and draws every figure;
3. rebuilds the 6 November manuscript (clean, and tracked against the published article); from release v3.0 also the revised v3 (clean, and tracked against 6 November);
4. recomputes the key numbers independently from the raw files and checks that each appears in the documents;
5. runs the consistency tests (64 for the 6 November version; 53 more for v3 from release v3.0): figures, tables, equations, references, headline numbers, the reviewer's requirements and the AJSE camera-ready template;
6. compares everything with the outputs that were submitted to the journal (`reference_outputs/`).

`bash reproduce_all.sh --docs` reuses the computed results and takes about a minute. `--fast` is a quick smoke test with fewer permutations. Step-by-step instructions are in [`README_REPRODUCE.md`](README_REPRODUCE.md).

## What the revised analysis (v3) finds

| | Result |
|---|---|
| Cohort | 6,927 accounts retrieved; 888 removed for incomplete submission histories (all active); both groups restricted to peak rating < 1500: **3,421 active and 908 labeled attrition** (no submission for at least 90 days). All eligible active accounts are used, so no random draw is involved. |
| Group differences | Small. Attrition accounts accept smaller shares of their attempts (math-tag r = -0.16, overall -0.13) and solve fewer problems per rated contest (median 5.95 vs. 7.80, r = -0.13). No measure used in the models exceeds \|r\| = 0.16. |
| Separability | Cross-validated ROC-AUC 0.596 [0.574, 0.617] (logistic regression) and 0.611 [0.590, 0.631] (random forest); Brier scores barely below the base rate. |
| Robustness | 50 balanced samples: RF mean 0.598; stricter cleaning rules about 0.60; inactivity of 3/6/12 months crossed with rating limits 1400/1500/1600: 0.59–0.66; matched on account age and contests: RF 0.579. |
| Not yet done | Reviewer item B1 (measures from the period before inactivity only) needs the raw API records, which are not public. |

The measures summarize each account's whole recorded history, so these results describe group differences; they do not show that inactivity can be predicted for individuals. Every value above is read from `results/r4_results.json`.

## Repository layout

```
data/
  cf_attrition_features.csv       6,927 Codeforces accounts (handles replaced by a salted hash), unchanged since 19 Sep 2026
  cf_matched_modelling_set.csv    rating-matched modelling cohort, n = 1,816 (written by r3)
  survey_responses.csv            96 anonymised survey responses, unchanged since 19 Sep 2026
  survey_analysis_set_n64.csv     survey analysis set, n = 64 (written by r3)
  survey_response_dates.csv       calendar date of each response (no time of day), to check the collection window
scripts/
  01_collect_and_build_features.ipynb     Codeforces API collection and feature building (original)
  02_cf_attrition_training.py             first-submission Codeforces models (kept unchanged)
  03_survey_analysis.ipynb                first-submission survey analysis (kept unchanged)
  revision/
    r0_rebuild_from_raw_jsonl.py          stage counts and completeness audit from the raw API records
    r1_rating_matching_and_leakage_audit.py   first-round revision (published Table III)
    r2_corrections_effect_sizes_oof_ews.py    first-round revision (survey)
    r3_inquiry_reanalysis.py              corrected analysis: produces every reported number
    r3_figures.py                         draws every figure from r3's outputs
    r3_table1_cohort.py                   stage-by-stage cohort counts (Table I)
    r3_export_survey_dates.py             date-only public file from the private timestamped sheet
    r4_check_reviewer_claims.py           tests every numerical claim of the reviewer report (8 Nov 2026)
    r4_revision_analyses.py               v3 analyses: cohort, effect sizes, models, robustness (items B2-B7)
    r4_figures.py                         the four v3 figures (every figure shows uncertainty)
results/              r3_*: 6 November version; r4_*: v3 (results, reviewer-claim checks, out-of-fold predictions, published vs. re-run test set)
figures/
  original/           the 17 original figure files (first submission and published article), unchanged
  revised/            the figures of the 6 November version
  v3/                 the figures of the revised v3
manuscript_build/     generators for the manuscripts and response letters, and their inputs
  v3/                 (added with release v3.0) revised paper, claim table, tests and build script
reference_outputs/    the outputs behind the documents submitted to the journal, for comparison
docs/
  ETHICS_AND_DATA.md            ethics approval, consent, anonymisation, observation date
  DATA_DICTIONARY.md            every column, defined as implemented
  survey_instrument.md          the full questionnaire with its branching
  reference_verification.md     check of every reference against Crossref and publishers (6 November version)
  reference_verification_v3.md  automatic Crossref/DataCite check of every v3 reference
  REPOSITORY_HISTORY.md         how to verify the September 2026 history (GitHub-signed commits)
  AJSE_template_conformance.md  layout checked against the AJSE camera-ready template
  Draft_Correction_Notice.txt   proposed correction notice
reproduce_all.sh      one-command rebuild and verification
```

## Data and privacy

- **Codeforces.** The data come from the public Codeforces API (`user.ratedList`, `user.info`, `user.status`, `user.rating`), collected in June 2026. Handles are replaced by a salted SHA-256 prefix; the salt and the raw API records, which contain handles, are not published, but are available to the editor on request. `scripts/revision/r0_rebuild_from_raw_jsonl.py` rebuilds every stage count from those records.
- **Survey.** An anonymous online questionnaire for students at universities in Bangladesh, collected 6 March – 2 April 2026 under the approval of the Research Ethics Committee of Metropolitan University, Sylhet (REC/MU/2026/007): the application was considered on 24 February 2026 and approved verbally, and the letter was issued on 17 March 2026; 84 of the 96 responses were submitted before the letter. It recorded no names, student IDs, e-mail addresses or institutions. Exact submission times are removed as quasi-identifiers, and only the date of each response is published. The approval letter is supplied to the journal and is not posted here, because it contains a personal identifier.
- Details: [`docs/ETHICS_AND_DATA.md`](docs/ETHICS_AND_DATA.md).

## What changed in response to the editorial inquiry

1. **Descriptives recomputed on the matched cohort.** The matched models of the published Table III are reproduced by `r1`, but the descriptive section had been carried over from the unmatched first submission. Every descriptive statistic, test and proportion is now computed on the rating-matched cohort.
2. **Data-quality rule.** 888 accounts (880 after the peak-rating filter) had incomplete retrieved submission histories: fewer submissions than rated contests, or more than 15 rated contests per month. All were active accounts. They are excluded by an explicit rule, and the model is also reported without the rule.
3. **Consistent leakage audit.** Every feature whose value depends on the length or end of the observed window is removed. The Intensity Ratio is replaced by its window-invariant form, problems solved per rated contest (Spearman ρ = 0.99 with the original).
4. **Baselines and metrics.** Results are reported against always-"attrition" and random baselines, with ROC-AUC, balanced accuracy, per-fold SD, a 200-permutation label test and bootstrap confidence intervals.
5. **Survey items.** Only items worded comparably across the questionnaire branches enter between-group tests.
6. **Withdrawn.** The survey classifier and the Early Warning System are withdrawn, and the Skill-Application Paradox is stated as a hypothesis only.
7. **References.** All references are verified. The non-existent entries flagged by the Desk belong to the original submission list, still carried by the Crossref deposit and the arXiv preprint. Published entries [5], [9] and [10] are corrected.
8. **Ethics dates.** The application was considered and approved verbally on 24 Feb 2026, before data collection began (6 Mar 2026); the approval letter was issued on 17 Mar 2026.

The first-submission and first-round scripts are kept unchanged, so every published number can be traced to the code that produced it.

## Reproducibility notes

- The random seed is 42 everywhere. Library versions are pinned in `requirements.txt` (scikit-learn 1.9.1, XGBoost 3.4.1, LightGBM 4.7.0, NumPy 2.5.3, pandas 3.0.5, SciPy 1.18.1), and two independent full runs gave identical results.
- Tree ensembles can differ in the third decimal under other library versions. Re-running the first-submission scripts with current versions reproduces six of the nine published classifier figures exactly; Random Forest, XGBoost and the ensemble differ by up to about 0.02.
- Figures use Arial. Where Arial is not installed, its metric twin Liberation Sans is used, so figure files are byte-identical only on systems with the same fonts. The numbers do not depend on fonts.

## Citation

See [`CITATION.cff`](CITATION.cff), or use the reference at the top of this page.

## Licence

Code: MIT (see [`LICENSE`](LICENSE)). Data: CC BY 4.0.

## Contact

Azuad Islam Ruhan (corresponding author), Department of Computer Science and Engineering, Metropolitan University, Sylhet, Bangladesh, ahnafruhan7@gmail.com
