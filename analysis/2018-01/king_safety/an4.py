import pandas as pd, numpy as np, json
grp=pd.read_csv("/mnt/project-files/analysis/2018-01/cohort_players.csv").set_index("p").group
d=pd.concat([pd.read_csv(f"h{i}.csv",keep_default_na=False,na_values=[""]) for i in (1,2,3,4)])
d=d.drop_duplicates(["site","p"])
d["ts"]=pd.to_datetime(d.ts,format="%Y.%m.%d %H:%M:%S"); d=d.sort_values(["p","ts"])
d["k"]=d.groupby("p").cumcount()+1; d["group"]=d.p.map(grp)
d["elo"]=pd.to_numeric(d.elo,errors="coerce"); d["oppelo"]=pd.to_numeric(d.oppelo,errors="coerce")
d["delay_rate"]=np.where(d.opp>0,d.delay/d.opp.where(d.opp>0),np.nan)
d["sv"]=np.where(d.castled==1,d.shield_vol,np.nan)
d["svmg_r"]=np.where((d.castled==1)&(d.mg>=5),d.svmg/d.mg.where(d.mg>0)*10,np.nan)
d["forfeit_r"]=np.where(d.first_legal_nm.notna()|(d.forfeit==1),d.forfeit,np.nan)
d.to_pickle("feat2.pkl")
S={"rows":len(d),"players":d.p.nunique()}
for m in ["opp","delay","delay_rate","sv","shield_vol_storm","luft","forfeit_r","dmax","dlast10"]:
    S[m]=d[m].describe().round(3).to_dict()
# validity: player-level means vs mean elo; game-level corr with elo controlling player? simple
pm=d.groupby("p").agg(elo=("elo","mean"),delay_rate=("delay_rate","mean"),sv=("sv","mean"),svmg=("svmg_r","mean"),forfeit=("forfeit_r","mean"),castle10=("castle_nm",lambda x:(x<=10).mean()))
S["corr_player_elo"]=pm.corr(method="spearman")["elo"].round(3).to_dict()
eb=pd.cut(d.elo,[0,1200,1400,1600,1800,2000,3000])
S["by_elo"]=d.groupby(eb,observed=True)[["delay_rate","sv","svmg_r","forfeit_r","dlast10"]].mean().round(3).reset_index().astype(str).to_dict("records")
L=d[d.score==0]
S["dlast10_losses_q"]=L.dlast10.quantile([.25,.5,.75,.9]).to_dict()
S["dlast10_by_term"]=L.groupby("mated").dlast10.mean().round(2).to_dict()
json.dump(S,open("S4.json","w"),indent=1,default=str); print(json.dumps(S,indent=1,default=str))
