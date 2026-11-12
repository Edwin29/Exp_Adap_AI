import pandas as pd, numpy as np
A=pd.read_pickle("/tmp/claude-0/ana12/A.pkl"); A=A[A.n>=5].copy()
sh=pd.read_csv("/tmp/claude-0/ana12/other_share.csv",index_col=0).share_other
for c in ["acc","per","n","k","k_all","days"]: A[c]=A[c].astype(float)
A["month"]=A.ts.dt.month; A["per100"]=100*A.per/A.n
A["lk"]=np.log2(A.k); A["lka"]=np.log2(A.k_all); A["ld"]=np.log2(A.days+1)
jan=A[A.month==1]; ok=jan.groupby("p").size(); ppl=ok[ok>=50].index
A=A[A.p.isin(ppl)]
BINS={"ld":np.arange(0,9.1,0.5),"lk":np.arange(0,13.1,0.5),"lka":np.arange(0,13.6,0.5)}
def fit_h(d,xs,y):
    # additive binned curves with person FE, by alternating projections; returns dict of bin effects
    d=d.copy(); r=d[y]-d.groupby("p")[y].transform("mean"); eff={x:pd.Series(0.0,index=range(len(BINS[x])+1)) for x in xs}
    for x in xs: d["b_"+x]=np.digitize(d[x],BINS[x])
    w=d.n.astype(float)
    for it in range(15):
        for x in xs:
            other=sum(d["b_"+o].map(eff[o]) for o in xs if o!=x) if len(xs)>1 else 0
            res=d[y]-other; a=(res*w).groupby(d.p).sum()/w.groupby(d.p).sum(); res=res-d.p.map(a)
            e=(res*w).groupby(d["b_"+x]).sum()/w.groupby(d["b_"+x]).sum(); eff[x]=e.astype(float).reindex(range(len(BINS[x])+1)).interpolate(limit_direction="both").fillna(0)
    return eff
def h(d,eff):
    t=pd.Series(0.0,index=d.index)
    for x in eff: t=t+pd.Series(np.digitize(d[x],BINS[x]),index=d.index).map(eff[x]).astype(float)
    return t
def wmean(v,w): return (v*w).sum()/w.sum()
rng=np.random.default_rng(1); folds=dict(zip(ppl,rng.permutation(len(ppl))%5))
MODELS={"a_변화없음":[],"b_날짜":["ld"],"c_블리츠판수":["lk"],"d_모든대국수":["lka"],"d2_날짜+모든대국":["ld","lka"]}
out=[]
for y in ["acc","per100"]:
    preds={m:[] for m in list(MODELS)+["e_d2+개인기울기"]}
    for f in range(5):
        tr=A[A.p.map(folds)!=f]; te=A[A.p.map(folds)==f]
        for m,xs in MODELS.items():
            eff=fit_h(tr,xs,y) if xs else {}
            te2=te.copy(); te2["hh"]=h(te2,eff) if xs else 0.0
            if m=="d2_날짜+모든대국":
                # personal slope on residual vs lka, shrink lambda chosen on train
                trh=tr.copy(); trh["hh"]=h(trh,eff)
                def slopes(d):
                    j=d[d.month==1]; r=j[y]-j.hh; x=j.lka-j.lka.mean(); 
                    return pd.Series({"a":wmean(r,j.n),"b":(x*(r-r.mean())*j.n).sum()/((x*x*j.n).sum()+1e-9),"xm":j.lka.mean()})
                best=None
                St=trh.groupby("p").apply(slopes)
                for lam in [0,.1,.25,.5,1]:
                    q=trh[trh.month>=3].join(St,on="p"); pr=q.a+q.hh+lam*q.b*(q.lka-q.xm)
                    err=((q[y]-pr)**2*q.n).sum()
                    if best is None or err<best[0]: best=(err,lam)
                lam=best[1]; Se=te2.groupby("p").apply(slopes); q=te2[te2.month>=3].join(Se,on="p")
                q=q.assign(pred=q.a+q.hh+lam*q.b*(q.lka-q.xm)); preds["e_d2+개인기울기"].append(q[["p","month","n",y,"pred"]].assign(lam=lam))
            a=te2[te2.month==1].groupby("p").apply(lambda j:wmean(j[y]-j.hh,j.n))
            q=te2[te2.month>=3].copy(); q["pred"]=q.p.map(a)+q.hh; preds[m].append(q[["p","month","n",y,"pred"]])
    for m,L in preds.items():
        q=pd.concat(L); g=q.groupby(["p","month"]).apply(lambda d:pd.Series({"obs":wmean(d[y],d.n),"pred":wmean(d.pred,d.n),"games":len(d)})).reset_index()
        g=g[g.games>=20]; g["se2"]=(g.obs-g.pred)**2
        out.append((y,m,len(g),g.p.nunique(),np.sqrt(g.se2.mean()),g.assign(sh=g.p.map(sh))))
        print(y,m,"person-months",len(g),"RMSE",round(np.sqrt(g.se2.mean()),3),("lam="+str(pd.concat(L).lam.mean().round(2))) if "lam" in pd.concat(L) else "")
pd.to_pickle(out,"pred_out.pkl")
# noise floor: sampling variance of monthly mean (bootstrap games)
for y in ["acc","per100"]:
    m=A[A.month>=3]; v=[]
    for (p,mo),d in m.groupby(["p","month"]):
        if len(d)<20: continue
        bs=[wmean(*(lambda s:(s[y],s.n))(d.sample(len(d),replace=True,random_state=i))) for i in range(100)]
        v.append(np.var(bs))
    print(y,"noise floor RMSE",round(np.sqrt(np.mean(v)),3))
