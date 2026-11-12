import pandas as pd, numpy as np
D=pd.read_pickle("D2.pkl")
def wm(d,c): return (d[c]*d.n).sum()/d.n.sum()
base=D[D.k<=20].groupby("p").apply(lambda d:pd.Series({"acc0":wm(d,"acc"),"per0":100*d.per.sum()/d.n.sum()}))
out=[]
print("== fixed games T: does time taken matter?")
for T in [200,400,800,1600]:
    w=D[(D.k>T-50)&(D.k<=T+50)]; s=w.groupby("p").filter(lambda d:len(d)>=30).groupby("p")
    a=s.apply(lambda d:pd.Series({"acc":wm(d,"acc"),"per":100*d.per.sum()/d.n.sum(),"days":d.days.median()})).join(base,how="inner")
    a["dacc"]=a.acc-a.acc0; a["dper"]=a.per-a.per0; a["ld"]=np.log2(a.days)
    X=np.c_[np.ones(len(a)),a.ld-a.ld.mean(),a.acc0-a.acc0.mean()]
    for yv in ["dacc","dper"]:
        b,res,*_=np.linalg.lstsq(X,a[yv].values,rcond=None); r=a[yv].values-X@b; se=np.sqrt(np.diag(r@r/(len(a)-3)*np.linalg.inv(X.T@X)))
        print(f"T={T} n={len(a)} days median {a.days.median():.0f} (IQR {a.days.quantile(.25):.0f}-{a.days.quantile(.75):.0f}) {yv}: mean {a[yv].mean():+.2f}, per doubling of days {b[1]:+.3f} ± {se[1]:.3f}")
        out.append(("games",T,yv,len(a),a[yv].mean(),b[1],se[1]))
print("== fixed days: do games played matter?")
for T in [30,60,120,240,330]:
    w=D[(D.days>T-10)&(D.days<=T+10)]; s=w.groupby("p").filter(lambda d:len(d)>=30).groupby("p")
    a=s.apply(lambda d:pd.Series({"acc":wm(d,"acc"),"per":100*d.per.sum()/d.n.sum(),"k":d.k.median()})).join(base,how="inner")
    a["dacc"]=a.acc-a.acc0; a["dper"]=a.per-a.per0; a["lk"]=np.log2(a.k)
    X=np.c_[np.ones(len(a)),a.lk-a.lk.mean(),a.acc0-a.acc0.mean()]
    for yv in ["dacc","dper"]:
        b,*_=np.linalg.lstsq(X,a[yv].values,rcond=None); r=a[yv].values-X@b; se=np.sqrt(np.diag(r@r/(len(a)-3)*np.linalg.inv(X.T@X)))
        print(f"day={T} n={len(a)} games median {a.k.median():.0f} (IQR {a.k.quantile(.25):.0f}-{a.k.quantile(.75):.0f}) {yv}: mean {a[yv].mean():+.2f}, per doubling of games {b[1]:+.3f} ± {se[1]:.3f}")
        out.append(("days",T,yv,len(a),a[yv].mean(),b[1],se[1]))
pd.DataFrame(out,columns=["fixed","T","y","n","mean_change","slope_per_doubling","se"]).to_csv("fixed_axis.csv",index=False)
