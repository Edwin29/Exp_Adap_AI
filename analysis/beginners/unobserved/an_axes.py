import pandas as pd, numpy as np
A=pd.read_pickle("A.pkl"); A=A[A.n>=5]
def wm(d): return (d.acc*d.n).sum()/d.n.sum()
def pr(d): return 100*d.per.sum()/d.n.sum()
base=A[A.k<=30].groupby("p").apply(lambda d:pd.Series({"acc0":wm(d),"per0":pr(d)}))
def reg(a,x,yv):
    X=np.c_[np.ones(len(a)),a[x]-a[x].mean(),a.acc0-a.acc0.mean()]
    b=np.linalg.lstsq(X,a[yv].values,rcond=None)[0]; r=a[yv].values-X@b; se=np.sqrt(np.diag(r@r/(len(a)-3)*np.linalg.inv(X.T@X))); return b[1],se[1]
def window(mask_fn,label,xcols):
    out=[]
    for T in label:
        w=A[mask_fn(A,T)]; s=w.groupby("p").filter(lambda d:len(d)>=30).groupby("p")
        a=s.apply(lambda d:pd.Series({"acc":wm(d),"per":pr(d),"days":d.days.median(),"k":d.k.median(),"k_all":d.k_all.median(),"k_other":d.k_other.median()})).join(base,how="inner")
        a["dacc"]=a.acc-a.acc0; a["dper"]=a.per-a.per0
        for c in ["days","k","k_all"]: a["l"+c]=np.log2(a[c].clip(lower=1))
        a["lk_other"]=np.log2(a.k_other+1)
        res=[f"{T}: n={len(a)}"]
        for x in xcols:
            for yv in ["dacc","dper"]:
                b,se=reg(a,x,yv); res.append(f"{yv}~{x} {b:+.2f}±{se:.2f}")
        print("  ".join(res))
print("== fixed BLITZ games: days / other games")
window(lambda A,T:(A.k>T-50)&(A.k<=T+50),[200,400,800,1600],["ldays","lk_other"])
print("== fixed TOTAL games (blitz+other): days")
window(lambda A,T:(A.k_all>T-50)&(A.k_all<=T+50),[200,400,800,1600],["ldays"])
print("== fixed days: blitz games / total games")
window(lambda A,T:(A.days>T-7)&(A.days<=T+7),[14,30,60,120,240],["lk","lk_all"])
