import pandas as pd, numpy as np, json
def load(dirn):
    M=pd.concat([pd.read_csv(f"{dirn}/moves{k}.csv") for k in range(4)])
    M["clk"]=pd.to_numeric(M.clk,errors="coerce"); M=M[(M.clk.isna())|(M.clk>=10)]
    M["blunder"]=(M.wp_loss>=30).astype(float)
    G=M.groupby(["site","p","win","group"]).agg(acc=("acc","mean"),blunder=("blunder","mean")).reset_index()
    return M,G
# calibration from earlier 150-player sample: player-window acc -> elo
M6,G6=load("/tmp/claude-0/ana6"); W6=pd.read_csv("/tmp/claude-0/ana6/wanted.csv")
P6=G6.groupby(["p","win"]).acc.mean().reset_index().merge(W6.groupby(["p","win"]).elo.mean().reset_index(),on=["p","win"])
b,a=np.polyfit(P6.acc,P6.elo,1)
M,G=load("/tmp/claude-0/ana7"); W=pd.read_csv("/tmp/claude-0/ana7/wanted.csv")
wins=["jan_early","jan_late","feb_late"]
P=G.groupby(["p","win"])[["acc","blunder"]].mean().unstack("win")
elo=W.groupby(["p","win"]).elo.mean().unstack().reindex(P.index)
imp=a+b*P["acc"]
R={"fit":[float(a),float(b)],"moves":len(M),"games":len(G),"n":len(P)}
for w in wins:
    R[w]={"acc":float(P[("acc",w)].mean()),"blunder":float(P[("blunder",w)].mean()),"elo":float(elo[w].mean()),"elo_med":float(elo[w].median()),
          "implied":float(imp[w].mean()),"gap_elo_minus_implied":float((elo[w]-imp[w]).mean())}
for x,y in (("jan_early","jan_late"),("jan_late","feb_late"),("jan_early","feb_late")):
    ch=P[("acc",y)]-P[("acc",x)]; bl=P[("blunder",y)]-P[("blunder",x)]
    R[f"{x}->{y}"]={"acc_chg":float(ch.mean()),"acc_se":float(ch.std()/np.sqrt(len(ch))),"frac_acc_up":float((ch>0).mean()),
       "blunder_chg":float(bl.mean()),"blunder_se":float(bl.std()/np.sqrt(len(bl))),
       "elo_chg":float((elo[y]-elo[x]).mean()),"corr_acc_elo_chg":float(np.corrcoef(ch,elo[y]-elo[x])[0,1])}
# reliability of a 20-game window: split-half within jan_late
g=G[G.win=="jan_late"].copy(); g["h"]=g.groupby("p").cumcount()%2
h=g.groupby(["p","h"]).acc.mean().unstack(); r=np.corrcoef(h[0],h[1])[0,1]
R["split_half_r"]=float(r); R["acc_chg_sd"]=float((P[("acc","feb_late")]-P[("acc","jan_early")]).std())
# null sd of change from window noise: per-game sd / sqrt(20) * sqrt2
sdg=G.groupby(["p","win"]).acc.std().mean(); R["noise_sd_chg"]=float(sdg*np.sqrt(2/20))
# ana6 levels for comparison
G6w=G6.groupby(["p","win","group"]).acc.mean().reset_index()
R["ana6_levels"]=G6w.groupby(["group","win"]).acc.mean().round(2).reset_index().to_dict("records")
print(json.dumps(R,indent=1)); json.dump(R,open("/tmp/claude-0/ana7/beg_acc.json","w"),indent=1)
P.to_csv("/tmp/claude-0/ana7/beg_player_acc.csv")
