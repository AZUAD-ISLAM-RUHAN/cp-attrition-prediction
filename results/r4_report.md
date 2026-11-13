# r4 revision analyses (reviewer report of 8 Nov 2026)

## B0 Cohort

Primary cohort: 4329 accounts = 3421 active + 908 attrition (peak < 1500, after the data-quality rule)
- peak rating: {'active_median': 1153.0, 'attrition_median': 1154.0, 'active_mean': 1158.272143, 'attrition_mean': 1149.498899, 'smd': 0.045008, 'ks_D': 0.051207, 'ks_p': 0.04455803420070484}

## B7 Primary models (all eligible accounts, repeated 5-fold CV)

- LR: {'auc_oof': 0.595903, 'auc_ci95': [0.57426, 0.616724], 'auc_fold_mean': 0.596496, 'auc_fold_sd': 0.023648, 'auc_fold_p2_5': 0.558452, 'auc_fold_p97_5': 0.638171, 'pr_auc': 0.285947, 'pr_auc_ci95': [0.262939, 0.313324], 'pr_auc_baseline': 0.209748, 'brier': 0.162538, 'brier_baseline': 0.165754, 'balanced_accuracy_at_base_rate': 0.56212, 'note': 'out-of-fold metrics computed per repeat and averaged over repeats; CI = bootstrap bounds averaged over repeats', 'calibration_repeat1': {'mean_predicted': [0.1106, 0.151, 0.1705, 0.1867, 0.2016, 0.2148, 0.2293, 0.2461, 0.2675, 0.3178], 'observed': [0.1547, 0.1409, 0.1732, 0.164, 0.1894, 0.2106, 0.2263, 0.2148, 0.2587, 0.3649]}}
- RF: {'auc_oof': 0.611325, 'auc_ci95': [0.590256, 0.630915], 'auc_fold_mean': 0.611503, 'auc_fold_sd': 0.01946, 'auc_fold_p2_5': 0.571452, 'auc_fold_p97_5': 0.644848, 'pr_auc': 0.294638, 'pr_auc_ci95': [0.269401, 0.322015], 'pr_auc_baseline': 0.209748, 'brier': 0.163528, 'brier_baseline': 0.165754, 'balanced_accuracy_at_base_rate': 0.564034, 'note': 'out-of-fold metrics computed per repeat and averaged over repeats; CI = bootstrap bounds averaged over repeats', 'calibration_repeat1': {'mean_predicted': [0.0654, 0.1077, 0.1377, 0.1645, 0.1923, 0.2219, 0.2547, 0.2909, 0.3425, 0.4506], 'observed': [0.1214, 0.1351, 0.1482, 0.1561, 0.2084, 0.21, 0.2306, 0.2565, 0.2899, 0.3565]}}
- class-weight check: {'auc_without_weights_1rep': 0.621468, 'auc_with_balanced_weights_1rep': 0.614724}  [135s]

## Descriptives (all eligible accounts; r > 0: higher in the attrition group)

- Math-tag acceptance rate: active 0.500 vs attrition 0.464; r = -0.161 [-0.201942, -0.116389]; p 8.8e-14, Holm 8.8e-13
- Data-structure acceptance rate: active 0.436 vs attrition 0.397; r = -0.123 [-0.163793, -0.08118]; p 1.2e-08, Holm 8.2e-08
- Overall acceptance rate: active 0.490 vs attrition 0.462; r = -0.133 [-0.171559, -0.089726]; p 6.2e-10, Holm 5.6e-09
- Struggle time (min): active 469.200 vs attrition 424.500; r = -0.013 [-0.054535, 0.029383]; p 0.54, Holm 1
- Upsolves per contest: active 0.250 vs attrition 0.253; r = 0.013 [-0.028784, 0.056652]; p 0.54, Holm 1
- Post-drop recovery: active 1.300 vs attrition 0.000; r = -0.054 [-0.094025, -0.011749]; p 0.011, Holm 0.055
- Editorial dependency index: active 82.562 vs attrition 73.918; r = -0.002 [-0.043044, 0.040446]; p 0.92, Holm 1
- Problems solved per contest: active 7.800 vs attrition 5.954; r = -0.131 [-0.17338, -0.090897]; p 1.3e-09, Holm 1e-08
- Rated contests per month: active 1.130 vs attrition 0.890; r = -0.169 [-0.208812, -0.130101]; p 3.8e-15, Holm 4.1e-14
- Problems solved per month: active 8.690 vs attrition 5.350; r = -0.258 [-0.295592, -0.21733]; p 5.8e-33, Holm 7e-32
- Account age (months): active 18.700 vs attrition 33.500; r = 0.475 [0.437744, 0.509158]; p 8.4e-108, Holm 1.1e-106
- Rated contests (total): active 13.000 vs attrition 13.000; r = 0.010 [-0.031033, 0.053826]; p 0.63, Holm 1
- Submissions per contest: active 17.200 vs attrition 14.155; r = -0.095 [-0.137873, -0.051749]; p 1e-05, Holm 6e-05

## B2 Balanced resamples (50 random draws of 908 actives)

- {'LR': {'mean': 0.592598, 'sd': 0.008414, 'min': 0.576099, 'max': 0.611964, 'p2_5': 0.578355, 'p97_5': 0.609938, 'seed42': 0.582371, 'seed42_rank_from_top': 46}, 'RF': {'mean': 0.59753, 'sd': 0.014374, 'min': 0.546992, 'max': 0.630918, 'p2_5': 0.5687, 'p97_5': 0.627179, 'seed42': 0.629714, 'seed42_rank_from_top': 2}}  [254s]

## B3 Incomplete histories and stricter rules

- R0: published rule (subs >= contests; <= 15 contests/month): {'n': 4329, 'active': 3421, 'attrition': 908, 'rf_auc': 0.616998, 'rf_auc_sd': 0.015341, 'lr_auc': 0.596791, 'lr_auc_sd': 0.031518}
- R1: R0 + at least 2 submissions per contest: {'n': 4208, 'active': 3304, 'attrition': 904, 'rf_auc': 0.596973, 'rf_auc_sd': 0.022498, 'lr_auc': 0.596569, 'lr_auc_sd': 0.012293}
- R2: R0 + at least 3 submissions per contest: {'n': 4118, 'active': 3226, 'attrition': 892, 'rf_auc': 0.599134, 'rf_auc_sd': 0.016097, 'lr_auc': 0.597496, 'lr_auc_sd': 0.021559}
- R3: R0 + at least 5 submissions per contest: {'n': 3882, 'active': 3059, 'attrition': 823, 'rf_auc': 0.606023, 'rf_auc_sd': 0.021591, 'lr_auc': 0.597101, 'lr_auc_sd': 0.029554}
[281s]

## B4 Definitions of attrition (inactivity x rating cut-off)

- {'rating_cut': 1400, 'inactive_months_min': 3.0, 'active': 2947, 'attrition': 777, 'rf_auc': 0.609314, 'rf_auc_sd': 0.01673, 'lr_auc': 0.591787, 'lr_auc_sd': 0.017725, 'r_solved_per_contest': -0.130271}
- {'rating_cut': 1400, 'inactive_months_min': 6.0, 'active': 2947, 'attrition': 455, 'rf_auc': 0.620801, 'rf_auc_sd': 0.021317, 'lr_auc': 0.628263, 'lr_auc_sd': 0.033807, 'r_solved_per_contest': -0.124657}
- {'rating_cut': 1400, 'inactive_months_min': 12.0, 'active': 2947, 'attrition': 231, 'rf_auc': 0.619603, 'rf_auc_sd': 0.022331, 'lr_auc': 0.655719, 'lr_auc_sd': 0.021124, 'r_solved_per_contest': -0.172648}
- {'rating_cut': 1500, 'inactive_months_min': 3.0, 'active': 3421, 'attrition': 908, 'rf_auc': 0.616998, 'rf_auc_sd': 0.015341, 'lr_auc': 0.596791, 'lr_auc_sd': 0.031518, 'r_solved_per_contest': -0.130878}
- {'rating_cut': 1500, 'inactive_months_min': 6.0, 'active': 3421, 'attrition': 545, 'rf_auc': 0.629732, 'rf_auc_sd': 0.025433, 'lr_auc': 0.633665, 'lr_auc_sd': 0.040299, 'r_solved_per_contest': -0.133119}
- {'rating_cut': 1500, 'inactive_months_min': 12.0, 'active': 3421, 'attrition': 282, 'rf_auc': 0.623663, 'rf_auc_sd': 0.023073, 'lr_auc': 0.656444, 'lr_auc_sd': 0.018648, 'r_solved_per_contest': -0.177331}
- {'rating_cut': 1600, 'inactive_months_min': 3.0, 'active': 3717, 'attrition': 984, 'rf_auc': 0.610121, 'rf_auc_sd': 0.01566, 'lr_auc': 0.59736, 'lr_auc_sd': 0.013419, 'r_solved_per_contest': -0.130696}
- {'rating_cut': 1600, 'inactive_months_min': 6.0, 'active': 3717, 'attrition': 597, 'rf_auc': 0.623665, 'rf_auc_sd': 0.017375, 'lr_auc': 0.635048, 'lr_auc_sd': 0.012394, 'r_solved_per_contest': -0.135322}
- {'rating_cut': 1600, 'inactive_months_min': 12.0, 'active': 3717, 'attrition': 310, 'rf_auc': 0.615262, 'rf_auc_sd': 0.039562, 'lr_auc': 0.660463, 'lr_auc_sd': 0.029032, 'r_solved_per_contest': -0.186944}
[335s]

## B5 Matching on account age and number of contests

- {'before': {'age_median_active': 18.7, 'age_median_attrition': 33.5, 'contests_median_active': 13.0, 'contests_median_attrition': 13.0}, 'after_matching': {'age_median_active': 33.2, 'contests_median_active': 13.0}, 'rf_auc_mean': 0.578649, 'rf_auc_min': 0.565521, 'rf_auc_max': 0.598234, 'lr_auc_mean': 0.590789, 'lr_auc_min': 0.58261, 'lr_auc_max': 0.599194, 'n_matchings': 20}  [380s]

## B6 Ablation of the two constructed features

- all 8: {'LR': {'auc': 0.596496, 'delta_vs_all': 0.0, 'delta_sd_over_folds': 0.0, 'delta_p2_5': 0.0, 'delta_p97_5': 0.0}, 'RF': {'auc': 0.611503, 'delta_vs_all': 0.0, 'delta_sd_over_folds': 0.0, 'delta_p2_5': 0.0, 'delta_p97_5': 0.0}}
- without EDI: {'LR': {'auc': 0.597408, 'delta_vs_all': 0.000911, 'delta_sd_over_folds': 0.001979, 'delta_p2_5': -0.001229, 'delta_p97_5': 0.00596}, 'RF': {'auc': 0.607292, 'delta_vs_all': -0.004211, 'delta_sd_over_folds': 0.01056, 'delta_p2_5': -0.029834, 'delta_p97_5': 0.010576}}
- without solved_per_contest: {'LR': {'auc': 0.581877, 'delta_vs_all': -0.014619, 'delta_sd_over_folds': 0.009191, 'delta_p2_5': -0.028309, 'delta_p97_5': 0.002074}, 'RF': {'auc': 0.578071, 'delta_vs_all': -0.033432, 'delta_sd_over_folds': 0.014442, 'delta_p2_5': -0.063936, 'delta_p97_5': -0.011887}}
- without both: {'LR': {'auc': 0.582762, 'delta_vs_all': -0.013734, 'delta_sd_over_folds': 0.010083, 'delta_p2_5': -0.028358, 'delta_p97_5': 0.006257}, 'RF': {'auc': 0.57703, 'delta_vs_all': -0.034473, 'delta_sd_over_folds': 0.01481, 'delta_p2_5': -0.065073, 'delta_p97_5': -0.012216}}
- feature pairs with |Spearman rho| >= 0.4: {'math_solve_rate~ds_solve_rate': 0.516, 'math_solve_rate~acceptance_rate': 0.862, 'ds_solve_rate~acceptance_rate': 0.601, 'avg_struggle_minutes~upsolves_per_contest': 0.482, 'avg_struggle_minutes~editorial_dependency_index': 0.783, 'avg_struggle_minutes~solved_per_contest': 0.48, 'upsolves_per_contest~editorial_dependency_index': 0.837, 'upsolves_per_contest~solved_per_contest': 0.449, 'editorial_dependency_index~solved_per_contest': 0.459}  [447s]