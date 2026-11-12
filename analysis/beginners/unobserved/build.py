import pandas as pd, glob, numpy as np
R="/tmp/claude-0/ana12/raw"; PER={"moved_piece_hung","other_piece_hung","ignored_threat","missed_capture"}
G=pd.concat([pd.read_csv(f) for f in glob.glob(R+"/games/*.csv")],ignore_index=True)
M=pd.concat([pd.read_csv(f,usecols=["site","p","clk","acc"]) for f in glob.glob(R+"/moves/*.csv")],ignore_index=True)
B=pd.concat([pd.read_csv(f,usecols=["site","p","clk","cat"]) for f in glob.glob(R+"/blunders/*.csv")],ignore_index=True)
M=M[M.clk>=10]; B=B[(B.clk>=10)&(B.cat!="noise")]
gm=M.groupby(["p","site"]).agg(n=("acc","size"),acc=("acc","mean")).reset_index()
gb=B.assign(per=B.cat.isin(PER),pos=B.cat.eq("positional_other"),tac=B.cat.eq("allowed_tactic"),mate=B.cat.eq("mate_allowed")).groupby(["p","site"])[["per","pos","tac","mate"]].sum().reset_index()
jf=G.merge(gm,on=["p","site"]).merge(gb,on=["p","site"],how="left").fillna({"per":0,"pos":0,"tac":0,"mate":0})
md=pd.read_pickle("/tmp/claude-0/ana10/out/gamelev.pkl"); md=md[md.prio=="A"]
cols=["p","site","utc_datetime","elo","result_for_p","n","acc","per","pos","tac","mate"]
A=pd.concat([jf[cols].assign(src="janfeb"),md[cols].assign(src="mardec")],ignore_index=True)
A["ts"]=pd.to_datetime(A.utc_datetime).dt.tz_localize(None); A=A.sort_values(["p","ts"]).reset_index(drop=True)
A["k"]=A.groupby("p").cumcount()+1
# other experience
meta=pd.read_csv("/mnt/user-data/uploads/Exp_Adap_AI/data/derived/beginners/all_games_meta_2018.csv.gz")
meta["ts"]=pd.to_datetime(meta.created_at_utc).dt.tz_localize(None)
meta=meta[meta.status!="aborted"]
O=meta[meta.username.isin(A.p.unique())][["username","ts","speed","rated","variant","opp_is_ai","perf"]].rename(columns={"username":"p"})
# cumulative other games before each blitz game
A["k_other"]=0
for p,d in A.groupby("p"):
    o=np.sort(O[O.p==p].ts.values); A.loc[d.index,"k_other"]=np.searchsorted(o,d.ts.values)
first=A.groupby("p").ts.min(); A["days"]=(A.ts-A.p.map(first)).dt.total_seconds()/86400
A["k_all"]=A.k+A.k_other
A.to_pickle("A.pkl"); O.to_pickle("O.pkl"); meta.to_pickle("meta.pkl")
print(len(A),A.p.nunique(),A.src.value_counts().to_dict()); print(len(meta),meta.status.value_counts().head(3).to_dict())
print("JF per person games",jf.groupby("p").size().describe().round(0).to_dict())
