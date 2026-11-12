import pandas as pd, numpy as np
g=pd.read_pickle("/tmp/claude-0/ana/games.pkl")
g=g[g.speed=="Blitz"][["w","b","we","be","wd","bd","ts"]]
a=pd.DataFrame({"p":g.w.values,"elo":g.we.values,"rd":g.wd.values,"ts":g.ts.values})
b=pd.DataFrame({"p":g.b.values,"elo":g.be.values,"rd":g.bd.values,"ts":g.ts.values})
L=pd.concat([a,b]); del a,b,g
L["p"]=L.p.astype(str); L=L.sort_values(["p","ts"]); L["k"]=L.groupby("p").cumcount()+1
n=L.groupby("p").size()
first=L[L.k==1].set_index("p")
newp=first[(first.elo==1500)&(first.rd.abs()>=50)].index
x=L[L.p.isin(newp)]
e30=x[x.k==30].set_index("p").elo; e60=x[x.k==60].set_index("p").elo
df=pd.DataFrame({"n":n.reindex(newp),"e30":e30,"e60":e60}).dropna(subset=["n"])
print("new accounts",len(df)); 
for th in (1100,1200,1300):
    for mn in (60,100,150):
        print(th,mn,int(((df.e30<=th)&(df.n>=mn)).sum()))
print(df.e30.describe())
df.to_csv("new_accounts.csv")
