import pandas as pd, numpy as np, json
meta=pd.read_pickle("meta.pkl")
man=pd.read_csv("/mnt/user-data/uploads/Exp_Adap_AI/data/lichess_api/beginners_2018-03_12/manifest.csv")
b=pd.read_csv("/mnt/user-data/uploads/Exp_Adap_AI/data/derived/beginners/beginners_984.csv").set_index("username")
ok=man[man.http_status==200].set_index("username")
blitz=(b.jan_blitz_games+b.feb_blitz_games).reindex(ok.index)+ok.n_games
meta["kind"]=np.select([meta.opp_is_ai==True, meta.variant.isin(["standard"])==False],["컴퓨터 상대","변형 체스"],default=meta.speed+np.where(meta.rated,"","(비레이팅)"))
oth=meta.groupby("username").size().reindex(ok.index).fillna(0)
share=oth/(oth+blitz)
print("people",len(share),"median other share",round(share.median(),3),"quartiles",share.quantile([.1,.25,.5,.75,.9]).round(3).tolist())
print("blitz-only (<5% other):",(share<.05).mean().round(3),"  >50% other:",(share>.5).mean().round(3))
print("totals: rated std blitz",int(blitz.sum()),"other",int(oth.sum()))
print(meta.groupby("kind").size().sort_values(ascending=False).head(12))
# A subset
A=pd.read_pickle("A.pkl"); sA=share.reindex(A.p.unique()); print("A median share",round(sA.median(),3),"blitz-only",(sA<.05).mean().round(3))
# bullet heavy?
bul=meta[(meta.speed=="bullet")].groupby("username").size().reindex(ok.index).fillna(0)/(oth+blitz)
print("bullet share median",round(bul.median(),3),">25% bullet:",(bul>.25).mean().round(3))
pd.DataFrame({"blitz":blitz,"other":oth,"share_other":share,"share_bullet":bul}).to_csv("other_share.csv")
