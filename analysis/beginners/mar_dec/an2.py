import pandas as pd, numpy as np, json
g=pd.read_pickle("out/gamelev.pkl"); c=g[g.mk<=20].copy()
mi={m:i for i,m in enumerate(sorted(c.month.unique()))}; c["t"]=c.month.map(mi)
cnt=c.groupby(["p","month"]).size()
ok=cnt[cnt>=15].reset_index().groupby("p").size(); ppl=ok[ok>=4].index
c=c[c.p.isin(ppl)]; c=c.merge(cnt[cnt>=15].rename("cm").reset_index()[["p","month"]],on=["p","month"])
rng=np.random.default_rng(7)
def slope(t,y,w):
    # weighted monthly means then OLS on month index
    df=pd.DataFrame({"t":t,"y":y*w,"w":w}).groupby("t").sum(); x=df.index.values.astype(float); m=(df.y/df.w).values
    x=x-x.mean(); return (x*(m-m.mean())).sum()/(x*x).sum()
res=[]
for p,d in c.groupby("p"):
    t=d.t.values; n=d.n.values
    for name,y,w in [("acc",d.acc.values,n),("per",100*d.per.values/n,n),("pos",100*d.pos.values/n,n)]:
        s=slope(t,y,w); null=np.array([slope(rng.permutation(t),y,w) for _ in range(300)])
        res.append((p,name,s,(np.abs(null)>=abs(s)).mean(),null.std()))
    # elo change: median elo of first active month vs last
    em=d.groupby("t").elo.median(); res.append((p,"elo",em.iloc[-1]-em.iloc[0],np.nan,np.nan))
R=pd.DataFrame(res,columns=["p","m","slope","pval","nullsd"])
R.to_csv("out/direction.csv",index=False)
print("people",len(ppl))
for m,d in R.groupby("m"):
    if m=="elo":
        print("elo first->last month median change",d.slope.median(),"q25/q75",d.slope.quantile([.25,.75]).tolist(),"<-50",(d.slope<-50).mean().round(3),">+50",(d.slope>50).mean().round(3)); continue
    sig=d.pval<0.05; good= d.slope>0 if m=="acc" else d.slope<0
    print(m,"median slope/month",round(d.slope.median(),4),"improve",round((sig&good).mean(),3),"decline",round((sig&~good).mean(),3),"flat",round((~sig).mean(),3),"(null expects 0.025/0.025)")
# per-person: early ability vs change
a=R[R.m=="acc"].set_index("p"); first=c[c.t==c.groupby("p").t.transform("min")].groupby("p").apply(lambda d:(d.acc*d.n).sum()/d.n.sum())
a["first"]=first; print("corr(first acc, acc slope)",round(a["first"].corr(a.slope),3))
# overlap: same people improve on acc and per?
w=R[R.m!="elo"].pivot(index="p",columns="m",values="slope"); print(w.corr().round(3))
