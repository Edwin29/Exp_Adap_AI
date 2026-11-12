import pandas as pd, numpy as np
d=pd.read_pickle("beg.pkl")
c=d.groupby(["p","month"]).size().unstack(fill_value=0)
ok=sorted(c[(c[1]>=60)&(c[2]>=40)].index); print("eligible",len(ok))
rng=np.random.default_rng(7); sel=rng.choice(ok,min(150,len(ok)),replace=False)
rows=[]
for p in sel:
    x=d[d.p==p]; j=x[x.month==1]; f=x[x.month==2]
    rows+= [j.head(20).assign(win="jan_early"), j.tail(20).assign(win="jan_late"), f.tail(20).assign(win="feb_late")]
W=pd.concat(rows)[["site","p","color","group","win","elo","oppelo","score","km","month"]]
W.to_csv("wanted.csv",index=False); print(len(W))
