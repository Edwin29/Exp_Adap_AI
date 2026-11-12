import pandas as pd, numpy as np
PER={"moved_piece_hung","other_piece_hung","ignored_threat","missed_capture"}
beg=pd.read_pickle("/tmp/claude-0/ana7/beg.pkl")[["site","p","ts","k","elo","score"]]
# Jan-Feb engine games
m0=pd.concat([pd.read_csv(f"/tmp/claude-0/ana7/moves{i}.csv") for i in range(4)]); m0=m0[m0.clk>=10]
b0=pd.concat([pd.read_csv(f"/tmp/claude-0/ana7/blund{i}.csv") for i in range(4)]); b0=b0[(b0.clk>=10)&(b0.cat!="noise")]
def gl(m,b):
    a=m.groupby(["p","site"]).agg(n=("acc","size"),acc=("acc","mean")).reset_index()
    bb=b.assign(per=b.cat.isin(PER),pos=b.cat.eq("positional_other")).groupby(["p","site"])[["per","pos"]].sum().reset_index()
    return a.merge(bb,on=["p","site"],how="left").fillna(0)
j=gl(m0,b0).merge(beg,on=["p","site"])
nJF=beg.groupby("p").size()
# Mar-Dec
g=pd.read_pickle("/tmp/claude-0/ana10/out/gamelev.pkl"); g=g[(g.prio=="A")&g.p.isin(j.p.unique())]
g=g.assign(ts=pd.to_datetime(g.utc_datetime).dt.tz_localize(None),k=g.k+g.p.map(nJF))[["p","site","n","acc","per","pos","ts","k","elo","result_for_p"]].rename(columns={"result_for_p":"score"})
D=pd.concat([j,g],ignore_index=True)
first=beg.groupby("p").ts.min(); D["days"]=(pd.to_datetime(D.ts)-D.p.map(first)).dt.total_seconds()/86400
D["per100"]=100*D.per/D.n; D["pos100"]=100*D.pos/D.n
D.to_pickle("D.pkl")
print(D.p.nunique(),len(D)); print(D.groupby(D.k.gt(nJF.reindex(D.p).values)).size())
b984=pd.read_csv("/mnt/user-data/uploads/Exp_Adap_AI/data/derived/beginners/beginners_984.csv").set_index("username")
cmp=(b984.jan_blitz_games+b984.feb_blitz_games).reindex(nJF.index); print("JF count match:",(cmp==nJF).mean(), (cmp-nJF).describe().round(1).to_dict())
print(D.groupby("p").k.max().describe().round(0).to_dict()); print(D.groupby("p").days.max().describe().round(0).to_dict())
