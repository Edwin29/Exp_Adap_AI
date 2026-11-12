import pandas as pd, numpy as np
A=pd.read_pickle("A.pkl"); A["day"]=A.ts.dt.floor("D")
rng=np.random.default_rng(5)
def build(S):
    rows=[]
    for p,d in A.groupby("p"):
        d=d.reset_index(drop=True); nb=len(d)//S
        st=[]
        for i in range(nb):
            b=d.iloc[i*S:(i+1)*S]
            st.append(dict(acc=(b.acc*b.n).sum()/b.n.sum(),per=100*b.per.sum()/b.n.sum(),days=b.day.nunique(),
                t0=b.ts.iloc[0],t1=b.ts.iloc[-1],k=b.k.iloc[-1],oth=b.k_other.iloc[-1]-b.k_other.iloc[0]))
        for t in range(1,nb-1):
            a,m,c=st[t-1],st[t],st[t+1]
            rows.append(dict(p=p,t=t,k=m["k"],dacc=c["acc"]-a["acc"],dper=c["per"]-a["per"],days=m["days"],oth=m["oth"],
                elapsed=(c["t0"]-a["t1"]).total_seconds()/86400))
    return pd.DataFrame(rows)
def fe(X,y,g):
    Xd=X-X.groupby(g).transform("mean"); yd=y-y.groupby(g).transform("mean"); return np.linalg.lstsq(Xd.values,yd.values,rcond=None)[0]
def run(R,cols,yv):
    b=fe(R[cols],R[yv],R.p); ps=R.p.unique(); bs=[]
    for _ in range(300):
        s=rng.choice(ps,len(ps)); B=pd.concat([R[R.p==q].assign(pb=i) for i,q in enumerate(s)]); bs.append(fe(B[cols],B[yv],B.pb))
    se=np.std(bs,axis=0); return ", ".join(f"{c} {b[i]:+.3f}±{se[i]:.3f}" for i,c in enumerate(cols))
R=build(50); R["ldays"]=np.log2(R.days); R["lt"]=np.log(R.t); R["loth"]=np.log2(R.oth+1); R["lel"]=np.log2(R.elapsed)
R.to_csv("spacing50_all.csv",index=False)
for name,sub in [("steep: blitz games<=600",R[R.k<=600]),("later: >600",R[R.k>600])]:
    print("==",name,len(sub),"triples",sub.p.nunique(),"people; days median",sub.days.median(),"IQR",sub.days.quantile([.25,.75]).tolist())
    for yv in ["dacc","dper"]:
        print("  ",yv,run(sub,["ldays","lt"],yv)); print("  ",yv,run(sub,["ldays","loth","lt"],yv))
    sub=sub.copy(); sub["c"]=sub.ldays-sub.groupby("p").ldays.transform("mean")
    print(sub.groupby(pd.qcut(sub.c,4,labels=["몰아","2","3","나눠"])).agg(n=("dacc","size"),days=("days","median"),dacc=("dacc","mean"),dper=("dper","mean")).round(3))
