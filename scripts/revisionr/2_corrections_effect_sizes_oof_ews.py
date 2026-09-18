import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
from scipy import stats
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

df=pd.read_csv('data/survey_responses.csv')
S="6. Your current CP status? "
m=df[df[S]!="Never started CP"].copy()
def coal(r,a,s):
    v=r.get(a,np.nan); return v if pd.notna(v) else r.get(s,np.nan)
m["dsa_grade"]=m["4. Grade in Data Structures and Algorithms (DSA) course "]
m["math_skill"]=m["5. Mathematics skills rating "]
m["prior_exp"]=m["3. Did you know programming before university? "]
m["ds_understanding"]=m.apply(lambda r: coal(r,"14. Understanding of standard data structures ","37. Understanding of standard data structures when you quit "),axis=1)
m["mentor_support"]=m.apply(lambda r: coal(r,"22. Have a mentor/senior guide? ","35. Had mentor/senior support? "),axis=1)
m["long_break"]=m.apply(lambda r: coal(r,"27. Taken 15+ consecutive days break in last 3 months? ",
                                         '36. Have you taken 15+ consecutive days of break during your CP journey?"'),axis=1)
m["thought_quit"]=m.apply(lambda r: coal(r,"28. Ever seriously thought about quitting CP? ","34.  Ever seriously thought about quitting CP?"),axis=1)
ua=m["11. Do you do upsolving after contests? "]; ps=m["33.  Practice habit in the month before quitting "]
m["upsolving_habit"]=[a if pd.notna(a) else {"Regular":"Sometimes","Became irregular":"Rarely","Stopped completely":"Never"}.get(p,np.nan) for a,p in zip(ua,ps)]
m["active"]=m[S].str.contains("Currently active",case=False,na=False)

# EXCLUDE intentional exits -> n = 64
INT="Interest in other tracks (Web Dev/ML)"
m64=m[~((~m.active)&(m["31. Main reasons for quitting "]==INT))].copy()
m64["label"]=(~m64.active).astype(int)
print(f"n = {len(m64)}   Active = {(m64.label==0).sum()}   True Attrition = {(m64.label==1).sum()}\n")
m64["grp"]=np.where(m64.label==0,"Active","Attrition")

NUM=["math_skill","ds_understanding"]
CAT=["dsa_grade","prior_exp","mentor_support","long_break","thought_quit","upsolving_habit"]

rows=[]
for f in NUM:
    a=pd.to_numeric(m64.loc[m64.grp=="Active",f],errors='coerce').dropna()
    s=pd.to_numeric(m64.loc[m64.grp=="Attrition",f],errors='coerce').dropna()
    t,pv=stats.ttest_ind(a,s,equal_var=False); n1,n2=len(a),len(s)
    sp=np.sqrt(((n1-1)*a.var(ddof=1)+(n2-1)*s.var(ddof=1))/(n1+n2-2)); d=(a.mean()-s.mean())/sp
    se=np.sqrt((n1+n2)/(n1*n2)+d**2/(2*(n1+n2)))
    rows.append((f,"Welch t",f"{t:.2f}",pv,f"d={d:.2f}",f"[{d-1.96*se:.2f}, {d+1.96*se:.2f}]",f"{a.mean():.2f} vs {s.mean():.2f}"))
rng=np.random.default_rng(42)
for f in CAT:
    sub=m64[[f,"grp"]].dropna(); ct=pd.crosstab(sub[f],sub["grp"])
    chi2,pv,dof,_=stats.chi2_contingency(ct); n=ct.values.sum(); V=np.sqrt(chi2/(n*(min(ct.shape)-1)))
    bs=[]
    for _ in range(2000):
        b=sub.sample(len(sub),replace=True,random_state=int(rng.integers(1e9))).reset_index(drop=True)
        c=pd.crosstab(b[f],b["grp"])
        if min(c.shape)<2: continue
        x2,_,_,_=stats.chi2_contingency(c); bs.append(np.sqrt(x2/(c.values.sum()*(min(c.shape)-1))))
    lo,hi=np.percentile(bs,[2.5,97.5])
    rows.append((f,"chi-square",f"{chi2:.2f}",pv,f"V={V:.2f}",f"[{lo:.2f}, {hi:.2f}]",f"n={n}, df={dof}"))

res=pd.DataFrame(rows,columns=["feature","test","stat","p","eff","ci","note"]).sort_values("p")
M=len(res); bonf=0.05/M
res["bonf"]=np.where(res.p<bonf,"yes","no")
rank=res.p.rank(method="first").astype(int); th=(rank/M)*0.05
mx=max([r for r,pv,t in zip(rank,res.p,th) if pv<=t]+[0]); res["bh"]=np.where(rank<=mx,"yes","no")
print(f"STATISTICS on n=64  ({M} tests, Bonferroni alpha={bonf:.4f})\n")
print(f"{'Feature':<19}{'Test':<12}{'Stat':>8}{'p':>9}  {'Effect':<9}{'95% CI':<17}{'Bonf':>5}{'BH':>4}")
print("-"*90)
for _,r in res.iterrows():
    ps="<0.001" if r.p<0.001 else f"{r.p:.3f}"
    print(f"{r.feature:<19}{r.test:<12}{r.stat:>8}{ps:>9}  {r.eff:<9}{r.ci:<17}{r.bonf:>5}{r.bh:>4}")
print()
for _,r in res.iterrows(): print(f"   {r.feature}: {r.note}")

X=m64[NUM+CAT]; y=m64["label"]
pre=ColumnTransformer([("n",Pipeline([("i",SimpleImputer(strategy="median")),("s",StandardScaler())]),NUM),
                       ("c",Pipeline([("i",SimpleImputer(strategy="most_frequent")),("o",OneHotEncoder(handle_unknown="ignore"))]),CAT)])
pw=(y==0).sum()/(y==1).sum()
mods={"Logistic Regression":LogisticRegression(max_iter=1000,class_weight='balanced',random_state=42),
 "Decision Tree":DecisionTreeClassifier(class_weight='balanced',random_state=42),
 "Random Forest":RandomForestClassifier(n_estimators=200,class_weight='balanced',random_state=42),
 "KNN":KNeighborsClassifier(n_neighbors=5),"SVM":SVC(probability=True,class_weight='balanced',random_state=42),
 "XGBoost":XGBClassifier(n_estimators=200,scale_pos_weight=pw,eval_metric='logloss',random_state=42,verbosity=0),
 "LightGBM":LGBMClassifier(n_estimators=200,class_weight='balanced',random_state=42,verbose=-1),
 "MLP":MLPClassifier(hidden_layer_sizes=(64,32),max_iter=500,random_state=42,early_stopping=True)}
mods["Soft-Voting Ensemble"]=VotingClassifier([("lr",LogisticRegression(max_iter=1000,class_weight='balanced',random_state=42)),
 ("rf",RandomForestClassifier(n_estimators=200,class_weight='balanced',random_state=42)),
 ("svm",SVC(probability=True,class_weight='balanced',random_state=42)),
 ("xgb",XGBClassifier(n_estimators=200,scale_pos_weight=pw,eval_metric='logloss',random_state=42,verbosity=0))],voting="soft")
cv=StratifiedKFold(5,shuffle=True,random_state=42)
print(f"\n\nMODELS on n=64\n{'Classifier':<24}{'CV F1':>8}{'SD':>8}")
sc_all={}
for n_,c in mods.items():
    s=cross_val_score(Pipeline([("p",pre),("m",c)]),X,y,cv=cv,scoring="f1"); sc_all[n_]=(s.mean(),s.std())
    print(f"{n_:<24}{s.mean():>8.3f}{s.std():>8.3f}")

rf=Pipeline([("p",pre),("m",RandomForestClassifier(n_estimators=200,class_weight='balanced',random_state=42))]).fit(X,y)
names=NUM+list(rf.named_steps['p'].named_transformers_['c'].named_steps['o'].get_feature_names_out(CAT))
agg={}
for n_,v in zip(names,rf.named_steps['m'].feature_importances_):
    base=n_ if n_ in NUM else next((c for c in CAT if n_.startswith(c)),n_)
    agg[base]=agg.get(base,0)+v
print("\nFeature importance:")
for f,v in sorted(agg.items(),key=lambda t:-t[1]): print(f"   {f:<20}{v:.3f}")

oof=cross_val_predict(Pipeline([("p",pre),("m",RandomForestClassifier(n_estimators=200,class_weight='balanced',random_state=42))]),
                      X,y,cv=cv,method="predict_proba")[:,1]*100
m64["risk"]=oof; act=m64[m64.label==0]
hi=(act.risk>=67).sum(); md=((act.risk>=33)&(act.risk<67)).sum(); lo=(act.risk<33).sum()
print(f"\nEWS (out-of-fold, 22 active): High={hi} ({hi/22*100:.0f}%)  Medium={md} ({md/22*100:.0f}%)  Low={lo} ({lo/22*100:.0f}%)")
hr=act[act.risk>=67]
print(f"  risk range {act.risk.min():.0f}-{act.risk.max():.0f}%; high-risk scores: {', '.join(f'{v:.0f}%' for v in sorted(hr.risk,reverse=True))}")
for f in ["dsa_grade","upsolving_habit","mentor_support","thought_quit"]:
    print(f"  {f:<16}: {dict(hr[f].value_counts())}")
