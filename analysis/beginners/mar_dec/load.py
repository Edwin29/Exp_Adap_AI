import pandas as pd, glob, os, numpy as np
R="/tmp/claude-0/ana10/raw"
G=pd.concat([pd.read_csv(f) for f in glob.glob(R+"/games/*.csv")],ignore_index=True)
M=pd.concat([pd.read_csv(f,usecols=["site","p","win","own_nm","ply","clk","wp_loss","acc"]) for f in glob.glob(R+"/moves/*.csv")],ignore_index=True)
B=pd.concat([pd.read_csv(f,usecols=["site","ply","p","win","clk","wp_loss","cat"]) for f in glob.glob(R+"/blunders/*.csv")],ignore_index=True)
G["month"]=G.utc_datetime.str[:7]; G=G.sort_values(["p","utc_datetime"]); G["k"]=G.groupby("p").cumcount()+1
G["mk"]=G.groupby(["p","month"]).cumcount()+1
for d in (M,B): d["prio"]=d.win.str[0]; d["month"]=d.win.str[2:]
G.to_pickle("out/G.pkl"); M.to_pickle("out/M.pkl"); B.to_pickle("out/B.pkl")
print(len(G),len(M),len(B)); print(G.groupby("month").p.nunique())
