# B1 - features from the period before inactivity (T_obs 2026-06-23T13:44:17+00:00)

Cohort: 2669 active, 908 attrition (published cohort and labels (--cohort-csv); accounts without records: 752).

## Window: 6_months ending 3 months before each account's last submission
Accounts with enough activity in the window: 1208 active, 298 attrition
- LR: ROC-AUC 0.6503 [0.6147, 0.6844], PR-AUC 0.3163 (base 0.1979), Brier 0.1519 (base 0.1587)
- RF: ROC-AUC 0.6241 [0.5868, 0.6606], PR-AUC 0.3195 (base 0.1979), Brier 0.1548 (base 0.1587)
  - math_solve_rate: r = -0.116 [-0.1994, -0.038], Holm p = 0.00954
  - ds_solve_rate: r = -0.0429 [-0.1243, 0.027], Holm p = 0.5
  - acceptance_rate: r = -0.138 [-0.2141, -0.0692], Holm p = 0.00132
  - avg_struggle_minutes: r = -0.1734 [-0.244, -0.0957], Holm p = 2.43e-05
  - upsolves_per_contest: r = -0.021 [-0.0955, 0.0475], Holm p = 0.568
  - post_drop_recovery: r = 0.058 [-0.017, 0.1296], Holm p = 0.355
  - editorial_dependency_index: r = -0.0907 [-0.1559, -0.0274], Holm p = 0.0557
  - solved_per_contest: r = -0.291 [-0.3548, -0.2251], Holm p = 5.32e-14

## Window: 12_months ending 3 months before each account's last submission
Accounts with enough activity in the window: 1631 active, 460 attrition
- LR: ROC-AUC 0.6085 [0.5797, 0.6377], PR-AUC 0.2988 (base 0.22), Brier 0.168 (base 0.1716)
- RF: ROC-AUC 0.5863 [0.5569, 0.6159], PR-AUC 0.2724 (base 0.22), Brier 0.1742 (base 0.1716)
  - math_solve_rate: r = -0.0796 [-0.1395, -0.0166], Holm p = 0.0452
  - ds_solve_rate: r = -0.0688 [-0.1327, -0.0076], Holm p = 0.0957
  - acceptance_rate: r = -0.0896 [-0.1465, -0.0282], Holm p = 0.0198
  - avg_struggle_minutes: r = -0.1218 [-0.1849, -0.0584], Holm p = 0.000454
  - upsolves_per_contest: r = 0.0086 [-0.0496, 0.0696], Holm p = 0.776
  - post_drop_recovery: r = 0.0285 [-0.031, 0.0876], Holm p = 0.694
  - editorial_dependency_index: r = -0.0632 [-0.1235, -0.0064], Holm p = 0.109
  - solved_per_contest: r = -0.2234 [-0.2797, -0.1682], Holm p = 1.9e-12

B3 (attrition accounts): {'attrition_accounts': 908, 'fewer_submissions_than_rated_contests': 0, 'rated_contests_before_first_retrieved_submission': 0, 'hit_10000_submission_cap': 0}
E4 (accounts whose inactivity rounds to 3.0): []
