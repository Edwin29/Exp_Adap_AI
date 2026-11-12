import pandas as pd, numpy as np
d=pd.read_pickle("/tmp/claude-0/ana7/beg.pkl").sort_values(["p","ts"])
n=d.groupby("p").size(); ok=sorted(n[n>=150].index); print("eligible",len(ok))
rng=np.random.default_rng(21); sel=rng.choice(ok,120,replace=False)
W=d[d.p.isin(sel)&(d.k>=31)&(d.k<=150)].assign(win="seq")[["site","p","color","group","win","elo","oppelo","score","k","month","ka_clean","dlast10","term"]]
W.to_csv("wanted.csv",index=False); print(len(W), W.groupby("p").size().describe())
