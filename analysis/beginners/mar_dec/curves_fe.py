import pandas as pd, numpy as np
D=pd.read_pickle("D.pkl"); D=D[D.n>=5]
KE=[0,20,40,80,160,320,640,1280,2560,1e9]; DE=[-1,3,7,14,30,60,120,240,400]
D["kb"]=pd.cut(D.k,KE,right=True,labels=False); D["db"]=pd.cut(D.days,DE,labels=False)
def fit(y,cols,w):
    X=[pd.get_dummies(D.p).values.astype(float)]
    for c in cols: X.append(pd.get_dummies(D[c],drop_first=True).values.astype(float))
    X=np.hstack(X); sw=np.sqrt(w); b=np.linalg.lstsq(X*sw[:,None],y*sw,rcond=None)[0]
    r=y-X@b; return (w*r*r).sum(), X.shape[1]
for yv in ["acc","per100"]:
    y=D[yv].values.astype(float); w=D.n.values.astype(float)
    base,_=fit(y,[],w); rk,pk=fit(y,["kb"],w); rd,pd_=fit(y,["db"],w); rb,pb=fit(y,["kb","db"],w)
    N=len(D)
    def F(r0,p0,r1,p1): return ((r0-r1)/(p1-p0))/(r1/(N-p1))
    print(yv,"within-person var explained: games",round(1-rk/base,5),"days",round(1-rd/base,5),"both",round(1-rb/base,5))
    print("   F add days given games",round(F(rk,pk,rb,pb),2),"(df",pb-pk,")  F add games given days",round(F(rd,pd_,rb,pb),2),"(df",pb-pd_,")")
# 2D table of person-demeaned acc
D["acc_dm"]=D.acc-D.groupby("p").acc.transform("mean"); D["per_dm"]=D.per100-D.groupby("p").per100.transform("mean")
print(D.pivot_table(index="kb",columns="db",values="acc_dm",aggfunc="mean").round(2))
print(D.pivot_table(index="kb",columns="db",values="acc_dm",aggfunc="size"))
D.to_pickle("D2.pkl")
