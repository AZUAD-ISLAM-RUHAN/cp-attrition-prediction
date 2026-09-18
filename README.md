# Predicting Student Attrition in Competitive Programming

Data and code for the paper *Predicting Student Attrition in Competitive Programming: A Study Integrating Survey Insights and Global Behavioral Logs*, submitted to the AIUB Journal of Science and Engineering.

---

## Layout

```
data/
  cf_attrition_features.csv     6,927 Codeforces profiles (handles hashed)
  survey_responses.csv          96 survey responses (timestamps removed)

scripts/
  01_collect_and_build_features.ipynb   Codeforces API collection, feature building,
                                        1-5 percentile normalisation
  02_cf_attrition_training.py           Codeforces models, trend charts
  03_survey_analysis.ipynb              survey models, feature importance,
                                        Early Warning System

scripts/revision/
  r1_rating_matching_and_leakage_audit.py
  r2_corrections_effect_sizes_oof_ews.py

figures/                        figures as they appear in the manuscript
docs/                           reference verification notes
```

---

## Pipeline

**`01_collect_and_build_features.ipynb`** queries the public Codeforces API, engineers the behavioural proxies, and normalises six of them onto a 1–5 ordinal scale by percentile binning. It writes `cf_attrition_features.csv`. Running it end to end takes several hours; the resulting CSV is already in `data/`, so this step is only needed to rebuild the dataset from scratch.

**`02_cf_attrition_training.py`** labels true attrition as inactive accounts with peak rating below 1500, excludes intentional exits at 1500 or above, balances the two classes 1:1 by random undersampling, adds the Intensity Ratio and Editorial Dependency Index, and trains nine classifiers. Reports the Soft-Voting Ensemble at CV F1 = 0.737.

**`03_survey_analysis.ipynb`** runs the survey pipeline: group comparison, nine classifiers, feature importance and the Early Warning System. Reports Random Forest at CV F1 = 0.924.

Those two figures are the ones in the first submission.

---

## Revision scripts

Reviewers raised two problems with the specification above. These scripts implement the fixes, and **the numbers in the current manuscript come from here**.

```bash
pip install -r requirements.txt
python scripts/revision/r1_rating_matching_and_leakage_audit.py
python scripts/revision/r2_corrections_effect_sizes_oof_ews.py
```

**`r1`** — the Codeforces layer. The attrition class is capped at peak rating 1500 by construction while the original active class was not, so a classifier could separate the groups partly by inferring skill rather than disengagement. This script restricts the active pool to accounts that also peaked below 1500, then removes `account_age_months`, `contests_per_month` and `activity_trend_ratio`, all of which carry information about *when* a user stopped rather than the behaviour preceding it. Three specifications are reported side by side:

| Spec | Cohort | Features | Best model |
|---|---|---|---|
| A | unmatched | 12 | Soft-Voting 0.737 |
| B | rating-matched | 12 | Random Forest 0.775 |
| C | rating-matched, audited | 9 | **Random Forest 0.682** |

Specification C is what the paper reports. The Intensity Ratio becomes the highest-ranked feature under C.

**`r2`** — the survey layer. The questionnaire branches on Q6, so two features had been drawn from the stopped branch alone: break history from Q36 without pairing it to the active-branch Q27, and peer circle density from Q39, for which no active-branch item exists. In both cases every active respondent was missing and every stopped respondent was present, so a chi-square test recovered the branching structure rather than any behavioural difference. This script pairs Q27 with Q36, drops peer circle density, restricts to the n = 64 modelling set, adds Cohen's *d* and Cramér's *V* with bootstrapped confidence intervals, applies Bonferroni and Benjamini-Hochberg corrections across the eight tests, and scores the Early Warning System out of fold.

Survey Random Forest falls from 0.924 to 0.832. The EWS distribution changes from 4/6/12 to 6/10/6.

---

## Reproducing the reported results

```bash
pip install -r requirements.txt
python scripts/revision/r1_rating_matching_and_leakage_audit.py   # Table III
python scripts/revision/r2_corrections_effect_sizes_oof_ews.py    # Tables II and IV, EWS
```

Random seed is 42 throughout. Both scripts read from `data/`.

---

## Data notes

Codeforces handles are replaced by a salted SHA-256 prefix; the mapping is not distributed. Raw submission histories are not redistributed but remain retrievable from the public API using `01_collect_and_build_features.ipynb`.

Survey responses are anonymous at source. The questionnaire collected no names, student identifiers, email addresses or institution names. Submission timestamps have been removed from the published file as a quasi-identifier.

The study was approved by the Research Ethics Committee of the authors' institution on 17 March 2026.

---

## Licence

Code under the MIT Licence. Data under CC BY 4.0.
