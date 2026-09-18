import pandas as pd, numpy as np, json, warnings
warnings.filterwarnings('ignore')
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
import xgboost as xgb, lightgbm as lgb

RS = 42
raw = pd.read_csv('data/cf_attrition_features.csv')

def build(match_rating: bool):
    """Replicate the original script, optionally matching the active pool on peak rating."""
    active  = raw[raw['status_proxy']=='Active'].copy()
    stopped = raw[raw['status_proxy']=='Stopped'].copy()
    ta = stopped[stopped['max_rating'] < 1500].copy()
    if match_rating:
        active = active[active['max_rating'] < 1500].copy()
    active['label']=0; ta['label']=1
    act_ds = active.sample(n=len(ta), random_state=RS)
    d = pd.concat([act_ds, ta], ignore_index=True)
    # --- FEATURE ENGINEERING exactly as in the original script ---
    d['intensity_ratio'] = d['problems_solved_per_month'] / (d['contests_per_month'] + 0.1)
    d['editorial_dependency_index'] = d['upsolves_per_contest'] * d['avg_struggle_minutes']
    return d

FEATURES_FULL = ['math_solve_rate','ds_solve_rate','upsolves_per_contest','avg_struggle_minutes',
 'activity_trend_ratio','post_drop_recovery','contests_per_month','problems_solved_per_month',
 'acceptance_rate','account_age_months','intensity_ratio','editorial_dependency_index']
SUSPECT = ['account_age_months','contests_per_month','activity_trend_ratio']
FEATURES_AUDIT = [f for f in FEATURES_FULL if f not in SUSPECT]

def models_for(y):
    pw = sum(y==0)/sum(y==1)
    m = {
     "Logistic Regression": LogisticRegression(max_iter=1000,random_state=RS,class_weight='balanced'),
     "Decision Tree": DecisionTreeClassifier(random_state=RS,class_weight='balanced'),
     "Random Forest": RandomForestClassifier(n_estimators=200,random_state=RS,class_weight='balanced'),
     "KNN": KNeighborsClassifier(n_neighbors=5),
     "SVM": SVC(probability=True,random_state=RS,class_weight='balanced'),
     "XGBoost": xgb.XGBClassifier(n_estimators=200,random_state=RS,scale_pos_weight=pw,eval_metric='logloss',verbosity=0),
     "LightGBM": lgb.LGBMClassifier(n_estimators=200,random_state=RS,class_weight='balanced',verbose=-1),
     "MLP": MLPClassifier(hidden_layer_sizes=(64,32),max_iter=500,random_state=RS,early_stopping=True),
    }
    m["Soft-Voting Ensemble"] = VotingClassifier(estimators=[
        ("lr",LogisticRegression(max_iter=1000,random_state=RS,class_weight='balanced')),
        ("rf",RandomForestClassifier(n_estimators=200,random_state=RS,class_weight='balanced')),
        ("svm",SVC(probability=True,random_state=RS,class_weight='balanced')),
        ("xgb",xgb.XGBClassifier(n_estimators=200,random_state=RS,scale_pos_weight=pw,eval_metric='logloss',verbosity=0)),
    ], voting="soft")
    return m

def run(d, feats, tag):
    X, y = d[feats].copy(), d['label'].copy()
    prep = ColumnTransformer([("num", Pipeline([("impute",SimpleImputer(strategy="median")),
                                                ("scale",StandardScaler())]), feats)])
    Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2,stratify=y,random_state=RS)
    cv = StratifiedKFold(n_splits=5,shuffle=True,random_state=RS)
    print(f"\n### {tag}   (n={len(d)}, {len(feats)} features)")
    print(f"{'Classifier':<23}{'CVF1':>7}{'SD':>7}{'Acc':>7}{'F1':>7}{'Rec':>7}")
    out={}
    for name,clf in models_for(y).items():
        pipe = Pipeline([("prep",prep),("clf",clf)])
        sc = cross_val_score(pipe, Xtr, ytr, cv=cv, scoring="f1")   # CV on TRAIN, as in original
        pipe.fit(Xtr,ytr); p = pipe.predict(Xte)
        r = dict(cv=round(sc.mean(),3), sd=round(sc.std(),3),
                 acc=round(accuracy_score(yte,p),3), f1=round(f1_score(yte,p,zero_division=0),3),
                 rec=round(recall_score(yte,p,zero_division=0),3))
        out[name]=r
        print(f"{name:<23}{r['cv']:>7.3f}{r['sd']:>7.3f}{r['acc']:>7.3f}{r['f1']:>7.3f}{r['rec']:>7.3f}")
    return out

res={}
dA = build(match_rating=False)
res['A'] = run(dA, FEATURES_FULL, "SPEC A - Original (unmatched, 12 features)")
dB = build(match_rating=True)
res['B'] = run(dB, FEATURES_FULL, "SPEC B - Rating matched, 12 features")
res['C'] = run(dB, FEATURES_AUDIT, "SPEC C - Rating matched + leakage audited (9 features)")

# feature importance
print("\n\n### FEATURE IMPORTANCE")
for tag, d, feats in [("A (unmatched, 12f)", dA, FEATURES_FULL),
                      ("B (matched, 12f)",   dB, FEATURES_FULL),
                      ("C (audited, 9f)",    dB, FEATURES_AUDIT)]:
    X,y = d[feats], d['label']
    Xtr,_,ytr,_ = train_test_split(X,y,test_size=0.2,stratify=y,random_state=RS)
    prep = ColumnTransformer([("num",Pipeline([("impute",SimpleImputer(strategy="median")),
                                               ("scale",StandardScaler())]),feats)])
    pipe = Pipeline([("prep",prep),("clf",RandomForestClassifier(n_estimators=200,random_state=RS,class_weight='balanced'))]).fit(Xtr,ytr)
    imp = sorted(zip(feats, pipe.named_steps['clf'].feature_importances_), key=lambda t:-t[1])
    print(f"\n-- {tag} --")
    for i,(f,v) in enumerate(imp,1):
        print(f"  {i:2}. {f:<30}{v:.3f}")

json.dump(res, open('rerun_correct.json','w'), indent=1)
