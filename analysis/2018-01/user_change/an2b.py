import pandas as pd, numpy as np, json
d=pd.read_pickle("feat.pkl"); d["bin"]=((d.k-1)//25)*25+1
rng=np.random.default_rng(1)
def zstats(d):
    out=[]
    for p,g in d.groupby("p",sort=False):
        a=g[g.k<=50].castle10.dropna(); b=g[(g.k>100)&(g.k<=150)].castle10.dropna()
        if len(a)<30 or len(b)<30: continue
        pp=(a.sum()+b.sum())/(len(a)+len(b))
        if not 0<pp<1: continue
        se=np.sqrt(pp*(1-pp)*(1/len(a)+1/len(b)))
        out.append((g.group.iloc[0],(b.mean()-a.mean())/se))
    return pd.DataFrame(out,columns=["group","z"])
obs=zstats(d)
null=[]
for r in range(0):
    s=d.copy()
    s["castle10"]=s.groupby("p").castle10.transform(lambda x: x.sample(frac=1,random_state=int(rng.integers(1e9))).values)
    z=zstats(s); null.append(z.groupby("group").z.agg(lambda x:(x.abs()>2).mean()))
null=pd.DataFrame()
print("obs |z|>2:",obs.groupby("group").z.agg(lambda x:(x.abs()>2).mean()).to_dict())

print("obs sd z",obs.groupby("group").z.std().to_dict())
# balanced panel: players with >=300 games
bp=d.groupby("p").k.max(); bp=bp[bp>=300].index
P=d[d.p.isin(bp)&(d.k<=300)]
print("balanced players", P.groupby("group").p.nunique().to_dict())
Bp=P.groupby(["group","bin"]).agg(castle10=("castle10","mean"),mated=("mated","mean"),elo=("elo","median"),checks=("checks_recv","mean")).reset_index()
Bp.to_csv("bins_balanced.csv",index=False); print(Bp.to_string())
# event study with residualized castle10 (player x color mean removed)
d["c10r"]=d.castle10-d.groupby(["p","color"]).castle10.transform("mean")
rows=[]
for p,g in d.groupby("p",sort=False):
    c=g.c10r.values; lt=g["lt"].values; grp=g.group.iloc[0]
    for i in range(10,len(g)-5):
        if lt[i] in ("mated","resign","time","win"):
            post=np.nanmean(c[i+1:i+6]); pre=np.nanmean(c[i-4:i+1]) if False else np.nanmean(c[i-5:i]); pre2=np.nanmean(c[i-10:i-5])
            rows.append((grp,lt[i],post-pre,pre-pre2))
E=pd.DataFrame(rows,columns=["group","type","post_minus_pre","pretrend"])
ES=E.groupby(["type"]).agg(n=("post_minus_pre","size"),eff=("post_minus_pre","mean"),se=("post_minus_pre",lambda x:x.std()/np.sqrt(len(x))),
    pre=("pretrend","mean"),pre_se=("pretrend",lambda x:x.std()/np.sqrt(len(x))))
print(ES.to_string()); ES.to_csv("event.csv")
ESg=E.groupby(["group","type"]).agg(n=("post_minus_pre","size"),eff=("post_minus_pre","mean"),se=("post_minus_pre",lambda x:x.std()/np.sqrt(len(x)))); print(ESg.to_string())
ESg.to_csv("event_by_group.csv")
obs.to_csv("obs_z.csv",index=False)
