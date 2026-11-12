import pandas as pd, numpy as np
A=pd.read_pickle("A_typ.pkl"); out=pd.read_pickle("pred_out.pkl")
O=pd.read_pickle("/tmp/claude-0/ana12/meta.pkl"); O["month"]=O.ts.dt.month
def wmean(v,w): return (v*w).sum()/w.sum()
J=A[A.month==1].copy(); J["day"]=J.ts.dt.floor("D")
gap=J.groupby("p").ts.diff().dt.total_seconds()/60; J["sess"]=(gap.isna()|(gap>30)).groupby(J.p).cumsum()
F=J.groupby("p").apply(lambda d:pd.Series({
 "jan_acc":wmean(d.acc,d.n),"jan_per":100*d.per.sum()/d.n.sum(),"jan_pos":100*d.pos.sum()/d.n.sum(),"jan_tac":100*d.tac.sum()/d.n.sum(),
 "log_jan_games":np.log2(len(d)),"games_per_active_day":len(d)/d.day.nunique(),"active_days":d.day.nunique(),
 "sess_len":d.groupby("sess").size().mean(),"win_rate":d.result_for_p.astype(float).mean(),
 "elo_change":float(d.elo.iloc[-1])-float(d.elo.iloc[0]),"moves_per_game":d.n.mean()}))
Oj=O[O.month==1].groupby("username").apply(lambda d:pd.Series({"n_oth":len(d),"n_slow":d.speed.isin(["rapid","classical","correspondence"]).sum(),"n_bul":d.speed.isin(["bullet","ultraBullet"]).sum(),"n_var":(d.variant!="standard").sum()}))
F=F.join(Oj).fillna(0); tot=F.n_oth+2**F.log_jan_games
F["share_other"]=F.n_oth/tot; F["share_slow"]=F.n_slow/tot; F["share_bullet"]=F.n_bul/tot; F["share_variant"]=F.n_var/tot
F=F.drop(columns=["n_oth","n_slow","n_bul","n_var"])
res={}
for y,m,n,np_,rmse,g in out:
    if m=="d2_날짜+모든대국":
        res[y]=g.assign(r=g.obs-g.pred).groupby("p").r.mean()
T=F.join(pd.DataFrame({"off_acc":res["acc"],"off_per":res["per100"]})).dropna()
print("people",len(T)); print("offset sd: acc",round(T.off_acc.std(),3),"per",round(T.off_per.std(),3))
cols=[c for c in F.columns]
Z=(T[cols]-T[cols].mean())/T[cols].std()
print(pd.DataFrame({"r_acc":Z.corrwith(T.off_acc),"r_per":Z.corrwith(T.off_per)}).round(2).sort_values("r_acc"))
# CV ridge
rng=np.random.default_rng(0); fold=rng.permutation(len(T))%5
for yv in ["off_acc","off_per"]:
    for lam in [1,5,20]:
        pred=np.zeros(len(T))
        for f in range(5):
            tr=fold!=f; X=Z.values[tr]; yy=T[yv].values[tr]; mu=yy.mean()
            b=np.linalg.solve(X.T@X+lam*np.eye(X.shape[1]),X.T@(yy-mu)); pred[~tr]=Z.values[~tr]@b+mu
        r2=1-((T[yv]-pred)**2).sum()/((T[yv]-T[yv].mean())**2).sum(); print(yv,"ridge lam",lam,"CV R2",round(r2,3))
T.to_csv("offset_features.csv")
