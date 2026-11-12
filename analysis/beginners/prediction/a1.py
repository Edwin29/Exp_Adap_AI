import pandas as pd, numpy as np
exec(open("pred.py").read().split("rng=np.random")[0])
O=pd.read_pickle("/tmp/claude-0/ana12/meta.pkl"); O=O[O.username.isin(ppl)]
O["typ"]=np.select([O.opp_is_ai==True,O.variant!="standard",O.speed.isin(["bullet","ultraBullet"]),O.speed.isin(["rapid","classical","correspondence"])],["ai","variant","bullet","slow"],"casualblitz")
for t in ["bullet","slow","casualblitz","variant","ai"]:
    A["c_"+t]=0.0
    for p,d in A.groupby("p"):
        o=np.sort(O[(O.username==p)&(O.typ==t)].ts.values); A.loc[d.index,"c_"+t]=np.searchsorted(o,d.ts.values)
    A["l_"+t]=np.log2(1+A["c_"+t])
A.to_pickle("A_typ.pkl")
sh=pd.read_csv("/tmp/claude-0/ana12/other_share.csv",index_col=0).share_other
janN=A[A.month==1].groupby("p").size()
print("Jan blitz games by group:",pd.Series(janN).groupby(pd.cut(sh.reindex(janN.index),[-1,.05,.3,1.1])).median().to_dict())
rng=np.random.default_rng(1); folds=dict(zip(ppl,rng.permutation(len(ppl))%5))
def fe_lin(d,cols,y):
    w=d.n.values; X=d[cols]; Xd=X-X.groupby(d.p).transform("mean"); yd=d[y]-d.groupby("p")[y].transform("mean")
    sw=np.sqrt(w); return np.linalg.lstsq(Xd.values*sw[:,None],yd.values*sw,rcond=None)[0]
def run(y,typed,base_last=None):
    L=[]
    for f in range(5):
        tr=A[A.p.map(folds)!=f].copy(); te=A[A.p.map(folds)==f].copy()
        eff=fit_h(tr,["ld","lka"] if not typed else ["ld","lk"],y)
        tr["hh"]=h(tr,eff); te["hh"]=h(te,eff)
        if typed:
            cols=["l_bullet","l_slow","l_casualblitz","l_variant","l_ai"]
            tr["r"]=tr[y]-tr.hh; b=fe_lin(tr.assign(**{y+"_r":tr.r}),cols,y+"_r")
            te["hh"]=te.hh+te[cols].values@b
        j=te[te.month==1]
        if base_last: j=j.groupby("p").tail(base_last)
        a=j.groupby("p").apply(lambda j:wmean(j[y]-j.hh,j.n))
        q=te[te.month>=3].copy(); q["pred"]=q.p.map(a)+q.hh; L.append(q)
    q=pd.concat(L); g=q.groupby(["p","month"]).apply(lambda d:pd.Series({"obs":wmean(d[y],d.n),"pred":wmean(d.pred,d.n),"games":len(d)})).reset_index(); g=g[g.games>=20]
    g["r"]=g.obs-g.pred; g["grp"]=pd.cut(g.p.map(sh),[-1,.05,.3,1.1],labels=["blitzonly","mid","otherheavy"])
    return np.sqrt((g.r**2).mean()), g.groupby("grp").r.agg(["mean",lambda r:(r**2).mean()]).round(3)
for y in ["acc","per100"]:
    for name,kw in [("d2 기본",{}),("d2, 1월 마지막 50판만으로 출발점",{"base_last":50}),("종류별 무게",{"typed":True})]:
        r,t=run(y,kw.get("typed",False),kw.get("base_last")); print(y,name,"RMSE",round(r,3)); print(t.to_string())
    if True:
        tr=A.copy(); eff=fit_h(tr,["ld","lk"],y); tr["hh"]=h(tr,eff); tr["r"]=tr[y]-tr.hh
        b=fe_lin(tr.assign(rr=tr.r),["l_bullet","l_slow","l_casualblitz","l_variant","l_ai"],"rr")
        print(y,"type weights per doubling (all data, FE):",dict(zip(["bullet","slow","casualblitz","variant","ai"],np.round(b,3))))
