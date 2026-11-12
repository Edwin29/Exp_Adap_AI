import pandas as pd, numpy as np, json
g=pd.read_pickle("out/gamelev.pkl"); G=pd.read_pickle("out/G.pkl")
man=pd.read_csv("/mnt/user-data/uploads/Exp_Adap_AI/data/lichess_api/beginners_2018-03_12/manifest.csv")
b984=pd.read_csv("/mnt/user-data/uploads/Exp_Adap_AI/data/derived/beginners/beginners_984.csv")
# --- experience vs calendar: people active (>=15 sampled games) in Mar and in Dec
c=g[g.mk<=20]
def wacc(d): return (d.acc*d.n).sum()/d.n.sum()
def wper(d): return 100*d.per.sum()/d.n.sum()
tot=G.groupby(["p","month"]).size().unstack(fill_value=0)  # all games (A full; B only first 20!) 
mg=man.set_index("username").monthly_games.dropna().apply(json.loads).apply(pd.Series).fillna(0)
rows=[]
for p,d in c.groupby("p"):
    e=d[d.month=="2018-03"]; l=d[d.month.isin(["2018-11","2018-12"])]
    if len(e)>=15 and len(l)>=15 and p in mg.index:
        between=mg.loc[p,[f"2018-{m:02d}" for m in range(4,11)]].sum()
        rows.append((p,wacc(l)-wacc(e),wper(l)-wper(e),between,wacc(e)))
X=pd.DataFrame(rows,columns=["p","dacc","dper","games_between","acc_mar"])
X["lg"]=np.log10(X.games_between+1)
print("n",len(X),"median games between",X.games_between.median())
X["q"]=pd.qcut(X.games_between,4,labels=["Q1 적음","Q2","Q3","Q4 많음"])
print(X.groupby("q").agg(n=("p","size"),games=("games_between","median"),dacc=("dacc","mean"),dacc_se=("dacc",lambda s:s.std()/np.sqrt(len(s))),dper=("dper","mean"),dper_se=("dper",lambda s:s.std()/np.sqrt(len(s))),acc_mar=("acc_mar","mean")).round(3))
import numpy.linalg as la
A=np.c_[np.ones(len(X)),X.lg,X.acc_mar-X.acc_mar.mean()]; 
for yv in ["dacc","dper"]:
    b,*_=la.lstsq(A,X[yv].values,rcond=None); r=X[yv].values-A@b; s2=r@r/(len(X)-3); se=np.sqrt(np.diag(s2*la.inv(A.T@A)))
    print(yv,"coef log10(games) ",round(b[1],3),"se",round(se[1],3),"| intercept(calendar part at ~0 games)",round(b[0],3))
# --- dropout
mg_all=man.set_index("username")
st=mg_all.account_status.copy()
act=mg.gt(0)
last=act.apply(lambda r: max([i for i,v in enumerate(r) if v],default=-1),axis=1)
b=b984.set_index("username")
b["status"]=st; b["n_mar_dec"]=mg_all.n_games; b["last_m"]=last.reindex(b.index)
b["grp"]=np.select([b.status=="not_found",b.status=="tos_violation",b.n_mar_dec.fillna(0)==0],["삭제(404)","약관위반","3~12월 0판"],"활동")
b["d_elo_janfeb"]=b.elo_last_game_feb-b.elo_at_game30
print(b.groupby("grp").agg(n=("jan_blitz_games","size"),jan=("jan_blitz_games","median"),feb=("feb_blitz_games","median"),elo30=("elo_at_game30","median"),elo_feb=("elo_last_game_feb","median"),delo=("d_elo_janfeb","median")).round(1))
pa=pd.read_csv("/tmp/claude-0/ana7/beg_player_acc.csv"); print(pa.columns.tolist()[:10])
surv=act.reindex(b[b.grp!="삭제(404)"].index).fillna(False).mean().round(3); print("share active by month (excl 404):",surv.to_dict())
X.to_csv("out/exp_vs_cal.csv",index=False); b.to_csv("out/dropout.csv")
