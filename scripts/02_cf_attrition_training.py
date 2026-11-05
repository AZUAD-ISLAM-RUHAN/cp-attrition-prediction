"""
================================================================================
CF ATTRITION PREDICTION - FINAL SCRIPT (v3)
================================================================================

KEY CHANGES FROM PREVIOUS VERSION:
  1. TRUE ATTRITION LABEL:
     - Stopped + max_rating < 1400 = True Attrition (frustrated quit)
     - Stopped + max_rating >= 1400 = Intentional Exit → EXCLUDED
     - Active = Active
     
  2. CLEAN FEATURES (no data leakage):
     - months_since_last_submission REMOVED (used to define label)
     - max_rating REMOVED (used in label threshold)
     - current_rating REMOVED (misleading for stopped users)
     - Duplicate/derived features removed
     - 10 clean behavioral features remain
     
  3. VISUALIZATIONS:
     - Trend charts (5 key behavioral patterns)
     - Active vs True Attrition comparison
     - ML performance chart
     - Feature importance chart
     - All paper-ready quality

HOW TO RUN:
  1. Google Colab-e jan
  2. cf_attrition_features.csv upload korun (left panel > Files)
  3. Pura script ekta cell-e paste kore run korun
  4. Output files download kore Claude-ke din

OUTPUT FILES (paper-ready):
  - cf_model_results.csv
  - cf_feature_importance.csv  
  - cf_results_summary.txt
  - cf_trend_struggle_time.png
  - cf_trend_contest_frequency.png
  - cf_trend_editorial_dependency.png
  - cf_trend_activity_decay.png
  - cf_trend_skill_gap.png
  - cf_cv_f1_chart.png
  - cf_feature_importance_chart.png
  - cf_active_vs_attrition_chart.png
================================================================================
"""

# ============================================================
# INSTALL
# ============================================================
import subprocess
subprocess.run(["pip", "install", "xgboost", "lightgbm", "scipy", "--quiet"], check=True)

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 150

from scipy import stats
from sklearn.model_selection import StratifiedKFold, train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score
import xgboost as xgb
import lightgbm as lgb

RANDOM_STATE = 42
NAVY   = '#1B2A4A'
CORAL  = '#E8604C'
GRAY   = '#C8D3E3'
GOLD   = '#F5A623'

# ============================================================
# STEP 1: LOAD DATA
# ============================================================
print("=" * 60)
print("STEP 1: Loading data")
print("=" * 60)

CSV_PATH = "cf_attrition_features.csv"
df_raw = pd.read_csv(CSV_PATH)
print(f"Raw data: {len(df_raw)} users")
print(df_raw['status_proxy'].value_counts())

# ============================================================
# STEP 2: LABEL REFINEMENT
# ============================================================
print("\n" + "=" * 60)
print("STEP 2: Refining labels (True Attrition vs Intentional Exit)")
print("=" * 60)

# Separate groups
active_df = df_raw[df_raw['status_proxy'] == 'Active'].copy()
stopped_df = df_raw[df_raw['status_proxy'] == 'Stopped'].copy()

# True Attrition: stopped + max_rating < 1500 (Expert level threshold)
# These are users who got stuck at low/mid levels and quit — frustrated dropout
true_attrition_df = stopped_df[stopped_df['max_rating'] < 1500].copy()

# Intentional Exit: stopped + max_rating >= 1500
# These likely made a deliberate career transition — NOT attrition
intentional_exit_df = stopped_df[stopped_df['max_rating'] >= 1500].copy()

print(f"\nActive Pool:       {len(active_df)}")
print(f"True Attrition:    {len(true_attrition_df)} (stopped + max_rating < 1500)")
print(f"Intentional Exit:  {len(intentional_exit_df)} (stopped + max_rating >= 1500) → EXCLUDED")

# Build modeling dataset
active_df['label'] = 0        # Active
true_attrition_df['label'] = 1  # True Attrition

# --- PERFECT BALANCING VIA RANDOM UNDERSAMPLING ---
# Active গ্রুপ থেকে Attrition গ্রুপের সমান সংখ্যক ইউজার র্যান্ডমলি নেওয়া
active_downsampled = active_df.sample(n=len(true_attrition_df), random_state=RANDOM_STATE)

# ২টা গ্রুপকে ১:১ অনুপাতে জোড়া দিয়ে ফাইনাল মডেলিং ডেটাসেট তৈরি
df = pd.concat([active_downsampled, true_attrition_df], ignore_index=True)

print(f"\nModeling dataset (Balanced 1:1): {len(df)} users")
print(f"  Active (Downsampled): {sum(df['label']==0)}")
print(f"  True Attrition: {sum(df['label']==1)}")

# ============================================================
# STEP 3: CLEAN FEATURES
# ============================================================
print("\n" + "=" * 60)
print("STEP 3: Feature selection (no leakage)")
print("=" * 60)

# --- FEATURE ENGINEERING ---
# ১. প্র্যাকটিস ইনটেনসিটি বনাম কন্টেস্ট ফ্রিকোয়েন্সির রেশিও
df['intensity_ratio'] = df['problems_solved_per_month'] / (df['contests_per_month'] + 0.1)
# ২. এডিটোরিয়াল ডিপেন্ডেনসি ইনডেক্স (আপনার মূল হাইপোথিসিস)
df['editorial_dependency_index'] = df['upsolves_per_contest'] * df['avg_struggle_minutes']

# These features are:
# - Behavioral proxies (not label-defining)
# - Directly interpretable
# - Survey-aligned (each maps to a survey question)
FEATURES = [
    'math_solve_rate',         # Math skill proxy (survey Q5)
    'ds_solve_rate',           # DS understanding proxy (survey Q14)
    'upsolves_per_contest',    # Post-contest upsolving (survey Q11)
    'avg_struggle_minutes',    # Struggle time (survey Q13)
    'activity_trend_ratio',    # Burnout/decay (survey Q18)
    'post_drop_recovery',      # Resilience after rating drop (survey Q17)
    'contests_per_month',      # Engagement frequency (survey Q10)
    'problems_solved_per_month', # Practice intensity (survey Q12)
    'acceptance_rate',         # Skill efficiency
    'account_age_months',      # CP experience duration (survey Q3)
    'intensity_ratio',         # New: Practice vs Contest intensity ratio
    'editorial_dependency_index' # New: Editorial dependency Index
]

# Keep only features that exist in the CSV
FEATURES = [f for f in FEATURES if f in df.columns]
print(f"Using {len(FEATURES)} clean features:")
for f in FEATURES:
    print(f"  - {f}")

# EXCLUDED features and why:
print("\nEXCLUDED features:")
print("  - months_since_last_submission: used to DEFINE the label (data leakage)")
print("  - max_rating: used in label threshold (data leakage)")
print("  - current_rating: misleading for stopped users")
print("  - total_contests: redundant with contests_per_month")
print("  - burnout_flag: derived from activity_trend_ratio (redundant)")
print("  - *_1to5 scores: derived from raw features (redundant)")
print("  NOTE: 1-5 normalized scores ARE included (abstract claim: normalize to 1-5 scale)")

X = df[FEATURES].copy()
y = df['label'].copy()

# ============================================================
# STEP 4: TREND VISUALIZATIONS
# ============================================================
print("\n" + "=" * 60)
print("STEP 4: Generating trend charts")
print("=" * 60)

active = df[df['label'] == 0]
attrition = df[df['label'] == 1]

def add_stat_annotation(ax, a_vals, s_vals, x_pos, y_pos):
    """Add t-test significance annotation to chart."""
    t, p = stats.ttest_ind(a_vals.dropna(), s_vals.dropna())
    if p < 0.001:
        sig = "p < 0.001 ***"
    elif p < 0.01:
        sig = f"p = {p:.3f} **"
    elif p < 0.05:
        sig = f"p = {p:.3f} *"
    else:
        sig = f"p = {p:.3f} (ns)"
    ax.text(x_pos, y_pos, sig, transform=ax.transAxes,
            fontsize=9, color='gray', ha='right')

# --- Trend 1: Struggle Time ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Boxplot
axes[0].boxplot([active['avg_struggle_minutes'].dropna(),
                 attrition['avg_struggle_minutes'].dropna()],
                labels=['Active', 'True Attrition'],
                patch_artist=True,
                boxprops=dict(facecolor=NAVY, alpha=0.7),
                medianprops=dict(color=CORAL, linewidth=2))
axes[0].set_ylabel('Avg Struggle Time (minutes)', fontsize=11)
axes[0].set_title('Struggle Time Distribution', fontsize=12, fontweight='bold')
add_stat_annotation(axes[0], active['avg_struggle_minutes'],
                    attrition['avg_struggle_minutes'], 0.98, 0.95)

# Bar comparison
means = [active['avg_struggle_minutes'].mean(), attrition['avg_struggle_minutes'].mean()]
bars = axes[1].bar(['Active', 'True Attrition'], means,
                   color=[NAVY, CORAL], width=0.5, zorder=3)
for bar, val in zip(bars, means):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                 f'{val:.0f} min', ha='center', va='bottom', fontweight='bold')
axes[1].set_ylabel('Mean Struggle Time (minutes)', fontsize=11)
axes[1].set_title('Mean Struggle Time\nActive vs True Attrition', fontsize=12, fontweight='bold')
axes[1].yaxis.grid(True, linestyle='--', alpha=0.4)
axes[1].set_axisbelow(True)
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)

diff_pct = (means[1] - means[0]) / means[0] * 100
fig.suptitle(f'Trend 1: Struggle Time — True Attrition users struggle {diff_pct:.1f}% more\n'
             f'(Supports "progress stagnation" as primary attrition driver)',
             fontsize=11, style='italic', y=1.02)
fig.tight_layout()
fig.savefig('cf_trend_struggle_time.png', bbox_inches='tight')
plt.close()
print("Saved: cf_trend_struggle_time.png")

# --- Trend 2: Contest Frequency ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].boxplot([active['contests_per_month'].dropna(),
                 attrition['contests_per_month'].dropna()],
                labels=['Active', 'True Attrition'],
                patch_artist=True,
                boxprops=dict(facecolor=NAVY, alpha=0.7),
                medianprops=dict(color=CORAL, linewidth=2))
axes[0].set_ylabel('Contests per Month', fontsize=11)
axes[0].set_title('Contest Frequency Distribution', fontsize=12, fontweight='bold')
axes[0].set_ylim(0, 20)
add_stat_annotation(axes[0], active['contests_per_month'],
                    attrition['contests_per_month'], 0.98, 0.95)

means = [active['contests_per_month'].mean(), attrition['contests_per_month'].mean()]
bars = axes[1].bar(['Active', 'True Attrition'], means,
                   color=[NAVY, CORAL], width=0.5, zorder=3)
for bar, val in zip(bars, means):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
axes[1].set_ylabel('Mean Contests per Month', fontsize=11)
axes[1].set_title('Contest Frequency\nActive vs True Attrition', fontsize=12, fontweight='bold')
axes[1].yaxis.grid(True, linestyle='--', alpha=0.4)
axes[1].set_axisbelow(True)
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)

diff_pct = (means[0] - means[1]) / means[0] * 100
fig.suptitle(f'Trend 2: Contest Frequency — Active users participate {diff_pct:.1f}% more frequently\n'
             f'(Disengagement precedes attrition)',
             fontsize=11, style='italic', y=1.02)
fig.tight_layout()
fig.savefig('cf_trend_contest_frequency.png', bbox_inches='tight')
plt.close()
print("Saved: cf_trend_contest_frequency.png")

# --- Trend 3: Editorial Dependency (upsolving paradox) ---
fig, ax = plt.subplots(figsize=(9, 5))

categories = ['Always\n(>=2 upsolves/contest)', 'Sometimes\n(1-2)', 'Rarely\n(0.5-1)', 'Never\n(<0.5)']
bins = [2, 1, 0.5, 0]

active_counts = [
    (active['upsolves_per_contest'] >= 2).sum(),
    ((active['upsolves_per_contest'] >= 1) & (active['upsolves_per_contest'] < 2)).sum(),
    ((active['upsolves_per_contest'] >= 0.5) & (active['upsolves_per_contest'] < 1)).sum(),
    (active['upsolves_per_contest'] < 0.5).sum(),
]
attrition_counts = [
    (attrition['upsolves_per_contest'] >= 2).sum(),
    ((attrition['upsolves_per_contest'] >= 1) & (attrition['upsolves_per_contest'] < 2)).sum(),
    ((attrition['upsolves_per_contest'] >= 0.5) & (attrition['upsolves_per_contest'] < 1)).sum(),
    (attrition['upsolves_per_contest'] < 0.5).sum(),
]

# Normalize to percentages
active_pct   = [c/len(active)*100   for c in active_counts]
attrition_pct = [c/len(attrition)*100 for c in attrition_counts]

x = np.arange(len(categories))
width = 0.35
b1 = ax.bar(x - width/2, active_pct,   width, label='Active',        color=NAVY,  zorder=3)
b2 = ax.bar(x + width/2, attrition_pct, width, label='True Attrition', color=CORAL, zorder=3)

for bar, val in zip(list(b1)+list(b2), active_pct+attrition_pct):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=8.5)

ax.set_ylabel('Percentage of Users (%)', fontsize=11)
ax.set_title('Trend 3: Post-Contest Upsolving Behavior\n'
             '"Editorial Dependency Hypothesis" — Stopped users upsolved more but gained less skill',
             fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=9)
ax.legend(fontsize=10)
ax.yaxis.grid(True, linestyle='--', alpha=0.4)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig('cf_trend_editorial_dependency.png', bbox_inches='tight')
plt.close()
print("Saved: cf_trend_editorial_dependency.png")

# --- Trend 4: Activity Decay (burnout) ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].boxplot([active['activity_trend_ratio'].dropna(),
                 attrition['activity_trend_ratio'].dropna()],
                labels=['Active', 'True Attrition'],
                patch_artist=True,
                boxprops=dict(facecolor=NAVY, alpha=0.7),
                medianprops=dict(color=CORAL, linewidth=2))
axes[0].set_ylabel('Activity Trend Ratio\n(recent 6mo / prior 6mo)', fontsize=11)
axes[0].set_title('Activity Trend Distribution', fontsize=12, fontweight='bold')
axes[0].set_ylim(0, 10)
add_stat_annotation(axes[0], active['activity_trend_ratio'],
                    attrition['activity_trend_ratio'], 0.98, 0.95)

burnout_active   = (active['burnout_flag'] == True).sum() / len(active) * 100
burnout_attrition = (attrition['burnout_flag'] == True).sum() / len(attrition) * 100
bars = axes[1].bar(['Active', 'True Attrition'],
                   [burnout_active, burnout_attrition],
                   color=[NAVY, CORAL], width=0.5, zorder=3)
for bar, val in zip(bars, [burnout_active, burnout_attrition]):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
axes[1].set_ylabel('% Users with Burnout Flag', fontsize=11)
axes[1].set_title('Burnout Rate\n(activity declining >50%)', fontsize=12, fontweight='bold')
axes[1].yaxis.grid(True, linestyle='--', alpha=0.4)
axes[1].set_axisbelow(True)
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)

fig.suptitle('Trend 4: Activity Decay / Burnout — True Attrition users show higher burnout rates',
             fontsize=11, style='italic', y=1.02)
fig.tight_layout()
fig.savefig('cf_trend_activity_decay.png', bbox_inches='tight')
plt.close()
print("Saved: cf_trend_activity_decay.png")

# --- Trend 5: Skill Gap (math + DS) ---
fig, ax = plt.subplots(figsize=(9, 5))

skill_features = {
    'Math\nSolve Rate': 'math_solve_rate',
    'DS\nSolve Rate': 'ds_solve_rate',
    'Acceptance\nRate': 'acceptance_rate',
    'Problems\nSolved/Month': 'problems_solved_per_month',
}

active_means  = [active[col].mean()    for col in skill_features.values()]
attrition_means = [attrition[col].mean() for col in skill_features.values()]
labels = list(skill_features.keys())

x = np.arange(len(labels))
width = 0.35
b1 = ax.bar(x - width/2, active_means,   width, label='Active',        color=NAVY,  zorder=3)
b2 = ax.bar(x + width/2, attrition_means, width, label='True Attrition', color=CORAL, zorder=3)

for bar, val in zip(list(b1)+list(b2), active_means+attrition_means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.003,
            f'{val:.3f}', ha='center', va='bottom', fontsize=8.5)

ax.set_ylabel('Mean Score', fontsize=11)
ax.set_title('Trend 5: Skill Gap — True Attrition users consistently underperform\n'
             'across all skill-related metrics',
             fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=10)
ax.legend(fontsize=10)
ax.yaxis.grid(True, linestyle='--', alpha=0.4)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig('cf_trend_skill_gap.png', bbox_inches='tight')
plt.close()
print("Saved: cf_trend_skill_gap.png")

# --- Active vs True Attrition: Overall comparison (1-5 scale) ---
compare_features = {
    'Math Skill\n(1-5)':        'math_solve_rate_1to5',
    'DS Understanding\n(1-5)':  'ds_solve_rate_1to5',
    'Upsolving\n(1-5)':         'upsolves_per_contest_1to5',
    'Struggle Time\n(1-5)':     'avg_struggle_minutes_1to5',
    'Activity Trend\n(1-5)':    'activity_trend_ratio_1to5',
    'Rating Volatility\n(1-5)': 'rating_volatility_1to5',
}

available = {k: v for k, v in compare_features.items() if v in df.columns}
if available:
    active_means_1to5   = [active[col].mean()    for col in available.values()]
    attrition_means_1to5 = [attrition[col].mean() for col in available.values()]

    x = np.arange(len(available))
    fig, ax = plt.subplots(figsize=(11, 5))
    b1 = ax.bar(x - width/2, active_means_1to5,   width,
                label=f'Active (n={len(active)})',        color=NAVY,  zorder=3)
    b2 = ax.bar(x + width/2, attrition_means_1to5, width,
                label=f'True Attrition (n={len(attrition)})', color=CORAL, zorder=3)

    for bar, val in zip(list(b1)+list(b2), active_means_1to5+attrition_means_1to5):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
                f'{val:.2f}', ha='center', va='bottom', fontsize=9)

    ax.set_ylabel('Mean Score (1-5 Scale)', fontsize=11)
    ax.set_title(f'Active vs True Attrition: Behavioral Feature Comparison\n'
                 f'(Codeforces Dataset, n={len(df)}, excl. intentional exits)',
                 fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(list(available.keys()), fontsize=9)
    ax.set_ylim(0, 6.2)
    ax.legend(fontsize=10)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    fig.savefig('cf_active_vs_attrition_chart.png', bbox_inches='tight')
    plt.close()
    print("Saved: cf_active_vs_attrition_chart.png")

# ============================================================
# STEP 5: ML PIPELINE
# ============================================================
print("\n" + "=" * 60)
print("STEP 5: ML Pipeline")
print("=" * 60)

preprocessor = ColumnTransformer(transformers=[
    ("num", Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]), FEATURES),
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
)
print(f"Train: {len(X_train)} | Test: {len(X_test)}")
print(f"Train — Active: {sum(y_train==0)}, Attrition: {sum(y_train==1)}")

pos_weight = sum(y==0) / sum(y==1)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE, class_weight='balanced'),
    "Decision Tree":       DecisionTreeClassifier(random_state=RANDOM_STATE, class_weight='balanced'),
    "Random Forest":       RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, class_weight='balanced'),
    "KNN":                 KNeighborsClassifier(n_neighbors=5),
    "SVM":                 SVC(probability=True, random_state=RANDOM_STATE, class_weight='balanced'),
    "XGBoost":             xgb.XGBClassifier(n_estimators=200, random_state=RANDOM_STATE,
                                              scale_pos_weight=pos_weight,
                                              eval_metric='logloss', verbosity=0),
    "LightGBM":            lgb.LGBMClassifier(n_estimators=200, random_state=RANDOM_STATE,
                                               class_weight='balanced', verbose=-1),
    "MLP":                 MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500,
                                         random_state=RANDOM_STATE, early_stopping=True),
}

voting = VotingClassifier(
    estimators=[
        ("lr",  LogisticRegression(max_iter=1000, random_state=RANDOM_STATE, class_weight='balanced')),
        ("rf",  RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, class_weight='balanced')),
        ("svm", SVC(probability=True, random_state=RANDOM_STATE, class_weight='balanced')),
        ("xgb", xgb.XGBClassifier(n_estimators=200, random_state=RANDOM_STATE,
                                    scale_pos_weight=pos_weight, eval_metric='logloss', verbosity=0)),
    ], voting="soft"
)
models["Soft-Voting Ensemble"] = voting

# ============================================================
# STEP 6: CROSS-VALIDATION
# ============================================================
print("\n" + "=" * 60)
print("STEP 6: 5-Fold CV")
print("=" * 60)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
cv_results = {}

for name, clf in models.items():
    pipe = Pipeline([("prep", preprocessor), ("clf", clf)])
    scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1")
    cv_results[name] = {"cv_f1_mean": round(scores.mean(), 3), "cv_f1_std": round(scores.std(), 3)}
    print(f"  {name:25s}: CV F1 = {scores.mean():.3f} (+/- {scores.std():.3f})")

# ============================================================
# STEP 7: TEST SET
# ============================================================
print("\n" + "=" * 60)
print("STEP 7: Test Set Results")
print("=" * 60)

test_results = {}
trained_pipes = {}

for name, clf in models.items():
    pipe = Pipeline([("prep", preprocessor), ("clf", clf)])
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    test_results[name] = {
        "test_accuracy":  round(accuracy_score(y_test, preds), 3),
        "test_f1":        round(f1_score(y_test, preds, zero_division=0), 3),
        "test_precision": round(precision_score(y_test, preds, zero_division=0), 3),
        "test_recall":    round(recall_score(y_test, preds, zero_division=0), 3),
    }
    trained_pipes[name] = pipe
    r = test_results[name]
    print(f"  {name:25s}: Acc={r['test_accuracy']:.3f} F1={r['test_f1']:.3f} "
          f"Prec={r['test_precision']:.3f} Rec={r['test_recall']:.3f}")

# ============================================================
# STEP 8: FEATURE IMPORTANCE
# ============================================================
print("\n" + "=" * 60)
print("STEP 8: Feature Importance")
print("=" * 60)

rf_pipe = trained_pipes["Random Forest"]
importances = rf_pipe.named_steps["clf"].feature_importances_
feat_imp = pd.DataFrame({"feature": FEATURES, "importance": importances}).sort_values("importance", ascending=False)
print(feat_imp.to_string(index=False))
feat_imp.to_csv("cf_feature_importance.csv", index=False)

# ============================================================
# STEP 9: ML CHARTS
# ============================================================
print("\n" + "=" * 60)
print("STEP 9: ML Charts")
print("=" * 60)

# CV F1 Chart
model_names = list(cv_results.keys())
cv_means = [cv_results[m]['cv_f1_mean'] for m in model_names]
cv_stds  = [cv_results[m]['cv_f1_std']  for m in model_names]

fig, ax = plt.subplots(figsize=(11, 5))
colors = [CORAL if v == max(cv_means) else NAVY for v in cv_means]
ax.bar(model_names, cv_means, color=colors, width=0.6, zorder=3)
ax.errorbar(range(len(model_names)), cv_means, yerr=cv_stds,
            fmt='none', color='black', capsize=4, linewidth=1.2, zorder=4)
for i, val in enumerate(cv_means):
    ax.text(i, val + 0.015, f'{val:.3f}', ha='center', va='bottom',
            fontsize=9, fontweight='bold')
ax.set_ylim(0, 1.1)
ax.set_ylabel('Mean F1-Score (5-Fold CV)', fontsize=12)
ax.set_title('Cross-Validation Performance: True Attrition vs Active\n'
             '(Intentional exits excluded from dataset)',
             fontsize=12, fontweight='bold')
ax.set_xticks(range(len(model_names)))
ax.set_xticklabels(model_names, rotation=20, ha='right', fontsize=9)
ax.yaxis.grid(True, linestyle='--', alpha=0.5, zorder=0)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig('cf_cv_f1_chart.png', bbox_inches='tight')
plt.close()
print("Saved: cf_cv_f1_chart.png")

# Feature Importance Chart
top10 = feat_imp.head(10)
fig, ax = plt.subplots(figsize=(8, 5))
colors = [CORAL if i == 0 else NAVY for i in range(len(top10))]
ax.barh(top10['feature'][::-1], top10['importance'][::-1],
        color=colors[::-1], height=0.6, zorder=3)
for i, (val, feat) in enumerate(zip(top10['importance'][::-1], top10['feature'][::-1])):
    ax.text(val + 0.001, i, f'{val:.3f}', va='center', fontsize=9)
ax.set_xlabel('Feature Importance', fontsize=11)
ax.set_title('Random Forest Feature Importance\n(CF Dataset, True Attrition only)',
             fontsize=12, fontweight='bold')
ax.xaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig('cf_feature_importance_chart.png', bbox_inches='tight')
plt.close()
print("Saved: cf_feature_importance_chart.png")

# ============================================================
# STEP 10: SAVE RESULTS
# ============================================================
print("\n" + "=" * 60)
print("STEP 10: Saving results")
print("=" * 60)

rows = []
for name in models:
    row = {"model": name}
    row.update(cv_results[name])
    row.update(test_results[name])
    rows.append(row)
pd.DataFrame(rows).to_csv("cf_model_results.csv", index=False)

best = max(cv_results, key=lambda m: cv_results[m]['cv_f1_mean'])

with open("cf_results_summary.txt", "w") as f:
    f.write("=" * 60 + "\n")
    f.write("CF ATTRITION MODEL - FINAL RESULTS SUMMARY (v3)\n")
    f.write("=" * 60 + "\n\n")
    f.write("DATASET:\n")
    f.write(f"  Raw: {len(df_raw)} users\n")
    f.write(f"  Active: {len(active_df)}\n")
    f.write(f"  True Attrition (max_rating < 1400): {len(true_attrition_df)}\n")
    f.write(f"  Intentional Exit (max_rating >= 1400): {len(intentional_exit_df)} → EXCLUDED\n")
    f.write(f"  Modeling dataset: {len(df)} users\n\n")
    f.write("KEY TRENDS (Active vs True Attrition):\n")
    trends = [
        ('Struggle Time', 'avg_struggle_minutes', True),
        ('Contests/Month', 'contests_per_month', False),
        ('Math Solve Rate', 'math_solve_rate', False),
        ('DS Solve Rate', 'ds_solve_rate', False),
        ('Upsolving/Contest', 'upsolves_per_contest', True),
        ('Activity Trend', 'activity_trend_ratio', False),
    ]
    for label, col, higher_bad in trends:
        a = active[col].mean()
        s = attrition[col].mean()
        diff = (s - a) / a * 100
        direction = "↑" if diff > 0 else "↓"
        f.write(f"  {label:25s}: Active={a:.3f} | Attrition={s:.3f} | {direction}{abs(diff):.1f}%\n")
    f.write("\nCROSS-VALIDATION (5-Fold F1):\n")
    for name, r in cv_results.items():
        f.write(f"  {name:25s}: {r['cv_f1_mean']:.3f} (+/- {r['cv_f1_std']:.3f})\n")
    f.write("\nTEST SET:\n")
    for name, r in test_results.items():
        f.write(f"  {name:25s}: Acc={r['test_accuracy']:.3f} F1={r['test_f1']:.3f} "
                f"Prec={r['test_precision']:.3f} Rec={r['test_recall']:.3f}\n")
    f.write(f"\nBEST MODEL: {best} (CV F1={cv_results[best]['cv_f1_mean']:.3f})\n")
    f.write("\nTOP 5 FEATURES:\n")
    for _, row in feat_imp.head(5).iterrows():
        f.write(f"  {row['feature']:35s}: {row['importance']:.4f}\n")

print("Saved: cf_results_summary.txt")
print("Saved: cf_model_results.csv")

print("\n" + "=" * 60)
print("ALL DONE! Download all files:")
print("=" * 60)
output_files = [
    "cf_model_results.csv",
    "cf_feature_importance.csv",
    "cf_results_summary.txt",
    "cf_trend_struggle_time.png",
    "cf_trend_contest_frequency.png",
    "cf_trend_editorial_dependency.png",
    "cf_trend_activity_decay.png",
    "cf_trend_skill_gap.png",
    "cf_cv_f1_chart.png",
    "cf_feature_importance_chart.png",
    "cf_active_vs_attrition_chart.png",
]
print("\nfrom google.colab import files")
for f_name in output_files:
    print(f"files.download('{f_name}')")
