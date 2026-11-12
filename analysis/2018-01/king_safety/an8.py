import pandas as pd, numpy as np, json
d=pd.read_pickle("feat4.pkl").reset_index(drop=True)
m="delayq_rate"
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
def person(E,col):
    P=E.groupby(["p","ev"])[col].agg(["mean","size","var"]).reset_index()
    a=P[P.ev=="ka_loss"].set_index("p"); b=P[P.ev=="other_loss"].set_index("p")
    j=a.join(b,lsuffix="_a",rsuffix="_b",how="inner"); j=j[(j.size_a>=5)&(j.size_b>=5)]
    z=(j.mean_a-j.mean_b)/np.sqrt(j.var_a/j.size_a+j.var_b/j.size_b)
    return dict(n=len(j),mean_diff=float((j.mean_a-j.mean_b).mean()),se=float((j.mean_a-j.mean_b).std()/np.sqrt(len(j))),sd_z=float(z.std()),gt2=float((z.abs()>2).mean()))
E=run(d)
T=E.groupby("ev").agg(n=("eff","size"),eff=("eff","mean"),eff_se=("eff",lambda x:x.std()/np.sqrt(len(x))),pre=("pre","mean"),far=("eff_far","mean"),far_se=("eff_far",lambda x:x.std()/np.sqrt(len(x))))
print(T)
R={"table":T.reset_index().to_dict("records"),"person_eff":person(E,"eff"),"person_far":person(E,"eff_far")}
rng=np.random.default_rng(1); nulls=[]
for k in range(5):
    s=d.copy(); s["r"]=s.groupby("p")["r"].transform(lambda x: x.sample(frac=1,random_state=int(rng.integers(1e9))).values)
    En=run(s); nulls.append({"eff":person(En,"eff"),"far":person(En,"eff_far")})
R["null"]=nulls
print(json.dumps({k:R[k] for k in ("person_eff","person_far","null")},indent=1))
json.dump(R,open("event_final.json","w"),indent=1)
E.to_csv("events_final.csv",index=False)
