import pandas as pd, numpy as np, json
grp=pd.read_csv("/mnt/project-files/analysis/2018-01/cohort_players.csv").set_index("p").group
J=pd.concat([pd.read_csv(f"/tmp/claude-0/ana3/k{i}.csv",keep_default_na=False,na_values=[""]) for i in (1,2,3,4)]).assign(month=1)
F=pd.concat([pd.read_csv(f"f{i}.csv",keep_default_na=False,na_values=[""]) for i in (1,2,3,4)]).assign(month=2)
d=pd.concat([J,F]).drop_duplicates(["site","p"],keep="first")
d["ts"]=pd.to_datetime(d.ts,format="%Y.%m.%d %H:%M:%S"); d=d.sort_values(["p","ts"]).reset_index(drop=True)
d["k"]=d.groupby("p").cumcount()+1; d["km"]=d.groupby(["p","month"]).cumcount()+1
d["group"]=d.p.map(grp); d["elo"]=pd.to_numeric(d.elo,errors="coerce")
m="delayq_rate"; d[m]=d.delayq/d.oppq.where(d.oppq>0)
d.to_pickle("feat_jf.pkl")
R={}
nf=d[d.month==2].groupby("p").size()
R["feb_games_total"]=int((d.month==2).sum()); R["players_feb_ge50"]={g:int(((nf>=50)&(grp.reindex(nf.index)==g)).sum()) for g in ("est","new")}
R["players_feb_any"]=int((nf>0).sum())
eb=pd.cut(d.elo,np.arange(600,2700,100)); d["exp"]=eb.map(d[d.month==1].groupby(eb[d.month==1],observed=True)[m].mean()).astype(float)
def windows(dd):
    rows=[]
    for p,g in dd.groupby("p",sort=False):
        j=g[g.month==1]; f=g[g.month==2]
        if len(j)<150 or len(f)<100: continue
        A=j.head(50); B=j.tail(50); C=f.head(50); D=f.tail(50)
        v=[x[m].mean() for x in (A,B,C,D)]
        if any(np.isnan(v)): continue
        rows.append((p,*v,A.exp.mean(),A.elo.mean(),D.elo.mean()))
    return pd.DataFrame(rows,columns=["p","A","B","C","D","expA","eloA","eloD"])
def summ(w):
    jan=w.B-w.A; feb=w.D-w.C; gapA=w.A-w.expA; tot=w.D-w.A
    return dict(n=len(w),corr_janchg_febchg=float(np.corrcoef(jan,feb)[0,1]),
      corr_janchg_D_minus_A=float(np.corrcoef(jan,tot)[0,1]),
      frac_toward_exp_A_to_D=float((tot*-np.sign(gapA)>0).mean()),corr_gap_tot=float(np.corrcoef(gapA,tot)[0,1]),
      var_A=float(w.A.var()),var_D=float(w.D.var()),mean=[float(w[c].mean()) for c in "ABCD"])
w=windows(d); R["obs"]=summ(w)
R["obs"]["by_group_mean"]={g:[float(w[grp.reindex(w.p).values==g][c].mean()) for c in "ABCD"] for g in ("est","new")}
R["obs"]["elo_change_med"]={g:float((w.eloD-w.eloA)[grp.reindex(w.p).values==g].median()) for g in ("est","new")}
rng=np.random.default_rng(11); nulls=[]
for r in range(10):
    s=d.copy(); s[m]=s.groupby("p")[m].transform(lambda x: x.sample(frac=1,random_state=int(rng.integers(1e9))).values)
    nulls.append(summ(windows(s)))
R["null"]={k:[float(np.mean([n[k] for n in nulls])),float(np.min([n[k] for n in nulls])),float(np.max([n[k] for n in nulls]))] for k in ("corr_janchg_febchg","corr_janchg_D_minus_A","frac_toward_exp_A_to_D","corr_gap_tot","var_D")}
w.to_csv("windows.csv",index=False)
print(json.dumps(R,indent=1)); json.dump(R,open("jf.json","w"),indent=1)
