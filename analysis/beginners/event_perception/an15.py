import pandas as pd, numpy as np, json, warnings; warnings.filterwarnings("ignore")
D="/tmp/claude-0/ana9"
M=pd.concat([pd.read_csv(f"{D}/moves{k}.csv") for k in range(4)])
M["clk"]=pd.to_numeric(M.clk,errors="coerce").fillna(999); M=M[M.clk>=10]
B=pd.concat([pd.read_csv(f"{D}/blund{k}.csv") for k in range(4)]).reset_index(drop=True)
HUNG=["moved_piece_hung","other_piece_hung","ignored_threat"]
W=pd.read_csv(f"{D}/wanted.csv").drop_duplicates(["site","p"])
nm=M.groupby(["site","p"]).size().rename("moves")
h=B[B.cat.isin(HUNG)].groupby(["site","p"]).size().rename("hung")
mc=B[B.cat=="missed_capture"].groupby(["site","p"]).size().rename("missed")
ob=B[~B.cat.isin(HUNG+["missed_capture","noise"])].groupby(["site","p"]).size().rename("otherbl")
G=W.set_index(["site","p"]).join([nm,h,mc,ob]).fillna({"hung":0,"missed":0,"otherbl":0}).reset_index()
G=G.sort_values(["p","k"]).reset_index(drop=True)
G.loc[G.moves<10,"moves"]=np.nan
for c in ("hung","missed","otherbl"): G[c+"_r"]=G[c]/G.moves*100
G["E"]=1/(1+10**((G.oppelo-G.elo)/400))
L=G.score==0; Wn=G.score>0
G["ev"]=np.select([L&(G.hung>=1),L&(G.hung==0),Wn&(G.hung>=1)],["hung_loss","other_loss","hung_nolose"],"")
R={"games":len(G),"players":G.p.nunique(),"moves":int(G.moves.sum()),"hung_per100":float(G.hung.sum()/G.moves.sum()*100),
   "ev_counts":G.ev.value_counts().to_dict()}
def run(G,col):
    out=[]
    for p,g in G.groupby("p",sort=False):
        v=g[col].to_numpy(); v=v-np.nanmean(v); ev=g.ev.to_numpy(); E=g.E.to_numpy()
        for i in np.flatnonzero(ev!=""):
            if i<10 or i+5>=len(g): continue
            out.append((p,ev[i],E[i],np.nanmean(v[i+1:i+6])-np.nanmean(v[i-5:i]),np.nanmean(v[i-5:i])-np.nanmean(v[i-10:i-5]),
                        np.nanmean(v[i+1:i+6])-np.nanmean(v[i-10:i-5]),v[i+1]-np.nanmean(v[i-10:i-5]) if not np.isnan(v[i+1]) else np.nan))
    return pd.DataFrame(out,columns=["p","ev","E","eff","pre","far","next1"])
def summ(E):
    T=E.groupby("ev").agg(n=("far","size"),eff=("eff","mean"),pre=("pre","mean"),far=("far","mean"),
        far_se=("far",lambda x:x.std()/np.sqrt(x.notna().sum())),next1=("next1","mean"))
    return T
def diff(E,a,b,col="far"):
    x=E[E.ev==a][col].dropna(); y=E[E.ev==b][col].dropna()
    return float(x.mean()-y.mean())
rng=np.random.default_rng(5)
for col in ("hung_r","missed_r","otherbl_r"):
    E=run(G,col); T=summ(E)
    r={"table":T.round(4).reset_index().to_dict("records"),
       "HL_minus_OL":diff(E,"hung_loss","other_loss"),"HL_minus_HN":diff(E,"hung_loss","hung_nolose"),
       "HL_minus_OL_next1":diff(E,"hung_loss","other_loss","next1")}
    # surprise split among losses
    Ls=E[E.ev.isin(["hung_loss","other_loss"])].copy(); Ls["unexp"]=Ls.E>=0.5
    r["split"]={f"{ev}_{'unexp' if u else 'exp'}":[int(len(x)),float(x.far.mean()),float(x.far.std()/np.sqrt(len(x)))] for (ev,u),x in Ls.groupby(["ev","unexp"])}
    def dd(Ls):
        m=lambda ev,u: Ls[(Ls.ev==ev)&(Ls.unexp==u)].far.mean()
        return float((m("hung_loss",True)-m("other_loss",True))-(m("hung_loss",False)-m("other_loss",False)))
    r["surprise_DiD"]=dd(Ls)
    if col=="hung_r":
        N1=[];N2=[];N3=[];N4=[]
        for rep in range(200):
            S=G.copy(); S[col]=S.groupby("p")[col].transform(lambda x: x.sample(frac=1,random_state=int(rng.integers(1e9))).values)
            En=run(S,col); N1.append(diff(En,"hung_loss","other_loss")); N2.append(diff(En,"hung_loss","hung_nolose"))
            N3.append(diff(En,"hung_loss","other_loss","next1"))
            Ln=En[En.ev.isin(["hung_loss","other_loss"])].copy(); Ln["unexp"]=Ln.E>=0.5; N4.append(dd(Ln))
        for k,N,obs in (("HL_minus_OL",N1,r["HL_minus_OL"]),("HL_minus_HN",N2,r["HL_minus_HN"]),("HL_minus_OL_next1",N3,r["HL_minus_OL_next1"]),("surprise_DiD",N4,r["surprise_DiD"])):
            N=np.array(N); r[k+"_null"]=[float(N.mean()),float(N.std()),float((np.abs(N-N.mean())>=abs(obs-N.mean())).mean())]
    R[col]=r; E.to_csv(f"{D}/events_{col}.csv",index=False)
print(json.dumps(R,indent=1,ensure_ascii=False)); json.dump(R,open(f"{D}/event_perc.json","w"),indent=1,ensure_ascii=False)
G.to_csv(f"{D}/games_seq.csv",index=False)
