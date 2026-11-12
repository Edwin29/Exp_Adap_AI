import pandas as pd, numpy as np, json
df=pd.read_pickle('games.pkl')
df["speed"]=df.speed.cat.rename_categories({"Other":"Rapid*"})
b=df[df.speed=="Blitz"]
L=pd.concat([pd.DataFrame({"p":b.w,"elo":b.we,"diff":b.wd,"ts":b.ts,"tc":b.tc}),
             pd.DataFrame({"p":b.b,"elo":b.be,"diff":b.bd,"ts":b.ts,"tc":b.tc})],ignore_index=True)
del df,b
L.sort_values(["p","ts"],inplace=True,kind="stable")
L["k"]=L.groupby("p").cumcount()
first=L[L.k==0].set_index("p")
print("diff0 for elo0==1500:",first[first.elo==1500]["diff"].abs().describe().to_dict())
print("diff0 for others:",first[first.elo!=1500]["diff"].abs().describe().to_dict())
newp=first[(first.elo==1500)&(first["diff"].abs()>=50)].index
cnt=L.groupby("p").size()
coh=cnt[newp]; coh100=coh[coh>=100].index
print("new strict:",len(newp)," >=100:",len(coh100), " >=200:",(coh>=200).sum())
C=L[L.p.isin(coh100)&(L.k<200)]
q=C.groupby("k").elo.quantile([.1,.25,.5,.75,.9]).unstack()
q["n"]=C.groupby("k").size()
q.to_csv("blitz_new_traj.csv")
# where are they after 30 games
e30=C[C.k==30].elo
print("elo at game30 quantiles",e30.quantile([.1,.25,.5,.75,.9]).to_dict())
# established heavy players (not new) for comparison
est=first[(first.elo!=1500)].index
cntest=cnt[est]; h=cntest[cntest>=100].index
E=L[L.p.isin(h)&(L.k<200)]
E["rel"]=E.elo-E.groupby("p").elo.transform("first")
qe=E.groupby("k").rel.quantile([.1,.5,.9]).unstack(); qe.to_csv("blitz_est_rel.csv")
C=C.copy(); C["rel"]=C.elo-1500
qn=C.groupby("k").rel.quantile([.1,.5,.9]).unstack(); qn.to_csv("blitz_new_rel.csv")
# abs rating change between game 30 and 199 for new cohort with >=200 games
c200=coh[coh>=200].index
D=L[L.p.isin(c200)]
a=D[D.k==30].set_index("p").elo; z=D[D.k==199].set_index("p").elo
print("new >=200: change game30->199", (z-a).quantile([.1,.25,.5,.75,.9]).to_dict(), len(c200))
# games per active day for heavy
json.dump({"new_strict":int(len(newp)),"new_ge100":int(len(coh100)),"new_ge200":int(len(c200))},open("cohort.json","w"))
