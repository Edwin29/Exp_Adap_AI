import pandas as pd, numpy as np
d=pd.read_pickle("/tmp/claude-0/ana5/feat_jf.pkl")
c=d.groupby(["p","month"]).size().unstack(fill_value=0)
ok=c[(c[1]>=40)&(c[2]>=40)].index
g=d.groupby("p").group.first()
rng=np.random.default_rng(42)
new=rng.choice(sorted([p for p in ok if g[p]=="new"]),100,replace=False)
est=rng.choice(sorted([p for p in ok if g[p]=="est"]),50,replace=False)
print(len([p for p in ok if g[p]=="new"]),len([p for p in ok if g[p]=="est"]))
rows=[]
for p in list(new)+list(est):
    x=d[d.p==p]
    a=x[x.month==1].head(20).assign(win="jan_early"); b=x[x.month==2].tail(20).assign(win="feb_late")
    rows.append(pd.concat([a,b])[["site","p","color","group","win","elo","oppelo","score","km","month"]])
W=pd.concat(rows); W.to_csv("wanted.csv",index=False); print(len(W), W.groupby(["group","win"]).size())
