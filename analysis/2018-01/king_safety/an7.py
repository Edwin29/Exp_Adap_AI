import pandas as pd, numpy as np, json
grp=pd.read_csv("/mnt/project-files/analysis/2018-01/cohort_players.csv").set_index("p").group
d=pd.concat([pd.read_csv(f"k{i}.csv",keep_default_na=False,na_values=[""]) for i in (1,2,3,4)]).drop_duplicates(["site","p"])
d["ts"]=pd.to_datetime(d.ts,format="%Y.%m.%d %H:%M:%S"); d=d.sort_values(["p","ts"]).reset_index(drop=True)
d["k"]=d.groupby("p").cumcount()+1; d["group"]=d.p.map(grp)
d["elo"]=pd.to_numeric(d.elo,errors="coerce")
d["delayq_rate"]=d.delayq/d.oppq.where(d.oppq>0)
d["delay_rate"]=d.delay/d.opp.where(d.opp>0)
d.to_pickle("feat4.pkl")
L=d[d.score==0]
S={"loss_n":len(L),"ka_old":float((L.dlast10>=10).mean()),"ka_clean":float(L.ka_clean.mean()),
   "mated_given_ka_clean":float(L[L.ka_clean==1].mated.mean()),"mated_given_other":float(L[(L.ka_clean==0)&(L.dlast10<10)].mated.mean()),
   "delayq_mean":float(d.delayq_rate.mean()),"oppq_mean":float(d.oppq.mean())}
eb=pd.cut(d.elo,[0,1200,1400,1600,1800,2000,3000])
S["by_elo"]=d.groupby(eb,observed=True).agg(delayq=("delayq_rate","mean"),ka_rate=("ka_clean",lambda x: x[d.loc[x.index,"score"]==0].mean())).round(3).reset_index().astype(str).to_dict("records")
pm=d.groupby("p").agg(elo=("elo","mean"),dq=("delayq_rate","mean")); S["corr_player_elo_delayq"]=float(pm.corr(method="spearman").loc["elo","dq"])
json.dump(S,open("S7.json","w"),indent=1); print(json.dumps(S,indent=1))
