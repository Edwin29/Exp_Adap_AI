import pandas as pd, numpy as np, json
df=pd.read_pickle('games.pkl')
df["speed"]=df.speed.cat.rename_categories({"Other":"Rapid*"})
S={}
S["games"]=len(df); S["clk_frac"]=float(df.clk.mean()); S["eval_frac"]=float(df.evl.mean())
S["speed_counts"]=df.speed.value_counts().to_dict()
S["clk_by_speed"]=df.groupby("speed",observed=True).clk.mean().to_dict()
S["eval_by_speed"]=df.groupby("speed",observed=True).evl.mean().to_dict()
S["term"]=df.te.value_counts().to_dict()
S["bot_games"]=int(((df.wt=="BOT")|(df.bt=="BOT")).sum())
S["titles"]=pd.concat([df.wt,df.bt]).value_counts().head(10).to_dict()
S["tourn_frac"]=float(df.tourn.mean())
S["plies_q"]=df.n.quantile([.05,.25,.5,.75,.95]).to_dict()
S["short_lt10"]=float((df.n<10).mean())
S["n_tc"]=int(df.tc.nunique())
# long format
sc={"1-0":1.0,"0-1":0.0,"1/2-1/2":0.5}
r=df.r.astype(str).map(sc)
L=pd.concat([
 pd.DataFrame({"p":df.w,"speed":df.speed,"tc":df.tc,"elo":df.we,"diff":df.wd,"day":df.day,"ts":df.ts,"score":r,"title":df.wt,"n":df.n}),
 pd.DataFrame({"p":df.b,"speed":df.speed,"tc":df.tc,"elo":df.be,"diff":df.bd,"day":df.day,"ts":df.ts,"score":1-r,"title":df.bt,"n":df.n})],ignore_index=True)
del df
L.sort_values(["p","speed","ts"],inplace=True,kind="stable")
S["unique_players"]=int(L.p.nunique())
g=L.groupby(["p","speed"],observed=True,sort=False)
P=g.agg(games=("elo","size"),days=("day","nunique"),elo0=("elo","first"),elo1=("elo","last"),diff0=("diff","first"),
        last_diff=("diff","last"),title=("title","first"))
P["elo_end"]=P.elo1+P.last_diff.fillna(0)
P["dElo"]=P.elo_end-P.elo0
# modal tc share
tcn=L.groupby(["p","speed","tc"],observed=True).size()
P["modal_tc_share"]=(tcn.groupby(level=[0,1]).max()/tcn.groupby(level=[0,1]).sum())
P["new_est"]=(P.elo0==1500)
P=P.reset_index()
P.to_pickle("players.pkl")
# player totals any speed
T=L.groupby("p").agg(games=("elo","size"),days=("day","nunique"))
T.to_pickle("ptot.pkl")
thr={}
for k in [50,100,200,500]:
    thr[f"any>={k}"]=int((T.games>=k).sum())
    for s in ["Bullet","Blitz","Rapid*","Classical"]:
        q=P[(P.speed==s)]
        thr[f"{s}>={k}"]=int((q.games>=k).sum())
        thr[f"{s}>={k}&days>=10"]=int(((q.games>=k)&(q.days>=10)).sum())
S["thresholds"]=thr
S["players_by_speed"]=P.groupby("speed",observed=True).size().to_dict()
S["games_per_player_q_any"]=T.games.quantile([.5,.75,.9,.99]).to_dict()
for s in ["Blitz","Rapid*","Bullet","Classical"]:
    q=P[P.speed==s]
    S[f"{s}_new_est"]=int(q.new_est.sum())
    for k in [50,100,200]:
        S[f"{s}_new_est_ge{k}"]=int((q.new_est&(q.games>=k)).sum())
    S[f"{s}_heavy100_elo0_q"]=q[q.games>=100].elo0.quantile([.1,.25,.5,.75,.9]).to_dict()
    S[f"{s}_all_elo0_q"]=q.elo0.quantile([.1,.25,.5,.75,.9]).to_dict()
    S[f"{s}_heavy100_dElo_q"]=q[q.games>=100].dElo.quantile([.1,.25,.5,.75,.9]).to_dict()
    S[f"{s}_heavy100_modal_tc_share_med"]=float(q[q.games>=100].modal_tc_share.median())
json.dump(S,open("summary.json","w"),indent=1,default=str,ensure_ascii=False)
print(json.dumps(S,indent=1,default=str,ensure_ascii=False))
