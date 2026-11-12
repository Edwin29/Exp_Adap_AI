import pandas as pd, numpy as np, json
G=pd.read_pickle("out/G.pkl"); M=pd.read_pickle("out/M.pkl"); B=pd.read_pickle("out/B.pkl")
PER={"moved_piece_hung","other_piece_hung","ignored_threat","missed_capture"}
M=M[M.clk>=10]; B=B[B.clk>=10]
B["per"]=B.cat.isin(PER); B["pos"]=B.cat.eq("positional_other"); B["tac"]=B.cat.eq("allowed_tactic"); B["mate"]=B.cat.eq("mate_allowed")
gm=M.groupby(["p","site"]).agg(n=("acc","size"),acc=("acc","mean")).reset_index()
gb=B.groupby(["p","site"])[["per","pos","tac","mate"]].sum().reset_index(); gb["bl"]=B.groupby(["p","site"]).size().values
g=G.merge(gm,on=["p","site"]).merge(gb,on=["p","site"],how="left").fillna({"per":0,"pos":0,"tac":0,"mate":0,"bl":0})
g["prio"]=g.p.map(M.drop_duplicates("p").set_index("p").prio)
g.to_pickle("out/gamelev.pkl")
# comparable sample: first 20 games each month
c=g[g.mk<=20]
def agg(d):
    s=d[["n","bl","per","pos","tac","mate"]].sum()
    return pd.Series({"people":d.p.nunique(),"games":len(d),"acc":(d.acc*d.n).sum()/s.n,
      **{k+"_100":100*s[k]/s.n for k in ["bl","per","pos","tac","mate"]},"elo_med":d.elo.median()})
out={}
for name,d in {"A":c[c.prio=="A"],"all":c}.items():
    out[name]=d.groupby("month").apply(agg).round(3)
# balanced panel: active (>=10 games) in 2018-03..05 AND 2018-10..12
act=c.groupby(["p","month"]).size().unstack(fill_value=0)
early=act[["2018-03","2018-04","2018-05"]].ge(10).any(axis=1); late=act[["2018-10","2018-11","2018-12"]].ge(10).any(axis=1)
bal=act.index[early&late]; out["balanced_all"]=c[c.p.isin(bal)].groupby("month").apply(agg).round(3)
out["balanced_A"]=c[c.p.isin(bal)&(c.prio=="A")].groupby("month").apply(agg).round(3)
for k,v in out.items(): print("==",k); print(v.to_string())
# Jan-Feb A baseline from earlier analysis
m0=pd.concat([pd.read_csv(f"/tmp/claude-0/ana7/moves{i}.csv") for i in range(4)]); m0=m0[m0.clk>=10]
b0=pd.concat([pd.read_csv(f"/tmp/claude-0/ana7/blund{i}.csv") for i in range(4)]); b0=b0[(b0.clk>=10)&(b0.cat!="noise")]
for w in ["jan_early","jan_late","feb_late"]:
    mm=m0[m0.win==w]; bb=b0[b0.win==w]; n=len(mm)
    print(w,"acc",round(mm.acc.mean(),3),"bl",round(100*len(bb)/n,3),"per",round(100*bb.cat.isin(PER).sum()/n,3),"pos",round(100*bb.cat.eq('positional_other').sum()/n,3),"tac",round(100*bb.cat.eq('allowed_tactic').sum()/n,3),"mate",round(100*bb.cat.eq('mate_allowed').sum()/n,3))
print("noise in new",B.cat.eq("noise").sum())
print("balanced n",len(bal),"of which A",c[c.p.isin(bal)&(c.prio=="A")].p.nunique())
