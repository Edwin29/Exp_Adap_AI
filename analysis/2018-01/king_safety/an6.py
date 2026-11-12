import pandas as pd, numpy as np, json, sys
d=pd.read_pickle("feat2.pkl").reset_index(drop=True)
TH=float(sys.argv[1])
M=sys.argv[2].split(",")
for m in M: d[m+"_r"]=d[m]-d.groupby(["p","color"])[m].transform("mean")
L=d.score==0; W=d.score==1
d["ev"]=np.select([L&(d.dlast10>=TH),L&(d.dlast10<TH),W&(d.odlast10>=TH)],["ka_loss","other_loss","ka_win"],"")
out=[];per=[]
for p,g in d.groupby("p",sort=False):
    g=g.reset_index(drop=True)
    for m in M:
        v=g[m+"_r"].to_numpy()
        for i in np.flatnonzero(g.ev.to_numpy()!=""):
            if i<10 or i+5>=len(g): continue
            post=np.nanmean(v[i+1:i+6]); pre=np.nanmean(v[i-5:i]); pre2=np.nanmean(v[i-10:i-5])
            out.append((p,m,g.ev[i],post-pre,pre-pre2))
E=pd.DataFrame(out,columns=["p","m","ev","eff","pre"]).dropna()
E.to_csv("events.csv",index=False)
T=E.groupby(["m","ev"]).agg(n=("eff","size"),eff=("eff","mean"),se=("eff",lambda x:x.std()/np.sqrt(len(x))),pre=("pre","mean"),pre_se=("pre",lambda x:x.std()/np.sqrt(len(x)))).reset_index()
print(T.to_string()); T.to_csv("event2.csv",index=False)
# per-person: difference KA loss effect minus other-loss effect, persons with >=5 of each
P=E.groupby(["m","p","ev"]).eff.agg(["mean","size","var"]).reset_index()
res={}
for m in M:
    a=P[(P.m==m)&(P.ev=="ka_loss")].set_index("p"); b=P[(P.m==m)&(P.ev=="other_loss")].set_index("p")
    j=a.join(b,lsuffix="_a",rsuffix="_b",how="inner"); j=j[(j.size_a>=5)&(j.size_b>=5)]
    diff=j.mean_a-j.mean_b; se=np.sqrt(j.var_a/j.size_a+j.var_b/j.size_b); z=diff/se
    res[m]={"persons":len(j),"mean_diff":float(diff.mean()),"se_mean_diff":float(diff.std()/np.sqrt(len(diff))),
            "sd_z":float(z.std()),"frac_absz_gt2":float((z.abs()>2).mean()),"median_events_ka":float(j.size_a.median())}
    pd.DataFrame({"diff":diff,"z":z}).to_csv(f"person_diff_{m}.csv")
print(json.dumps(res,indent=1)); json.dump({"table":T.to_dict("records"),"person":res,"TH":TH},open("event2.json","w"),indent=1)
