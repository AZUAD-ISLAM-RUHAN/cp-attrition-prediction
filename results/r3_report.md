# r3 re-analysis report

## CF-1 Cohort flow and data-quality checks

- rows_in_released_file: 6927
- note_collection_gate: Rows already passed the collection gate in 01_collect_and_build_features (current rating >0 and <2400, >=5 rated contests, >=1 accepted submission). Counts excluded by that gate are only recoverable from the raw JSONL files.
- peak_rating_ge_2400_in_file: 35
- current_rating_ge_2400_in_file: 0
- dq_q1_fewer_submissions_than_rated_contests: {'Active': 774, 'Stopped': 0}
- dq_q2_more_than_15_contests_per_month: {'Active': 114, 'Stopped': 0}
- max_contests_per_month_among_stopped: 9.0
- rows_after_data_quality: 6039
- all_rows: {'active': 5603, 'stopped': 1324, 'stopped_peak_lt1500_true_attrition': 908, 'stopped_peak_ge1500_intentional_exit_excluded': 416, 'active_peak_lt1500_matched_pool': 4047, 'active_peak_ge1500_excluded_by_matching': 1556}
- after_dq: {'active': 4715, 'stopped': 1324, 'stopped_peak_lt1500_true_attrition': 908, 'stopped_peak_ge1500_intentional_exit_excluded': 416, 'active_peak_lt1500_matched_pool': 3421, 'active_peak_ge1500_excluded_by_matching': 1294}

Primary cohort: n=1816 (908 active, 908 true attrition)
Correlation of implemented intensity_ratio with solved_per_contest in primary cohort: Spearman rho=0.989

## CF-2 Rating balance

- original_unmatched: {'active_peak_mean': 1331.225771, 'active_peak_median': 1282.0, 'attrition_peak_mean': 1149.498899, 'attrition_peak_median': 1154.0, 'standardised_mean_difference': 0.659715, 'ks_D': 0.281938, 'ks_p': 3.501128769219431e-32}
- primary_matched_clean: {'active_peak_mean': 1160.277533, 'active_peak_median': 1148.0, 'attrition_peak_mean': 1149.498899, 'attrition_peak_median': 1154.0, 'standardised_mean_difference': 0.055211, 'ks_D': 0.060573, 'ks_p': 0.07146137791504281}

## CF-3 Descriptive comparison (matched cohort)

| feature | active median [IQR] | attrition median [IQR] | median diff % | r_rb (attr>act) [95% CI] | p | p_Holm |
|---|---|---|---|---|---|---|
| contests_per_month | 1.15 [0.63, 2.03] | 0.89 [0.47, 1.57] | -22.6 | -0.178 [-0.227, -0.128] | <0.001 | <0.001 |
| problems_solved_per_month | 8.8 [4.51, 17.2] | 5.35 [2.56, 10.7] | -39.2 | -0.282 [-0.332, -0.232] | <0.001 | <0.001 |
| avg_struggle_minutes | 587 [47.9, 3.06e+03] | 424 [23.2, 3.01e+03] | -27.6 | -0.045 [-0.098, 0.004] | 0.095 | 0.191 |
| math_solve_rate | 0.499 [0.405, 0.584] | 0.464 [0.38, 0.55] | -7.1 | -0.131 [-0.185, -0.079] | <0.001 | <0.001 |
| ds_solve_rate | 0.427 [0.3, 0.556] | 0.397 [0.257, 0.5] | -7.0 | -0.099 [-0.152, -0.048] | <0.001 | 0.001 |
| acceptance_rate | 0.484 [0.404, 0.577] | 0.462 [0.382, 0.549] | -4.6 | -0.100 [-0.155, -0.046] | <0.001 | 0.001 |
| upsolves_per_contest | 0.269 [0.0612, 0.615] | 0.253 [0, 0.63] | -5.9 | -0.026 [-0.076, 0.024] | 0.334 | 0.334 |
| activity_trend_ratio | 0.86 [0.36, 2.01] | 0.6 [0.19, 1.66] | -30.2 | -0.145 [-0.198, -0.093] | <0.001 | <0.001 |
| post_drop_recovery | 1.4 [0, 19.5] | 0 [-2.35, 16.8] | -100.0 | -0.060 [-0.111, -0.006] | 0.026 | 0.077 |
| solved_per_contest | 8.21 [4.31, 13.8] | 5.95 [3.22, 10.9] | -27.5 | -0.168 [-0.219, -0.119] | <0.001 | <0.001 |
| account_age_months | 19 [10.2, 29.9] | 33.5 [22.1, 51] | 76.3 | 0.480 [0.433, 0.521] | <0.001 | <0.001 |

Same statistics on the ORIGINAL unmatched cohort (for the response letter only):
- contests_per_month: mean 7.273 vs 1.186; median 1.47 vs 0.89; r_rb=-0.322; p=<0.001
- problems_solved_per_month: mean 13.704 vs 7.857; median 9.34 vs 5.35; r_rb=-0.278; p=<0.001
- avg_struggle_minutes: mean 2645.720 vs 3058.970; median 308 vs 424; r_rb=0.061; p=0.025
- math_solve_rate: mean 0.538 vs 0.469; median 0.5 vs 0.464; r_rb=-0.213; p=<0.001
- ds_solve_rate: mean 0.480 vs 0.400; median 0.449 vs 0.397; r_rb=-0.189; p=<0.001
- acceptance_rate: mean 0.515 vs 0.464; median 0.498 vs 0.462; r_rb=-0.165; p=<0.001
- upsolves_per_contest: mean 0.439 vs 0.414; median 0.2 vs 0.253; r_rb=0.039; p=0.150
- activity_trend_ratio: mean 3.297 vs 3.909; median 0.935 vs 0.6; r_rb=-0.146; p=<0.001
- post_drop_recovery: mean 13.306 vs 5.963; median 7.9 vs 0; r_rb=-0.166; p=<0.001
- solved_per_contest: mean 9.933 vs 8.820; median 7.19 vs 5.95; r_rb=-0.016; p=0.548
- account_age_months: mean 28.251 vs 38.773; median 20.7 vs 33.5; r_rb=0.343; p=<0.001

Original headline values reproduced: {'contests_per_month_mean_active': 7.272786, 'contests_per_month_mean_attr': 1.186002, 'active_rows_failing_dq_in_original_sample': 148, 'contests_per_month_mean_active_excluding_dq_fail': 1.854855, 'struggle_mean_active': 2645.720485, 'struggle_mean_attr': 3058.969604, 'burnout_pct_active': 29.845815, 'burnout_pct_attr': 45.044053}

## CF-4 Activity-decay flag

Implemented definition: ATR = submissions in the second half of the user's own submission span / submissions in the first half; flag = ATR < 0.5. ATR is set to 1.0 when the first half is empty.
- primary_matched_clean: {'active_k': 297, 'active_n': 908, 'active_pct': 32.709251, 'active_ci': [29.736071, 35.828123], 'attr_k': 409, 'attr_n': 908, 'attr_pct': 45.044053, 'attr_ci': [41.83546, 48.294404], 'diff_pp': 12.334802, 'diff_ci_pp': [7.860159, 16.739865], 'chi2': 29.068606, 'p': 6.98599128687925e-08, 'relative_risk': 1.377104, 'atr_fallback_1.0_active': 9, 'atr_fallback_1.0_attr': 6}
- original_unmatched: {'active_k': 271, 'active_n': 908, 'active_pct': 29.845815, 'active_ci': [26.959454, 32.901996], 'attr_k': 409, 'attr_n': 908, 'attr_pct': 45.044053, 'attr_ci': [41.83546, 48.294404], 'diff_pp': 15.198238, 'diff_ci_pp': [10.767063, 19.545175], 'chi2': 44.769967, 'p': 2.215956710415858e-11, 'relative_risk': 1.509225, 'atr_fallback_1.0_active': 44, 'atr_fallback_1.0_attr': 6}
- upsolving bins: {'primary_matched_clean': {'active': {'zero_pct': 23.237885, 'lt_0.5_pct': 66.079295, '0.5_to_1_pct': 21.475771, '1_to_2_pct': 11.563877, 'ge_2_pct': 0.881057, 'mean_1to5': 3.017621}, 'attrition': {'zero_pct': 27.643172, 'lt_0.5_pct': 67.180617, '0.5_to_1_pct': 19.823789, '1_to_2_pct': 11.563877, 'ge_2_pct': 1.431718, 'mean_1to5': 2.935022}}, 'original_unmatched': {'active': {'zero_pct': 31.718062, 'lt_0.5_pct': 67.951542, '0.5_to_1_pct': 17.511013, '1_to_2_pct': 11.894273, 'ge_2_pct': 2.643172, 'mean_1to5': 2.814978}, 'attrition': {'zero_pct': 27.643172, 'lt_0.5_pct': 67.180617, '0.5_to_1_pct': 19.823789, '1_to_2_pct': 11.563877, 'ge_2_pct': 1.431718, 'mean_1to5': 2.935022}}}

## CF-5 Classifiers


### Spec B: matched + DQ, 12 original features (n=1816, 12 features)
| model | CV-F1 (train, 5-fold) | rep-CV F1 | rep-CV ROC-AUC | rep-CV bal.acc | test acc | test F1 | test recall | test AUC [95% CI] |
|---|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.681199 ± 0.024281 | 0.679438 ± 0.02768 | 0.755352 ± 0.02279 | 0.693699 ± 0.024165 | 0.703297 | 0.694915 | 0.675824 | 0.749789 [0.696304, 0.797834] |
| Decision Tree | 0.624468 ± 0.031033 | 0.634839 ± 0.024758 | 0.635661 ± 0.024555 | 0.635661 ± 0.024555 | 0.642857 | 0.661458 | 0.697802 | 0.642857 [0.594552, 0.69162] |
| Random Forest | 0.727521 ± 0.03136 | 0.734005 ± 0.022828 | 0.786012 ± 0.024368 | 0.725743 ± 0.022041 | 0.71978 | 0.731579 | 0.763736 | 0.775389 [0.726234, 0.821435] |
| KNN | 0.631847 ± 0.02638 | 0.646209 ± 0.024663 | 0.700114 ± 0.023502 | 0.649769 ± 0.023296 | 0.67033 | 0.673913 | 0.681319 | 0.708836 [0.660303, 0.757875] |
| SVM | 0.722359 ± 0.038112 | 0.712647 ± 0.029952 | 0.779915 ± 0.027004 | 0.708119 ± 0.029105 | 0.733516 | 0.738544 | 0.752747 | 0.776476 [0.727408, 0.823415] |
| XGBoost | 0.712379 ± 0.022383 | 0.714915 ± 0.022814 | 0.779938 ± 0.022153 | 0.709767 ± 0.024666 | 0.703297 | 0.71123 | 0.730769 | 0.76911 [0.720078, 0.814077] |
| LightGBM | 0.72943 ± 0.009133 | 0.716103 ± 0.01839 | 0.786296 ± 0.021802 | 0.712745 ± 0.018673 | 0.722527 | 0.730667 | 0.752747 | 0.787073 [0.738073, 0.83174] |
| MLP | 0.68884 ± 0.039716 | 0.714131 ± 0.032468 | 0.773071 ± 0.029248 | 0.710562 ± 0.030268 | 0.706044 | 0.71916 | 0.752747 | 0.777291 [0.727869, 0.82379] |
| Soft-Voting Ensemble | 0.738274 ± 0.025766 | 0.732917 ± 0.022819 | 0.796819 ± 0.024057 | 0.728381 ± 0.021938 | 0.733516 | 0.741333 | 0.763736 | 0.788975 [0.739406, 0.832792] |
| Baseline: always 'attrition' | 0.666666 ± 0.000966 | 0.666666 ± 0.001095 | 0.5 ± 0.0 | 0.5 ± 0.0 | 0.5 | 0.666667 | 1.0 | 0.5 |
| Baseline: random (stratified) | 0.499057 ± 0.022146 | 0.486437 ± 0.054224 | 0.488975 ± 0.046084 | 0.488975 ± 0.046084 | 0.456044 | 0.446927 | 0.43956 | 0.456044 |

### Spec C: matched + DQ, r1 audit (9 features) (n=1816, 9 features)
| model | CV-F1 (train, 5-fold) | rep-CV F1 | rep-CV ROC-AUC | rep-CV bal.acc | test acc | test F1 | test recall | test AUC [95% CI] |
|---|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.631611 ± 0.029899 | 0.631831 ± 0.020725 | 0.643642 ± 0.025183 | 0.595918 ± 0.022225 | 0.604396 | 0.632653 | 0.681319 | 0.653393 [0.596228, 0.707008] |
| Decision Tree | 0.54639 ± 0.024308 | 0.547917 ± 0.024787 | 0.546601 ± 0.025955 | 0.546601 ± 0.025955 | 0.532967 | 0.538043 | 0.543956 | 0.532967 [0.48323, 0.585145] |
| Random Forest | 0.613761 ± 0.022105 | 0.627338 ± 0.021279 | 0.65665 ± 0.026927 | 0.620018 ± 0.020856 | 0.604396 | 0.612903 | 0.626374 | 0.637031 [0.580804, 0.692809] |
| KNN | 0.572313 ± 0.021474 | 0.573164 ± 0.021935 | 0.59028 ± 0.025849 | 0.568472 ± 0.020269 | 0.57967 | 0.583106 | 0.587912 | 0.594478 [0.540621, 0.651125] |
| SVM | 0.634404 ± 0.015688 | 0.631522 ± 0.028504 | 0.647321 ± 0.031187 | 0.59966 ± 0.026997 | 0.596154 | 0.629723 | 0.686813 | 0.648427 [0.590988, 0.705482] |
| XGBoost | 0.612979 ± 0.023608 | 0.594001 ± 0.020729 | 0.628174 ± 0.029941 | 0.590163 ± 0.022853 | 0.557692 | 0.577428 | 0.604396 | 0.586523 [0.527251, 0.644151] |
| LightGBM | 0.61269 ± 0.025393 | 0.606224 ± 0.02354 | 0.634906 ± 0.026559 | 0.600727 ± 0.021972 | 0.565934 | 0.582011 | 0.604396 | 0.597392 [0.541207, 0.653048] |
| MLP | 0.621971 ± 0.025385 | 0.608817 ± 0.045926 | 0.625123 ± 0.031691 | 0.584653 ± 0.030486 | 0.587912 | 0.611399 | 0.648352 | 0.639114 [0.581981, 0.695165] |
| Soft-Voting Ensemble | 0.632215 ± 0.018967 | 0.62996 ± 0.022791 | 0.660049 ± 0.028218 | 0.619478 ± 0.023495 | 0.590659 | 0.598383 | 0.60989 | 0.635098 [0.577984, 0.689897] |
| Baseline: always 'attrition' | 0.666666 ± 0.000966 | 0.666666 ± 0.001095 | 0.5 ± 0.0 | 0.5 ± 0.0 | 0.5 | 0.666667 | 1.0 | 0.5 |
| Baseline: random (stratified) | 0.499057 ± 0.022146 | 0.486437 ± 0.054224 | 0.488975 ± 0.046084 | 0.488975 ± 0.046084 | 0.456044 | 0.446927 | 0.43956 | 0.456044 |

### Spec D: matched + DQ, consistent window audit (8 features) [PRIMARY] (n=1816, 8 features)
| model | CV-F1 (train, 5-fold) | rep-CV F1 | rep-CV ROC-AUC | rep-CV bal.acc | test acc | test F1 | test recall | test AUC [95% CI] |
|---|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.577812 ± 0.034487 | 0.566577 ± 0.031296 | 0.584997 ± 0.02771 | 0.553067 ± 0.029251 | 0.527473 | 0.549738 | 0.576923 | 0.564394 [0.503344, 0.625758] |
| Decision Tree | 0.558207 ± 0.016206 | 0.534034 ± 0.020621 | 0.532707 ± 0.018383 | 0.532707 ± 0.018383 | 0.524725 | 0.523416 | 0.521978 | 0.524725 [0.472324, 0.573355] |
| Random Forest | 0.609708 ± 0.010452 | 0.588126 ± 0.025534 | 0.620306 ± 0.023547 | 0.589061 ± 0.024846 | 0.571429 | 0.57377 | 0.576923 | 0.594071 [0.535163, 0.651413] |
| KNN | 0.544669 ± 0.0423 | 0.535791 ± 0.021454 | 0.555319 ± 0.023334 | 0.538312 ± 0.022794 | 0.57967 | 0.576177 | 0.571429 | 0.597361 [0.541852, 0.654048] |
| SVM | 0.579874 ± 0.030548 | 0.567208 ± 0.036486 | 0.591705 ± 0.031997 | 0.564289 ± 0.028044 | 0.535714 | 0.561039 | 0.593407 | 0.574931 [0.514564, 0.636025] |
| XGBoost | 0.597322 ± 0.023014 | 0.581865 ± 0.024764 | 0.605826 ± 0.025329 | 0.580592 ± 0.025172 | 0.549451 | 0.541899 | 0.532967 | 0.555096 [0.496799, 0.612145] |
| LightGBM | 0.605364 ± 0.035306 | 0.58177 ± 0.02796 | 0.604883 ± 0.025986 | 0.58126 ± 0.024829 | 0.538462 | 0.535912 | 0.532967 | 0.556213 [0.497633, 0.613763] |
| MLP | 0.541761 ± 0.049671 | 0.550895 ± 0.035286 | 0.574196 ± 0.031294 | 0.547821 ± 0.026255 | 0.524725 | 0.515406 | 0.505495 | 0.55102 [0.490558, 0.611587] |
| Soft-Voting Ensemble | 0.600285 ± 0.018273 | 0.5911 ± 0.025329 | 0.622053 ± 0.025686 | 0.589953 ± 0.025205 | 0.563187 | 0.552113 | 0.538462 | 0.572817 [0.511579, 0.631686] |
| Baseline: always 'attrition' | 0.666666 ± 0.000966 | 0.666666 ± 0.001095 | 0.5 ± 0.0 | 0.5 ± 0.0 | 0.5 | 0.666667 | 1.0 | 0.5 |
| Baseline: random (stratified) | 0.499057 ± 0.022146 | 0.486437 ± 0.054224 | 0.488975 ± 0.046084 | 0.488975 ± 0.046084 | 0.456044 | 0.446927 | 0.43956 | 0.456044 |

### Sensitivity: Spec D on matched cohort WITHOUT data-quality exclusion (n=1816, 8 features)
| model | CV-F1 (train, 5-fold) | rep-CV F1 | rep-CV ROC-AUC | rep-CV bal.acc | test acc | test F1 | test recall | test AUC [95% CI] |
|---|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.602819 ± 0.03201 | 0.597195 ± 0.028804 | 0.6196 ± 0.0244 | 0.581839 ± 0.025244 | 0.568681 | 0.600509 | 0.648352 | 0.584078 |
| Decision Tree | 0.589626 ± 0.022253 | 0.566499 ± 0.025952 | 0.565648 ± 0.024534 | 0.565648 ± 0.024534 | 0.521978 | 0.549223 | 0.582418 | 0.521978 |
| Random Forest | 0.654176 ± 0.035823 | 0.632387 ± 0.027087 | 0.663413 ± 0.028145 | 0.612428 ± 0.026267 | 0.601648 | 0.638404 | 0.703297 | 0.627294 |
| KNN | 0.574811 ± 0.030027 | 0.550994 ± 0.017214 | 0.578027 ± 0.019508 | 0.547361 ± 0.018401 | 0.535714 | 0.558747 | 0.587912 | 0.577044 |
| SVM | 0.605197 ± 0.034289 | 0.584421 ± 0.032834 | 0.615209 ± 0.028226 | 0.57855 ± 0.028707 | 0.557692 | 0.590331 | 0.637363 | 0.581995 |
| XGBoost | 0.626119 ± 0.019687 | 0.602723 ± 0.024741 | 0.640698 ± 0.026336 | 0.595146 ± 0.024445 | 0.568681 | 0.596401 | 0.637363 | 0.622751 |
| LightGBM | 0.616139 ± 0.028584 | 0.609357 ± 0.020286 | 0.6447 ± 0.027031 | 0.596808 ± 0.023703 | 0.563187 | 0.587013 | 0.620879 | 0.606358 |
| MLP | 0.594943 ± 0.026275 | 0.582252 ± 0.027349 | 0.60194 ± 0.027039 | 0.56786 ± 0.022643 | 0.53022 | 0.579853 | 0.648352 | 0.570432 |
| Soft-Voting Ensemble | 0.640861 ± 0.026178 | 0.623879 ± 0.024323 | 0.659189 ± 0.026904 | 0.612116 ± 0.024799 | 0.598901 | 0.631313 | 0.686813 | 0.62423 |
| Baseline: always 'attrition' | 0.666666 ± 0.000966 | 0.666666 ± 0.001095 | 0.5 ± 0.0 | 0.5 ± 0.0 | 0.5 | 0.666667 | 1.0 | 0.5 |
| Baseline: random (stratified) | 0.499057 ± 0.022146 | 0.486437 ± 0.054224 | 0.488975 ± 0.046084 | 0.488975 ± 0.046084 | 0.456044 | 0.446927 | 0.43956 | 0.456044 |

### Permutation tests (repeated-label shuffling, ROC-AUC, 5-fold CV on full primary cohort)
- Random Forest: AUC=0.623; null mean=0.503, null 95th pct=0.528; p=0.0050 (200 permutations)
- Logistic Regression: AUC=0.582; null mean=0.504, null 95th pct=0.529; p=0.0050 (200 permutations)

## CF-6 Feature importance (Spec D, Random Forest)

- solved_per_contest: impurity=0.167; permutation ΔAUC=0.066 ± 0.017
- math_solve_rate: impurity=0.138; permutation ΔAUC=0.029 ± 0.016
- avg_struggle_minutes: impurity=0.135; permutation ΔAUC=0.035 ± 0.014
- acceptance_rate: impurity=0.133; permutation ΔAUC=0.013 ± 0.012
- ds_solve_rate: impurity=0.119; permutation ΔAUC=-0.003 ± 0.008
- post_drop_recovery: impurity=0.116; permutation ΔAUC=0.022 ± 0.010
- editorial_dependency_index: impurity=0.098; permutation ΔAUC=0.016 ± 0.008
- upsolves_per_contest: impurity=0.094; permutation ΔAUC=0.006 ± 0.011

## SV-1 Survey sample flow

{'responses': 96, 'status_counts': {'Previously did CP, but stopped': 51, 'Never started CP': 23, 'Currently active in CP': 22}, 'excluded_never_started': 23, 'cp_experienced': 73, 'excluded_intentional_exit': 9, 'analysis_set': 64, 'active': 22, 'true_attrition': 42}
Reasons (n=51, single choice): Rating not increasing/no progress: 12 (23.529412%, 95% CI [14.004813, 36.762488]); Others: 9 (17.647059%, 95% CI [9.572296, 30.254405]); Interest in other tracks (Web Dev/ML): 9 (17.647059%, 95% CI [9.572296, 30.254405]); Lack of guidance or mentor: 8 (15.686275%, 95% CI [8.169126, 28.010708]); Academic pressure (CGPA focus): 7 (13.72549%, 95% CI [6.811015, 25.721952]); Mental stress or burnout: 6 (11.764706%, 95% CI [5.504999, 23.381102])

## SV-2 Item comparability

- prior_exp: {'active_item': 'Q3', 'stopped_item': 'Q3', 'note': 'common item, same wording for all respondents', 'decision': 'comparable'}
- dsa_grade: {'active_item': 'Q4', 'stopped_item': 'Q4', 'note': 'common item, same wording for all respondents', 'decision': 'comparable'}
- math_skill: {'active_item': 'Q5', 'stopped_item': 'Q5', 'note': 'common item, same wording for all respondents', 'decision': 'comparable'}
- ds_understanding: {'active_item': 'Q14', 'stopped_item': 'Q37', 'note': "parallel wording; stopped branch refers to 'when you quit'", 'decision': 'comparable with recall caveat'}
- mentor_support: {'active_item': 'Q22', 'stopped_item': 'Q35', 'note': 'parallel wording; present vs past tense', 'decision': 'comparable with recall caveat'}
- thought_quit: {'active_item': 'Q28', 'stopped_item': 'Q34', 'note': 'identical wording', 'decision': 'comparable with recall caveat'}
- upsolving_habit: {'active_item': 'Q11', 'stopped_item': 'Q33', 'note': 'different constructs: Q11 = post-contest upsolving frequency; Q33 = general practice habit in the month before quitting; original recoding Regular->Sometimes, Became irregular->Rarely, Stopped completely->Never', 'decision': 'NOT comparable - excluded from between-group inference'}
- long_break: {'active_item': 'Q27', 'stopped_item': 'Q36', 'note': 'different reference periods: Q27 = last 3 months; Q36 = whole CP journey', 'decision': 'NOT comparable - excluded from between-group inference'}
- friend_circle_cp: {'active_item': '-', 'stopped_item': 'Q39', 'note': 'asked of the stopped branch only; no active-branch item', 'decision': 'NOT comparable - excluded'}

## SV-3 Group tests on comparable items (n=64)

- math_skill: Welch t (Mann-Whitney U in note); stat=2.31, df=36.1, p=0.027, Holm=0.161, BH=0.161; Hedges-uncorrected d=0.65 [0.11, 1.21]; stopped mean 3.93 (n=42) vs active 3.41 (n=22); medians 4 vs 3
- ds_understanding: Welch t (Mann-Whitney U in note); stat=1.33, df=47.1, p=0.191, Holm=0.469, BH=0.230; Hedges-uncorrected d=0.34 [-0.13, 0.88]; stopped mean 3.52 (n=42) vs active 3.09 (n=22); medians 4 vs 3
- dsa_grade: Pearson chi-square (no continuity correction); exact p Monte-Carlo permutation; stat=5.96, df=3.0, p=0.112, Holm=0.469, BH=0.214; Cramer V=0.31 [0.14, 0.53]; table 4x2, n=64, min expected count=0.69
- prior_exp: Pearson chi-square (no continuity correction); exact p Fisher; stat=0.53, df=1.0, p=0.597, Holm=0.597, BH=0.597; Cramer V=0.09 [0.01, 0.34]; table 2x2, n=64, min expected count=9.62
- mentor_support: Pearson chi-square (no continuity correction); exact p Fisher; stat=3.15, df=1.0, p=0.094, Holm=0.469, BH=0.214; Cramer V=0.22 [0.01, 0.48]; table 2x2, n=64, min expected count=6.88
- thought_quit: Pearson chi-square (no continuity correction); exact p Fisher; stat=2.31, df=1.0, p=0.143, Holm=0.469, BH=0.214; Cramer V=0.19 [0.01, 0.43]; table 2x2, n=64, min expected count=5.50
Within-branch descriptives: {'Q11_upsolving_active_n22': {'Sometimes': 12, 'Always': 6, 'Rarely': 2, 'Never': 2}, 'Q33_practice_month_before_quitting_stopped_n51': {'Became irregular': 29, 'Regular': 12, 'Stopped completely': 10}, 'Q27_break_last3months_active_n22': {'Yes': 13, 'No': 9}, 'Q36_break_ever_stopped_n51': {'Yes': 37, 'No': 14}, 'Q39_friend_circle_stopped': {'1-2 people': 20, 'More than 5 people': 15, '3-5 people': 13}}

## SV-4 Survey classifier on comparable items only (n=64)


### Survey: 6 comparable items (n=64, 6 features)
| model | CV-F1 (train, 5-fold) | rep-CV F1 | rep-CV ROC-AUC | rep-CV bal.acc | test acc | test F1 | test recall | test AUC [95% CI] |
|---|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.708632 ± 0.166757 | 0.650964 ± 0.143565 | 0.630042 ± 0.173194 | 0.577389 ± 0.139979 | 0.538462 | 0.666667 | 0.666667 | 0.5 |
| Decision Tree | 0.654372 ± 0.098665 | 0.620031 ± 0.140941 | 0.492917 ± 0.133849 | 0.493667 ± 0.130334 | 0.538462 | 0.625 | 0.555556 | 0.555556 |
| Random Forest | 0.625714 ± 0.150211 | 0.606254 ± 0.142766 | 0.537042 ± 0.134529 | 0.477833 ± 0.097513 | 0.538462 | 0.666667 | 0.666667 | 0.555556 |
| KNN | 0.667308 ± 0.159465 | 0.756023 ± 0.060707 | 0.524028 ± 0.129057 | 0.517278 ± 0.083396 | 0.769231 | 0.842105 | 0.888889 | 0.5 |
| SVM | 0.695238 ± 0.192748 | 0.677917 ± 0.11526 | 0.553958 ± 0.12887 | 0.543111 ± 0.134275 | 0.538462 | 0.666667 | 0.666667 | 0.472222 |
| XGBoost | 0.612601 ± 0.220363 | 0.659616 ± 0.123616 | 0.531292 ± 0.131431 | 0.517 ± 0.081774 | 0.538462 | 0.625 | 0.555556 | 0.555556 |
| LightGBM | 0.451458 ± 0.311136 | 0.618787 ± 0.122494 | 0.5185 ± 0.144283 | 0.517278 ± 0.129038 | 0.615385 | 0.705882 | 0.666667 | 0.486111 |
| MLP | 0.784967 ± 0.033079 | 0.759307 ± 0.156983 | 0.496792 ± 0.17841 | 0.5 ± 0.0 | 0.692308 | 0.818182 | 1.0 | 0.416667 |
| Soft-Voting Ensemble | 0.661593 ± 0.19749 | 0.674607 ± 0.121084 | 0.586208 ± 0.141042 | 0.516722 ± 0.0918 | 0.538462 | 0.666667 | 0.666667 | 0.555556 |
| Baseline: always 'attrition' | 0.784967 ± 0.033079 | 0.792035 ± 0.025481 | 0.5 ± 0.0 | 0.5 ± 0.0 | 0.692308 | 0.818182 | 1.0 | 0.5 |
| Baseline: random (stratified) | 0.658242 ± 0.121982 | 0.571333 ± 0.108553 | 0.467222 ± 0.139504 | 0.467222 ± 0.139504 | 0.538462 | 0.625 | 0.555556 | 0.527778 |
Permutation test, LR on comparable items: AUC=0.650, null mean=0.504, p=0.0647
Input width after one-hot encoding of the 6 comparable items: 12

## SV-5 Reproducing the original statistics

- long_break_orig: {'chi2_missing_as_category_n73': 73.0, 'crosstab': {0: {'MISSING': 22, 'No': 0, 'Yes': 0}, 1: {'MISSING': 0, 'No': 14, 'Yes': 37}}}
- friend_circle_orig: {'chi2_missing_as_category_n73': 60.461176, 'crosstab': {0: {'1-2 people': 0, '3-5 people': 0, 'MISSING': 22, 'More than 5 people': 0}, 1: {'1-2 people': 20, '3-5 people': 13, 'MISSING': 3, 'More than 5 people': 15}}}
- upsolving_n73: 27.700487
- upsolving_n64_r2: {'chi2': 23.178185, 'crosstab': {0: {'Always': 6, 'Never': 2, 'Rarely': 2, 'Sometimes': 12}, 1: {'Always': 0, 'Never': 9, 'Rarely': 22, 'Sometimes': 11}}}
- long_break_paired_n64_r2: {'chi2_yates': 0.106063, 'chi2_pearson': 0.359909}
- mentor_support_n64: {'chi2_yates': 2.221488, 'chi2_pearson': 3.148367}
- thought_quit_n64: {'chi2_yates': 1.477633, 'chi2_pearson': 2.308802}
- prior_exp_n64: {'chi2_yates': 0.215488, 'chi2_pearson': 0.532124}

Wrote data/cf_matched_modelling_set.csv and data/survey_analysis_set_n64.csv