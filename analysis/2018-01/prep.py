import pandas as pd, numpy as np, glob, re
cols="d t w b we be wd bd tc r te ev eco wt bt clk evl n".split()
fs=sorted(glob.glob("/mnt/user-data/uploads/Exp_Adap_AI/outputs/analysis_2018-01/c*.tsv.gz"))
df=pd.concat([pd.read_csv(f,sep="\t",names=cols,header=None,quoting=3,dtype=str,na_filter=False) for f in fs],ignore_index=True)
print(len(df))
def speed(ev):
    for s in ["UltraBullet","Bullet","Blitz","Rapid","Classical","Correspondence"]:
        if s in ev: return s
    return "Other"
evu=df.ev.unique(); m={e:speed(e) for e in evu}
df["speed"]=df.ev.map(m).astype("category")
df["tourn"]=df.ev.str.contains("tournament|swiss",case=False)
df["day"]=pd.to_numeric(df.d.str[-2:],errors="coerce").astype("Int16")
df.loc[df.d.str.startswith("2017"),"day"]=0
for c in ["we","be","wd","bd","n"]: df[c]=pd.to_numeric(df[c],errors="coerce").astype("float32")
df["clk"]=df.clk=="1"; df["evl"]=df.evl=="1"
for c in ["tc","r","te","eco","wt","bt"]: df[c]=df[c].astype("category")
# timestamp order
df["ts"]=pd.to_datetime(df.d+" "+df.t,format="%Y.%m.%d %H:%M:%S",errors="coerce")
df.drop(columns=["d","t","ev"],inplace=True)
df.to_pickle("games.pkl")
print(df.dtypes); print(df.speed.value_counts())
