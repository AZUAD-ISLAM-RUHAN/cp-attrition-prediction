# Predicting Student Attrition in Competitive Programming

Data and code for:

> A. I. Ruhan, G. M. Naeem, R. I. Rafi, S. A. Mim, N. B. Opi, D. F. Chowdhury, and M. R. K. Sadi, "Predicting Student Attrition in Competitive Programming: A Large-Scale Study Integrating Survey Insights and Global Behavioral Logs," *AIUB Journal of Science and Engineering (AJSE)*, vol. 25, no. 2, pp. 231–243, 2026. DOI: [10.53799/vka5w161](https://doi.org/10.53799/vka5w161)

Public repository: https://github.com/AZUAD-ISLAM-RUHAN/cp-attrition-prediction

> **Status (6 November 2026).** The article is temporarily retracted while the AJSE Editorial Desk reviews it (inquiry of 3 November 2026). This repository holds everything needed to verify the corrected version submitted in response: the data, every script, and one command that regenerates every number, table and figure. The corrected manuscript itself is with the journal and is not posted here.

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

1. computes every statistic, test and model from the raw data (`scripts/revision/r3_inquiry_reanalysis.py`);
2. builds Table I and draws every figure;
3. rebuilds the corrected manuscript, clean and with tracked changes against the published article;
4. recomputes the key numbers independently from the raw files and checks that each appears in the documents;
5. runs 64 consistency tests: figures, tables, equations, references, headline numbers and conformance with the AJSE camera-ready template;
6. compares everything with the outputs that were submitted to the journal (`reference_outputs/`).

`bash reproduce_all.sh --docs` reuses the computed results and takes about a minute. `--fast` is a quick smoke test with fewer permutations. Step-by-step instructions are in [`README_REPRODUCE.md`](README_REPRODUCE.md).

## What the corrected analysis finds

| | Result |
|---|---|
| Codeforces cohort | 6,927 accounts released; 880 removed for incomplete submission histories; 1,816 users rating-matched (908 active, 908 true attrition, all peak rating < 1500) |
| Group differences | Users who withdrew entered fewer rated contests (median 0.89 vs. 1.15 per month) and solved fewer problems per month (5.35 vs. 8.80). All effects are small (rank-biserial \|r\| ≤ 0.28). |
| Prediction | Best repeated 5-fold CV ROC-AUC 0.622 (soft-voting ensemble); Random Forest 0.620, label-permutation p = 0.005. No model beats the F1 of the always-"attrition" baseline (0.667). |
| Survey | 96 responses, analysis set n = 64. The most frequent reason for stopping is stalled rating progress (12 of 51). The difference in self-rated mathematics ability (3.93 vs. 3.41) does not survive Holm correction. |

Every value above is read from `results/r3_results.json`, and no number in the paper is typed by hand.

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
results/              r3_results.json (every number, machine-readable), r3_report.md, r3_table1_cohort.json
figures/
  original/           the 17 original figure files (first submission and published article), unchanged
  revised/            the figures of the corrected manuscript
manuscript_build/     generators for the corrected manuscript and the response letter, and their inputs
reference_outputs/    the outputs behind the documents submitted to the journal, for comparison
docs/
  ETHICS_AND_DATA.md            ethics approval, consent, anonymisation, observation date
  DATA_DICTIONARY.md            every column, defined as implemented
  survey_instrument.md          the full questionnaire with its branching
  reference_verification.md     check of every reference against Crossref and publishers
  AJSE_template_conformance.md  layout checked against the AJSE camera-ready template
  Draft_Correction_Notice.txt   proposed correction notice
reproduce_all.sh      one-command rebuild and verification
```

## Data and privacy

- **Codeforces.** The data come from the public Codeforces API (`user.ratedList`, `user.info`, `user.status`, `user.rating`), collected in June 2026. Handles are replaced by a salted SHA-256 prefix; the salt and the raw API records, which contain handles, are not published, but are available to the editor on request. `scripts/revision/r0_rebuild_from_raw_jsonl.py` rebuilds every stage count from those records.
- **Survey.** An anonymous online questionnaire for students at universities in Bangladesh, collected 6 March – 2 April 2026 under approval of the Research Ethics Committee of Metropolitan University, Sylhet (REC/MU/2026/007; resolution of 24 February 2026). It recorded no names, student IDs, e-mail addresses or institutions. Exact submission times are removed as quasi-identifiers, and only the date of each response is published. The approval letter is supplied to the journal and is not posted here, because it contains a personal identifier.
- Details: [`docs/ETHICS_AND_DATA.md`](docs/ETHICS_AND_DATA.md).

## What changed in response to the editorial inquiry

1. **Descriptives recomputed on the matched cohort.** The matched models of the published Table III are reproduced by `r1`, but the descriptive section had been carried over from the unmatched first submission. Every descriptive statistic, test and proportion is now computed on the rating-matched cohort.
2. **Data-quality rule.** 888 accounts (880 after the peak-rating filter) had incomplete retrieved submission histories: fewer submissions than rated contests, or more than 15 rated contests per month. All were active accounts. They are excluded by an explicit rule, and the model is also reported without the rule.
3. **Consistent leakage audit.** Every feature whose value depends on the length or end of the observed window is removed. The Intensity Ratio is replaced by its window-invariant form, problems solved per rated contest (Spearman ρ = 0.99 with the original).
4. **Baselines and metrics.** Results are reported against always-"attrition" and random baselines, with ROC-AUC, balanced accuracy, per-fold SD, a 200-permutation label test and bootstrap confidence intervals.
5. **Survey items.** Only items worded comparably across the questionnaire branches enter between-group tests.
6. **Withdrawn.** The survey classifier and the Early Warning System are withdrawn, and the Skill-Application Paradox is stated as a hypothesis only.
7. **References.** All references are verified. The non-existent entries flagged by the Desk belong to the original submission list, still carried by the Crossref deposit and the arXiv preprint. Published entries [5], [9] and [10] are corrected.
8. **Ethics dates.** The REC resolution (24 Feb 2026) predates data collection (from 6 Mar 2026). The approval letter was issued on 17 Mar 2026.

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
