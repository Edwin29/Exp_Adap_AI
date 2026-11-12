import pandas as pd, numpy as np, json
M=pd.concat([pd.read_csv(f"moves{k}.csv") for k in range(4)])
M["clk"]=pd.to_numeric(M.clk,errors="coerce")
M=M[(M.clk.isna())|(M.clk>=10)]
M["blunder"]=(M.wp_loss>=30).astype(float); M["mistake"]=(M.wp_loss>=20).astype(float)
M["cpl"]=(M.cp_before-M.cp_after).clip(lower=0)
G=M.groupby(["site","p","win","group"]).agg(acc=("acc","mean"),blunder=("blunder","mean"),mistake=("mistake","mean"),cpl=("cpl","mean"),n=("acc","size")).reset_index()
P=G.groupby(["p","group","win"])[["acc","blunder","mistake","cpl"]].mean().unstack("win")
W=pd.read_csv("wanted.csv"); elo=W.groupby(["p","win"]).elo.mean().unstack()
d=pd.read_pickle("/tmp/claude-0/ana5/feat_jf.pkl"); d=d.merge(W[["site","p","win"]],on=["site","p"])
dq=d.groupby(["p","win"]).delayq_rate.mean().unstack()
R={}
for g in ("new","est"):
    x=P.xs(g,level="group")
    r={}
    for m in ("acc","blunder","mistake","cpl"):
        ch=x[(m,"feb_late")]-x[(m,"jan_early")]
        r[m]={"jan":float(x[(m,"jan_early")].mean()),"feb":float(x[(m,"feb_late")].mean()),"chg":float(ch.mean()),"se":float(ch.std()/np.sqrt(len(ch))),"frac_improve":float(((ch>0) if m=="acc" else (ch<0)).mean())}
    pe=x.index; e=(elo.feb_late-elo.jan_early).reindex(pe)
    r["elo_chg_mean"]=float(e.mean()); r["n"]=len(pe)
    r["corr_acc_chg_elo_chg"]=float(np.corrcoef((x[("acc","feb_late")]-x[("acc","jan_early")]),e)[0,1])
    dqc=(dq.feb_late-dq.jan_early).reindex(pe)
    ok=dqc.notna()
    r["delay_chg_mean"]=float(dqc.mean()); r["corr_acc_chg_delay_chg"]=float(np.corrcoef((x[("acc","feb_late")]-x[("acc","jan_early")])[ok],dqc[ok])[0,1])
    R[g]=r
# diff-in-diff accuracy
a=P[("acc","feb_late")]-P[("acc","jan_early")]; gi=a.index.get_level_values("group")
R["did_acc"]=float(a[gi=="new"].mean()-a[gi=="est"].mean()); R["did_se"]=float(np.sqrt(a[gi=="new"].var()/sum(gi=="new")+a[gi=="est"].var()/sum(gi=="est")))
# cross-sectional validity: player acc vs elo (jan)
R["corr_acc_elo_jan"]=float(np.corrcoef(P[("acc","jan_early")],elo.jan_early.reindex(P.index.get_level_values("p")))[0,1])
R["moves"]=len(M); R["games"]=len(G)
print(json.dumps(R,indent=1)); json.dump(R,open("acc.json","w"),indent=1)
P.to_csv("player_acc.csv")
