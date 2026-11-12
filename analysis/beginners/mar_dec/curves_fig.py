import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family":"WenQuanYi Zen Hei","figure.facecolor":"#fcfcfb","axes.facecolor":"#fcfcfb","axes.spines.top":False,"axes.spines.right":False,"axes.unicode_minus":False})
D=pd.read_pickle("D2.pkl")
pace=D.groupby("p").apply(lambda d:d.k.max()/max(d.days.max(),1)); D["pace"]=D.p.map(pd.qcut(pace,3,labels=["느림","중간","빠름"]))
KE=[0,20,60,120,250,500,1000,2000,4000,8000]; DE=[-.1,7,21,45,75,105,150,200,260,330,366]
def cells(col,E):
    D["b"]=pd.cut(D[col],E,labels=False)
    c=D.groupby(["p","b"]).filter(lambda d:len(d)>=10).groupby(["p","b"]).apply(lambda d:pd.Series({"x":d[col].median(),"acc":(d.acc*d.n).sum()/d.n.sum(),"per":100*d.per.sum()/d.n.sum(),"pace":d.pace.iloc[0]})).reset_index()
    return c
C={"k":cells("k",KE),"days":cells("days",DE)}
COL={"느림":"#2a7ab0","중간":"#9a9a9a","빠름":"#d0632b"}
fig,ax=plt.subplots(2,2,figsize=(12,8.6))
for j,(axis,lab) in enumerate([("k","1월 첫 판부터 둔 블리츠 판 수 (로그 눈금)"),("days","1월 첫 판부터 지난 날짜")]):
    c=C[axis]
    for i,(y,ylab) in enumerate([("acc","정확도"),("per","지각 실수 / 100수")]):
        a=ax[i,j]
        for p,d in c.groupby("p"): a.plot(d.x,d[y],color=COL[d.pace.iloc[0]],alpha=.10,lw=.8)
        for pc in ["느림","중간","빠름"]:
            m=c[c.pace==pc].groupby("b").agg(x=("x","median"),y=(y,"median"),n=("p","size")); m=m[m.n>=8]
            a.plot(m.x,m.y,color=COL[pc],lw=2.6,marker="o",ms=4,label=f"{pc} 속도 ({(pace.pipe(lambda s:pd.qcut(s,3,labels=['느림','중간','빠름']))==pc).sum()}명)")
        if axis=="k": a.set_xscale("log")
        a.set_ylim((80,90) if y=="acc" else (0,2.6)); a.set_ylabel(ylab); a.set_xlabel(lab,fontsize=10)
        if i==0 and j==0: a.legend(frameon=False,fontsize=9,loc="lower right",title="하루 판 수로 나눈 세 묶음",title_fontsize=9)
ax[0,0].set_title("둔 판 수 축: 같은 판 수에서 느린 사람이 더 높다",loc="left",fontsize=11)
ax[0,1].set_title("날짜 축: 속도와 상관없이 곡선이 겹친다",loc="left",fontsize=11)
fig.suptitle("초보 150명의 1~12월 곡선 (가는 선 = 한 사람, 굵은 선 = 묶음별 중앙값)",x=0.01,ha="left",fontsize=13)
fig.tight_layout(); fig.savefig("curves.png",dpi=130)
print(pace.describe().round(2).to_dict()); print(pd.qcut(pace,3).cat.categories)
