import pandas as pd, numpy as np, json
d=pd.read_pickle("feat4.pkl")
rng=np.random.default_rng(0)
import sys; M=sys.argv[1].split(",")
# 1) individual change z (games 1-50 vs 101-150), Welch on per-game values; shuffle null
def zs(dd,m):
    out={}
    for p,g in dd.groupby("p",sort=False):
        a=g.loc[g.k<=50,m].dropna(); b=g.loc[(g.k>100)&(g.k<=150),m].dropna()
        if len(a)<20 or len(b)<20: continue
        se=np.sqrt(a.var()/len(a)+b.var()/len(b))
        if se>0: out[p]=(b.mean()-a.mean())/se
    return pd.Series(out)
R={}
for m in M:
    oz=zs(d,m); nulls=[]
    for r in range(10):
        s=d[["p","k",m]].copy()
        s[m]=s.groupby("p")[m].transform(lambda x: x.sample(frac=1,random_state=int(rng.integers(1e9))).values)
        nulls.append(zs(s,m))
    nz=pd.concat(nulls)
    g=d.groupby("p").group.first()
    R[m]={"n":len(oz),"obs_gt2":float((oz.abs()>2).mean()),"null_gt2":float((nz.abs()>2).mean()),
          "null_gt2_p95":float(np.percentile([(x.abs()>2).mean() for x in nulls],95)),
          "by_group":{k:float((oz[g.reindex(oz.index)==k].abs()>2).mean()) for k in ("est","new")},
          "sd_obs":float(oz.std()),"sd_null":float(nz.std())}
    oz.rename("z").to_csv(f"z4_{m}.csv"); nz.rename("z").to_csv(f"znull4_{m}.csv")
print(json.dumps(R,indent=1))
json.dump(R,open("indiv4_"+"_".join(M)+".json","w"),indent=1)
