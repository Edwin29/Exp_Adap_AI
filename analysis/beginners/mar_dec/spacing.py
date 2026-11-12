import pandas as pd, numpy as np
g=pd.read_pickle("/tmp/claude-0/ana10/out/gamelev.pkl"); g=g[g.prio=="A"].copy()
g["ts"]=pd.to_datetime(g.utc_datetime); g=g.sort_values(["p","ts"]); g["day"]=g.ts.dt.floor("D")
g["perv"]=100*g.per/g.n
def build(S):
    rows=[]
    for p,d in g.groupby("p"):
        d=d.reset_index(drop=True); nb=len(d)//S
        if nb<3: continue
        bl=[d.iloc[i*S:(i+1)*S] for i in range(nb)]
        st=[{"acc":(b.acc*b.n).sum()/b.n.sum(),"per":100*b.per.sum()/b.n.sum(),"days":b.day.nunique(),
             "span":(b.ts.iloc[-1]-b.ts.iloc[0]).total_seconds()/86400,"t0":b.ts.iloc[0],"t1":b.ts.iloc[-1]} for b in bl]
        for t in range(1,nb-1):
            a,m,c=st[t-1],st[t],st[t+1]
            rows.append(dict(p=p,t=t,dacc=c["acc"]-a["acc"],dper=c["per"]-a["per"],days=m["days"],span=m["span"],
                gap_in=(m["t0"]-a["t1"]).total_seconds()/86400,gap_out=(c["t0"]-m["t1"]).total_seconds()/86400,acc_mid=m["acc"]))
    return pd.DataFrame(rows)
def fe_ols(X,y,grp):
    Xd=X-X.groupby(grp).transform("mean"); yd=y-y.groupby(grp).transform("mean")
    b=np.linalg.lstsq(Xd.values,yd.values,rcond=None)[0]; return b
rng=np.random.default_rng(5)
for S in [50,100]:
    R=build(S); R["ldays"]=np.log2(R.days); R["lt"]=np.log(R.t); R["lgi"]=np.log2(1+R.gap_in); R["lgo"]=np.log2(1+R.gap_out)
    print(f"== block {S} games: {len(R)} triples, {R.p.nunique()} people; distinct days in middle block median {R.days.median()} IQR {R.days.quantile(.25)}-{R.days.quantile(.75)}")
    for yv in ["dacc","dper"]:
        for cols in [["ldays","lt"],["ldays","lt","lgi","lgo"]]:
            b=fe_ols(R[cols],R[yv],R.p)
            ps=R.p.unique(); boots=[]
            for _ in range(300):
                s=rng.choice(ps,len(ps)); B=pd.concat([R[R.p==q].assign(pb=i) for i,q in enumerate(s)])
                boots.append(fe_ols(B[cols],B[yv],B.pb))
            se=np.std(boots,axis=0)
            print(f"  {yv} ~ {'+'.join(cols)}: " + ", ".join(f"{c} {b[i]:+.3f}±{se[i]:.3f}" for i,c in enumerate(cols)))
    # simple contrast: bottom vs top quartile of within-person-centered spread
    R["ld_c"]=R.ldays-R.groupby("p").ldays.transform("mean")
    q=pd.qcut(R.ld_c,4,labels=["몰아 둠","2","3","나눠 둠"])
    print(R.groupby(q).agg(n=("dacc","size"),days=("days","median"),dacc=("dacc","mean"),dper=("dper","mean")).round(3))
    R.to_csv(f"spacing_S{S}.csv",index=False)
