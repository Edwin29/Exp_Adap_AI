import pandas as pd, numpy as np, json
d=pd.concat([pd.read_csv(f"f{i}.csv") for i in range(1,5)],ignore_index=True)
co=pd.read_csv("/mnt/project-files/analysis/2018-01/cohort_players.csv")
d=d.merge(co,on="p")
d["ts"]=pd.to_datetime(d.ts,format="%Y.%m.%d %H:%M:%S")
d.sort_values(["p","ts"],inplace=True,kind="stable")
d["k"]=d.groupby("p").cumcount()+1
d["castle10"]=((d.castled==1)&(d.castle_ply<=10)).astype(float)
d.loc[d.nmoves_own<10,"castle10"]=np.nan   # too short to judge
d["base"]=d.tc.str.split("+").str[0].astype(float); d["inc"]=d.tc.str.split("+").str[1].astype(float)
d["time_frac"]=d.sec_per_move*d.nmoves_own/(d.base+d.inc*d.nmoves_own)
d["lt"]=np.select([(d.score==0)&(d.mated==1),(d.score==0)&(d.term=="Time forfeit"),(d.score==0)],["mated","time","resign"],"")
d.loc[d.score==1,"lt"]="win"; d.loc[d.score==0.5,"lt"]="draw"
# first move consistency as white
d.to_pickle("feat.pkl")
S={}
S["rows"]=len(d); S["players"]=d.p.nunique()
S["games_per_player"]=d.groupby("p").size().describe().to_dict()
S["by_group"]=d.groupby("group")[["castle10","castled","shield_pawn_moves","checks_recv","time_frac","mated"]].mean().to_dict()
S["lt_share"]=d.groupby("group").lt.value_counts(normalize=True).unstack().to_dict()
# bins
d["bin"]=((d.k-1)//25)*25+1
B=d[d.k<=300].groupby(["group","bin"]).agg(castle10=("castle10","mean"),checks=("checks_recv","mean"),
    time_frac=("time_frac","mean"),mated=("mated","mean"),elo=("elo","median"),n=("p","size")).reset_index()
B.to_csv("bins.csv",index=False); print(B.to_string())
# per player first 50 vs games 101-150 change in castle10
res=[]
for p,g in d.groupby("p"):
    a=g[g.k<=50].castle10.dropna(); b=g[(g.k>100)&(g.k<=150)].castle10.dropna()
    if len(a)<30 or len(b)<30: continue
    pa,pb=a.mean(),b.mean(); pp=(a.sum()+b.sum())/(len(a)+len(b))
    se=np.sqrt(pp*(1-pp)*(1/len(a)+1/len(b))) if 0<pp<1 else np.nan
    res.append((p,g.group.iloc[0],pa,pb,pb-pa,(pb-pa)/se if se else np.nan))
R=pd.DataFrame(res,columns=["p","group","early","late","delta","z"])
R.to_csv("player_change.csv",index=False)
S["player_change"]={gname:{"n":int(len(x)),"delta_median":float(x.delta.median()),"delta_q10":float(x.delta.quantile(.1)),"delta_q90":float(x.delta.quantile(.9)),
   "frac_z_gt2":float((x.z>2).mean()),"frac_z_lt-2":float((x.z<-2).mean()),"sd_z":float(x.z.std())} for gname,x in R.groupby("group")}
json.dump(S,open("S.json","w"),indent=1,default=str)
print(json.dumps(S,indent=1,default=str))
