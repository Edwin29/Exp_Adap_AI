import pandas as pd, numpy as np
A=pd.read_pickle("A.pkl"); A=A[A.n>=5]
def wm(d): return (d.acc*d.n).sum()/d.n.sum()
def pr(d): return 100*d.per.sum()/d.n.sum()
base=A[A.k<=30].groupby("p").apply(lambda d:pd.Series({"acc0":wm(d),"per0":pr(d)}))
rows=[]
for T in [400,800]:
    w=A[(A.k>T-50)&(A.k<=T+50)]; s=w.groupby("p").filter(lambda d:len(d)>=30).groupby("p")
    a=s.apply(lambda d:pd.Series({"acc":wm(d),"per":pr(d),"days":d.days.median(),"ko":d.k_other.median()})).join(base,how="inner")
    a["dacc"]=a.acc-a.acc0; a["dper"]=a.per-a.per0; a["ld"]=np.log2(a.days); a["lo"]=np.log2(a.ko+1)
    print(T,"corr(ldays, lother)",round(a.ld.corr(a.lo),2))
    for yv in ["dacc","dper"]:
        X=np.c_[np.ones(len(a)),a.ld-a.ld.mean(),a.lo-a.lo.mean(),a.acc0-a.acc0.mean()]
        b=np.linalg.lstsq(X,a[yv].values,rcond=None)[0]; r=a[yv].values-X@b; se=np.sqrt(np.diag(r@r/(len(a)-4)*np.linalg.inv(X.T@X)))
        print(f"  {yv}: days {b[1]:+.2f}±{se[1]:.2f}  other games {b[2]:+.2f}±{se[2]:.2f}  (n={len(a)})")
