# Published values vs. re-execution of the deposited scripts (4 Nov 2026)

Re-executed with the pinned environment (scikit-learn 1.9.1, xgboost 3.4.1, lightgbm 4.7.0). Differences of a few thousandths in tree ensembles come from library-version changes in their random number streams, not from the data.

## Published Table III (Codeforces) vs r1 re-run

| Classifier | (A) pub | (A) rerun | (B) pub | (B) rerun | (C) pub | (C) rerun | (C) SD pub | (C) SD rerun |
|----------------------|------|------|------|------|------|------|------|------|
| Logistic Regression | 0.704 | 0.704 | 0.716 | 0.716 | 0.639 | 0.639 | 0.037 | 0.037 |
| Decision Tree | 0.621 | 0.621 | 0.655 | 0.655 | 0.568 | 0.567 | 0.043 | 0.044 |
| Random Forest | 0.731 | 0.732 | 0.775 | 0.767 | 0.682 | 0.686 | 0.011 | 0.012 |
| KNN | 0.667 | 0.667 | 0.676 | 0.676 | 0.589 | 0.589 | 0.012 | 0.012 |
| SVM | 0.732 | 0.732 | 0.743 | 0.743 | 0.652 | 0.652 | 0.022 | 0.022 |
| XGBoost | 0.726 | 0.726 | 0.755 | 0.755 | 0.652 | 0.652 | 0.027 | 0.027 |
| LightGBM | 0.736 | 0.736 | 0.751 | 0.751 | 0.645 | 0.645 | 0.024 | 0.024 |
| MLP | 0.712 | 0.712 | 0.720 | 0.720 | 0.608 | 0.608 | 0.026 | 0.026 |
| Soft-Voting Ensemble | 0.737 | 0.740 | 0.767 | 0.765 | 0.679 | 0.679 | 0.013 | 0.019 |

Identical to three decimals: column (B) 7/9, column (C) 7/9. Largest difference: 0.008 (B), 0.004 (C).

## Published Table IV (survey) vs r2 re-run

| Classifier | CV F1 pub | rerun | SD pub | rerun |
|----------------------|------|------|------|------|
| Logistic Regression | 0.833 | 0.833 | 0.036 | 0.036 |
| Random Forest | 0.832 | 0.845 | 0.082 | 0.060 |
| Soft-Voting Ensemble | 0.805 | 0.800 | 0.046 | 0.045 |
| KNN | 0.798 | 0.798 | 0.048 | 0.048 |
| Decision Tree | 0.772 | 0.761 | 0.100 | 0.091 |
| XGBoost | 0.753 | 0.753 | 0.073 | 0.073 |
| SVM | 0.750 | 0.750 | 0.069 | 0.069 |
| MLP | 0.729 | 0.729 | 0.120 | 0.120 |
| LightGBM | 0.651 | 0.651 | 0.098 | 0.098 |

## Published Table I vs data

6,927 -> 6,892 (peak < 2400) -> 5,573 active / 1,319 inactive -> 908 true attrition / 411 intentional exits; matching pool 4,047. All reproduced exactly (scripts/revision/r3_table1_cohort.py, without the new data-quality step).

## Published Early Warning System

Published: 6 high / 10 medium / 6 low. Re-run of r2: High=5 (23%)  Medium=8 (36%)  Low=9. The tiers are unstable across library versions, which is one reason the EWS is withdrawn.