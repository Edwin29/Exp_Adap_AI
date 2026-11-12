import pandas as pd, numpy as np
g=pd.read_pickle("out/gamelev.pkl"); a=g[g.prio=="A"].copy()
# Use game index blocks of 100 games instead of months (experience axis)
a["blk"]=(a.k-1)//100
cnt=a.groupby("p").size(); ppl=cnt[cnt>=400].index; a=a[a.p.isin(ppl)]
rng=np.random.default_rng(11)
def slope(t,y,w):
    df=pd.DataFrame({"t":t,"y":y*w,"w":w}).groupby("t").sum(); x=df.index.values.astype(float); m=(df.y/df.w).values
    x=x-x.mean(); return (x*(m-m.mean())).sum()/(x*x).sum()
res=[]
for p,d in a.groupby("p"):
    t=d.blk.values; n=d.n.values
    for name,y in [("acc",d.acc.values),("per",100*d.per.values/n),("pos",100*d.pos.values/n),("tac",100*d.tac.values/n)]:
        s=slope(t,y,n); null=np.array([slope(rng.permutation(t),y,n) for _ in range(300)])
        res.append((p,name,s,(np.abs(null)>=abs(s)).mean(),null.std(),len(d)))
R=pd.DataFrame(res,columns=["p","m","slope","pval","nullsd","games"]); R.to_csv("out/direction_A.csv",index=False)
print("A people with >=400 games:",len(ppl),"median games",cnt[ppl].median())
for m,d in R.groupby("m"):
    sig=d.pval<0.05; good=d.slope>0 if m=="acc" else d.slope<0
    print(m,"median slope/100g",round(d.slope.median(),4),"nullsd",round(d.nullsd.median(),4),"improve",round((sig&good).mean(),3),"decline",round((sig&~good).mean(),3),"flat",round((~sig).mean(),3))
w=R.pivot(index="p",columns="m",values="slope"); print(w.corr().round(2))
# curve shape: pooled by block for these people (balanced up to block 4)
c=a[a.blk<=9].groupby("blk").apply(lambda d:pd.Series({"people":d.p.nunique(),"acc":(d.acc*d.n).sum()/d.n.sum(),"per":100*d.per.sum()/d.n.sum(),"pos":100*d.pos.sum()/d.n.sum(),"tac":100*d.tac.sum()/d.n.sum()}))
print(c.round(3))
