import pandas as pd, numpy as np
d=pd.read_pickle("feat.pkl")
R=pd.read_csv("player_change.csv")
# opening repertoire change: as white, share of early-modal first move; as black, share of early-modal ECO letter+digit
out=[]
for p,g in d.groupby("p"):
    e=g[g.k<=50]; l=g[(g.k>100)&(g.k<=150)]
    if len(e)<30 or len(l)<30: continue
    ew=e[e.color=="w"].first_move; lw=l[l.color=="w"].first_move
    eb=e[e.color=="b"].eco.str[:2]; lb=l[l.color=="b"].eco.str[:2]
    mw=ew.mode().iloc[0] if len(ew) else None; mb=eb.mode().iloc[0] if len(eb) else None
    rep_w=(ew==mw).mean()-(lw==mw).mean() if mw is not None and len(lw) else np.nan
    rep_b=(eb==mb).mean()-(lb==mb).mean() if mb is not None and len(lb) else np.nan
    # castle10 change within same-white-first-move games
    same=g[(g.color=="w")&(g.first_move==mw)]
    a=same[same.k<=50].castle10.dropna(); b=same[(same.k>100)&(same.k<=150)].castle10.dropna()
    within=b.mean()-a.mean() if len(a)>=10 and len(b)>=10 else np.nan
    out.append((p,rep_w,rep_b,within))
O=pd.DataFrame(out,columns=["p","rep_drop_w","rep_drop_b","delta_within_opening"]).merge(R,on="p")
O["absz"]=O.z.abs(); O["changer"]=O.absz>2
print(O.groupby("changer")[["rep_drop_w","rep_drop_b"]].median())
print("corr |delta| vs rep drop w:",O[["delta","rep_drop_w"]].abs().corr().iloc[0,1], " b:",O[["delta","rep_drop_b"]].abs().corr().iloc[0,1])
c=O[O.changer]
print("changers n",len(c)," delta median abs",c.delta.abs().median()," within-opening delta median abs",c.delta_within_opening.abs().median(), "same-sign frac",(np.sign(c.delta)==np.sign(c.delta_within_opening)).mean(), "nonnull",c.delta_within_opening.notna().sum())
O.to_csv("opening_check.csv",index=False)
