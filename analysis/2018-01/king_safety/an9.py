import pandas as pd, numpy as np, json
d=pd.read_pickle("feat4.pkl"); m="delayq_rate"
rng=np.random.default_rng(3)
# expected level by elo (game-level regression on elo bins)
eb=pd.cut(d.elo,np.arange(600,2700,100)); exp=d.groupby(eb,observed=True)[m].mean(); d["exp"]=eb.map(exp).astype(float)
def stats(dd,w1,w2,minn=20):
    out=[]
    for p,g in dd.groupby("p",sort=False):
        a=g[(g.k>w1[0])&(g.k<=w1[1])]; b=g[(g.k>w2[0])&(g.k<=w2[1])]
        a1=a[m].dropna(); b1=b[m].dropna()
        if len(a1)<minn or len(b1)<minn: continue
        gap0=a1.mean()-a.exp.mean()   # above expected level for own rating at start
        out.append((p,a1.mean(),b1.mean()-a1.mean(),gap0))
    return pd.DataFrame(out,columns=["p","start","chg","gap0"])
R={}
for name,w1,w2 in (("1-50 vs 101-150",(0,50),(100,150)),("1-100 vs 201-300",(0,100),(200,300))):
    o=stats(d,w1,w2)
    nulls=[]
    for r in range(10):
        s=d.copy(); s[m]=s.groupby("p")[m].transform(lambda x: x.sample(frac=1,random_state=int(rng.integers(1e9))).values)
        n=stats(s,w1,w2); nulls.append((np.corrcoef(n.start,n.chg)[0,1],np.corrcoef(n.gap0,n.chg)[0,1],(n.chg*-np.sign(n.gap0)>0).mean()))
    nl=np.array(nulls)
    R[name]={"players":len(o),"mean_chg":float(o.chg.mean()),
      "corr_start_chg":float(np.corrcoef(o.start,o.chg)[0,1]),"null_corr_start_chg":[float(nl[:,0].mean()),float(nl[:,0].min()),float(nl[:,0].max())],
      "corr_gap_chg":float(np.corrcoef(o.gap0,o.chg)[0,1]),"null_corr_gap_chg":[float(nl[:,1].mean()),float(nl[:,1].min()),float(nl[:,1].max())],
      "frac_toward_expected":float((o.chg*-np.sign(o.gap0)>0).mean()),"null_frac_toward":[float(nl[:,2].mean()),float(nl[:,2].min()),float(nl[:,2].max())]}
# long players: trajectory slope per 100 games and sign consistency between halves
L=d.groupby("p").k.max(); lp=L[L>=300].index
sl=[]
for p in lp:
    g=d[(d.p==p)&(d.k<=300)].dropna(subset=[m])
    if len(g)<150: continue
    q=[g[(g.k>i)&(g.k<=i+100)][m].mean() for i in (0,100,200)]
    sl.append(q)
S=np.array(sl); c1=S[:,1]-S[:,0]; c2=S[:,2]-S[:,1]
R["300plus"]={"players":len(S),"means_by_100":S.mean(0).round(4).tolist(),"corr_chg1_chg2":float(np.corrcoef(c1,c2)[0,1]),"same_sign":float((np.sign(c1)==np.sign(c2)).mean())}
print(json.dumps(R,indent=1)); json.dump(R,open("trend.json","w"),indent=1)
