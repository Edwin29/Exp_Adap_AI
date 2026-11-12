import pandas as pd, numpy as np
A=pd.read_pickle("A_typ.pkl")
O=pd.read_pickle("/tmp/claude-0/ana12/meta.pkl"); O["month"]=O.ts.dt.month
oth=O.groupby(["username","month"]).size()
def wmean(v,w): return (v*w).sum()/w.sum()
M=A.groupby(["p","month"]).apply(lambda d:pd.Series({"acc":wmean(d.acc,d.n),"per":100*d.per.sum()/d.n.sum(),"blitz":len(d),"days":d.ts.dt.floor("D").nunique(),"kend":d.k_all.iloc[-1]})).reset_index()
M["other"]=[oth.get((p,m),0) for p,m in zip(M.p,M.month)]
rows=[]
for p,d in M.groupby("p"):
    d=d.set_index("month")
    for m in range(2,12):
        if all(x in d.index for x in [m-1,m,m+1]) and d.loc[m-1,"blitz"]>=20 and d.loc[m+1,"blitz"]>=20:
            rows.append(dict(p=p,m=m,dacc=d.loc[m+1,"acc"]-d.loc[m-1,"acc"],dper=d.loc[m+1,"per"]-d.loc[m-1,"per"],
              lblitz=np.log2(1+d.loc[m,"blitz"]),lother=np.log2(1+d.loc[m,"other"]),lall=np.log2(1+d.loc[m,"blitz"]+d.loc[m,"other"]),
              ldays=np.log2(1+d.loc[m,"days"]),lk=np.log2(d.loc[m-1,"kend"]),acc_prev=d.loc[m-1,"acc"]))
R=pd.DataFrame(rows); print("triples",len(R),"people",R.p.nunique())
rng=np.random.default_rng(3)
def fe(X,y,g):
    Xd=X-X.groupby(g).transform("mean"); yd=y-y.groupby(g).transform("mean"); return np.linalg.lstsq(Xd.values,yd.values,rcond=None)[0]
def boot(cols,yv,R=R):
    b=fe(R[cols],R[yv],R.p); ps=R.p.unique(); bs=[]
    for _ in range(300):
        s=rng.choice(ps,len(ps)); B=pd.concat([R[R.p==q].assign(pb=i) for i,q in enumerate(s)]); bs.append(fe(B[cols],B[yv],B.pb))
    se=np.std(bs,axis=0); return ", ".join(f"{c} {b[i]:+.3f}±{se[i]:.3f}" for i,c in enumerate(cols))
for yv in ["dacc","dper"]:
    print(yv,"| all games in middle month + level:",boot(["lall","lk"],yv))
    print(yv,"| blitz vs other separately:",boot(["lblitz","lother","lk"],yv))
    print(yv,"| games vs active days:",boot(["lall","ldays","lk"],yv))
# between-person version of same (person means) for contrast
P=R.groupby("p")[["dacc","dper","lall","lk"]].mean()
for yv in ["dacc","dper"]:
    X=np.c_[np.ones(len(P)),P.lall-P.lall.mean(),P.lk-P.lk.mean()]; b=np.linalg.lstsq(X,P[yv],rcond=None)[0]; r=P[yv]-X@b; se=np.sqrt(np.diag(r@r/(len(P)-3)*np.linalg.inv(X.T@X)))
    print(yv,"BETWEEN-person: lall",round(b[1],3),"±",round(se[1],3))
R.to_csv("within_month.csv",index=False)
