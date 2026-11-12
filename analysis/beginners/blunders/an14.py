import pandas as pd, numpy as np, json
M=pd.concat([pd.read_csv(f"/tmp/claude-0/ana7/moves{k}.csv") for k in range(4)])
M["clk"]=pd.to_numeric(M.clk,errors="coerce").fillna(999); M=M[M.clk>=10]
Bl=pd.concat([pd.read_csv(f"/tmp/claude-0/ana7/blund{k}.csv") for k in range(4)])
Bl["clk"]=pd.to_numeric(Bl.clk,errors="coerce").fillna(999)
ph=lambda x: pd.cut(x,[0,10,25,999],labels=["opening(1-10)","middle(11-25)","late(26+)"])
tb=lambda x: pd.cut(x,[9,30,60,1e9],labels=["10-30s","30-60s","60s+"])
M["phase"]=ph(M.own_nm); M["tbin"]=tb(M.clk); Bl["phase"]=ph(Bl.own_nm); Bl["tbin"]=tb(Bl.clk)
W=["jan_early","jan_late","feb_late"]
nm=M.groupby(["p","win"]).size().unstack()[W]
R={"n_blunders":len(Bl),"n_moves":len(M),"cat_share":Bl.cat.value_counts(normalize=True).round(3).to_dict()}
def rate_table(num, den, label):
    # num, den: per (p,win) counts -> per 100 moves; mean over players, change with se
    r=(num.reindex(den.index).fillna(0)/den*100)
    out={"level":{w:round(float(r[w].mean()),3) for w in W}}
    for a,b in (("jan_early","feb_late"),("jan_late","feb_late")):
        ch=r[b]-r[a]; out[f"{a}->{b}"]=[round(float(ch.mean()),3),round(float(ch.std()/np.sqrt(ch.notna().sum())),3)]
    return out
tot=Bl.groupby(["p","win"]).size().unstack().reindex(columns=W)
R["all"]=rate_table(tot,nm,"all")
R["by_cat"]={c:rate_table(Bl[Bl.cat==c].groupby(["p","win"]).size().unstack().reindex(columns=W),nm,c) for c in Bl.cat.unique()}
# phase: per 100 moves in that phase
R["by_phase"]={}
for p_ in M.phase.cat.categories:
    den=M[M.phase==p_].groupby(["p","win"]).size().unstack()[W]
    R["by_phase"][p_]=rate_table(Bl[Bl.phase==p_].groupby(["p","win"]).size().unstack().reindex(columns=W),den,p_)
R["by_time"]={}
for t in M.tbin.cat.categories:
    den=M[M.tbin==t].groupby(["p","win"]).size().unstack()[W]
    R["by_time"][t]=rate_table(Bl[Bl.tbin==t].groupby(["p","win"]).size().unstack().reindex(columns=W),den,t)
# share of moves in low time (time management)
low=M[M.tbin=="10-30s"].groupby(["p","win"]).size().unstack().reindex(columns=W).fillna(0)
R["share_moves_lowtime"]={w:round(float((low[w]/nm[w]).mean()*100),2) for w in W}
R["moves_per_game"]={w:round(float(M[M.win==w].groupby("site").size().mean()),1) for w in W}
# decomposition: how much of total change comes from each category
ch={c:R["by_cat"][c]["jan_early->feb_late"][0] for c in R["by_cat"]}
R["decomp_jan_early->feb_late"]=ch
print(json.dumps(R,indent=1,ensure_ascii=False)); json.dump(R,open("/tmp/claude-0/ana7/blund_types.json","w"),indent=1,ensure_ascii=False)
