import pandas as pd, numpy as np, json
d=pd.read_pickle("/tmp/claude-0/ana7/beg.pkl").reset_index(drop=True)
c=pd.read_pickle("/tmp/claude-0/ana5/feat_jf.pkl")
m="delayq_rate"; R={}
d["cast15"]=np.where(d.nm>=15,(d.castled==1)&(d.castle_nm<=15),np.nan).astype(float)
# 1) trajectory over game index, balanced panel (>=300 games)
bins=[0,20,50,100,150,200,300]
n=d.groupby("p").size(); bal=n[n>=300].index; b=d[d.p.isin(bal)&(d.k<=300)].copy()
b["kb"]=pd.cut(b.k,bins)
T=b.groupby("kb",observed=True).agg(elo=("elo","mean"),delayq=(m,"mean"),cast15=("cast15","mean"),ka=("ka_clean","mean"),score=("score","mean"))
R["traj_n"]=len(bal); R["traj"]={str(k):v for k,v in T.round(3).to_dict("index").items()}
print(len(bal)); print(T.round(3))
# rating norm from cohort Jan + beginners Jan
allj=pd.concat([c[c.month==1][["elo",m]],d[d.month==1][["elo",m]]])
eb=lambda x: pd.cut(x,np.arange(500,2700,100))
norm=allj.groupby(eb(allj.elo),observed=True)[m].mean()
R["norm"]={str(k):round(float(v),3) for k,v in norm.items()}
d["exp"]=eb(d.elo).map(norm).astype(float)
# 2) individual z, games 1-50 vs 101-150, shuffle null
rng=np.random.default_rng(0)
def zs(dd,col):
    out={}
    for p,g in dd.groupby("p",sort=False):
        a=g.loc[g.k<=50,col].dropna(); bb=g.loc[(g.k>100)&(g.k<=150),col].dropna()
        if len(a)<20 or len(bb)<20: continue
        se=np.sqrt(a.var()/len(a)+bb.var()/len(bb))
        if se>0: out[p]=(bb.mean()-a.mean())/se
    return pd.Series(out)
for col in (m,"cast15"):
    oz=zs(d,col); nulls=[]
    for r in range(10):
        s=d[["p","k",col]].copy()
        s[col]=s.groupby("p")[col].transform(lambda x: x.sample(frac=1,random_state=int(rng.integers(1e9))).values)
        nulls.append(zs(s,col))
    R["indiv_"+col]=dict(n=len(oz),obs_gt2=float((oz.abs()>2).mean()),null_gt2=float(np.mean([(x.abs()>2).mean() for x in nulls])),
        null_p95=float(np.percentile([(x.abs()>2).mean() for x in nulls],95)),mean_z=float(oz.mean()),
        frac_up=float((oz>2).mean()),frac_down=float((oz<-2).mean()))
# 3) convergence: first 50 games (A) vs last 50 Feb (D)
def windows(dd):
    rows=[]
    for p,g in dd.groupby("p",sort=False):
        f=g[g.month==2]
        if len(g)<150 or len(f)<50: continue
        A=g.head(50); D=f.tail(50); v=(A[m].mean(),D[m].mean())
        if np.isnan(v).any(): continue
        rows.append((p,*v,A.exp.mean(),D.exp.mean(),A.elo.mean(),D.elo.mean()))
    return pd.DataFrame(rows,columns=["p","A","D","expA","expD","eloA","eloD"])
def summ(w):
    tot=w.D-w.A; gap=w.A-w.expA
    return dict(n=len(w),toward=float((tot*-np.sign(gap)>0).mean()),corr_gap_tot=float(np.corrcoef(gap,tot)[0,1]),
                gapA_abs=float((w.A-w.expA).abs().mean()),gapD_abs=float((w.D-w.expD).abs().mean()),meanA=float(w.A.mean()),meanD=float(w.D.mean()))
w=windows(d); R["conv"]=summ(w); R["conv"]["elo_med"]=[float(w.eloA.median()),float(w.eloD.median())]
nl=[]
for r in range(10):
    s=d.copy(); s[m]=s.groupby("p")[m].transform(lambda x: x.sample(frac=1,random_state=int(rng.integers(1e9))).values)
    nl.append(summ(windows(s)))
R["conv_null"]={k:[float(np.mean([x[k] for x in nl])),float(np.max([x[k] for x in nl]))] for k in ("toward","corr_gap_tot","gapD_abs")}
# 4) event study
d["r"]=d[m]-d.groupby(["p","color"])[m].transform("mean")
L=d.score==0; W=d.score==1
d["ev"]=np.select([L&(d.ka_clean==1),L&(d.dlast10<10),W&(d.oka_clean==1)],["ka_loss","other_loss","ka_win"],"")
def run(dd):
    out=[]
    for p,g in dd.groupby("p",sort=False):
        v=g["r"].to_numpy(); ev=g["ev"].to_numpy()
        for i in np.flatnonzero(ev!=""):
            if i<10 or i+5>=len(g): continue
            post=np.nanmean(v[i+1:i+6]); pre=np.nanmean(v[i-5:i]); pre2=np.nanmean(v[i-10:i-5])
            out.append((p,ev[i],post-pre,pre-pre2,post-pre2))
    return pd.DataFrame(out,columns=["p","ev","eff","pre","eff_far"]).dropna()
import warnings; warnings.filterwarnings("ignore")
E=run(d)
T=E.groupby("ev").agg(n=("eff","size"),eff=("eff","mean"),pre=("pre","mean"),far=("eff_far","mean"),far_se=("eff_far",lambda x:x.std()/np.sqrt(len(x))))
R["event"]=T.round(4).reset_index().to_dict("records")
ka=E[E.ev=="ka_loss"].eff_far.values; ol=E[E.ev=="other_loss"].eff_far.values
R["event_diff"]=[float(ka.mean()-ol.mean()),float(np.sqrt(ka.var()/len(ka)+ol.var()/len(ol)))]
R["ka_rate"]=float(d[d.score==0].ka_clean.mean())
print(json.dumps(R,indent=1)); json.dump(R,open("/tmp/claude-0/ana7/beg_castle.json","w"),indent=1)
