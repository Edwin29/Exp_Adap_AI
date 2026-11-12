import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family":"WenQuanYi Zen Hei","axes.unicode_minus":False,"font.size":11,
 "axes.spines.top":False,"axes.spines.right":False,"axes.edgecolor":"#8a8985","axes.labelcolor":"#52514e",
 "xtick.color":"#52514e","ytick.color":"#52514e","axes.grid":True,"grid.color":"#e6e5e0","grid.linewidth":0.8,
 "figure.facecolor":"#fcfcfb","axes.facecolor":"#fcfcfb","savefig.facecolor":"#fcfcfb"})
C=["#2a78d6","#eb6834","#1baf7a","#eda100"]; TP="#0b0b0b"; TS="#52514e"
import os; os.makedirs("fig",exist_ok=True)
d=pd.read_pickle("feat.pkl")
# null z: shuffle order 5 times
rng=np.random.default_rng(7)
def zs(dd):
    out=[]
    for p,g in dd.groupby("p",sort=False):
        a=g[g.k<=50].castle10.dropna(); b=g[(g.k>100)&(g.k<=150)].castle10.dropna()
        if len(a)<30 or len(b)<30: continue
        pp=(a.sum()+b.sum())/(len(a)+len(b))
        if not 0<pp<1: continue
        out.append((b.mean()-a.mean())/np.sqrt(pp*(1-pp)*(1/len(a)+1/len(b))))
    return out
nz=[]
for r in range(5):
    s=d[["p","k","castle10"]].copy()
    s["castle10"]=s.groupby("p").castle10.transform(lambda x: x.sample(frac=1,random_state=int(rng.integers(1e9))).values)
    nz+=zs(s)
oz=pd.read_csv("obs_z.csv").z.values
# Fig A: histogram observed vs null
fig,ax=plt.subplots(figsize=(8,4.8))
bins=np.arange(-6,6.01,0.5)
ax.hist(nz,bins=bins,density=True,color="#c3c2b7",label="순서를 섞은 경우(우연만 있을 때)",rwidth=0.92)
ax.hist(oz,bins=bins,density=True,histtype="step",color=C[0],lw=2.2,label="실제 순서")
for x in (-2,2): ax.axvline(x,color="#8a8985",ls="--",lw=1)
ax.set_xlabel("플레이어별 변화 점수 z (1~50판 대비 101~150판의 '10수 안 캐슬링' 비율 변화)")
ax.set_ylabel("밀도"); ax.legend(frameon=False,fontsize=9,loc="upper left")
ax.text(2.2,ax.get_ylim()[1]*0.8,"|z|>2인 플레이어\n실제 11.1% vs 우연 4.5%",color=TS,fontsize=9)
ax.set_title("개인별 변화는 우연보다 두 배 이상 자주 나타난다",loc="left",color=TP,fontsize=13)
fig.tight_layout(); fig.savefig("fig/figA_z.png",dpi=160); plt.close()
# Fig B: balanced panel bins
B=pd.read_csv("bins_balanced.csv")
fig,ax=plt.subplots(figsize=(8,4.6))
for i,(gname,lab) in enumerate([("est","기존 161명"),("new","신규(추정) 131명")]):
    b=B[B.group==gname]; ax.plot(b.bin+12,b.castle10*100,color=C[i],lw=2,marker="o",ms=5,label=lab)
ax.set_ylim(35,65); ax.set_xlabel("이달 블리츠 판 수 (25판 구간의 가운데)"); ax.set_ylabel("10수 안에 캐슬링한 비율 (%)")
ax.legend(frameon=False,fontsize=9,loc="upper right")
ax.set_title("집단 평균은 300판 동안 거의 평평하다 (300판 이상 둔 사람만)",loc="left",color=TP,fontsize=13)
fig.tight_layout(); fig.savefig("fig/figB_group.png",dpi=160); plt.close()
# Fig C: individual trajectories
R=pd.read_csv("player_change.csv")
up=R.sort_values("z",ascending=False).head(2).p.tolist(); dn=R.sort_values("z").head(2).p.tolist()
rnd=R.sample(30,random_state=3).p.tolist()
fig,ax=plt.subplots(figsize=(8,4.8))
for p in rnd:
    g=d[(d.p==p)&(d.k<=300)]; r=g.castle10.rolling(40,min_periods=30).mean()*100
    ax.plot(g.k,r,color="#c3c2b7",lw=0.8,alpha=0.8)
for j,p in enumerate(up+dn):
    g=d[(d.p==p)&(d.k<=300)]; r=g.castle10.rolling(40,min_periods=30).mean()*100
    col=C[2] if p in up else C[1]
    ax.plot(g.k,r,color=col,lw=2)
ax.plot([],[],color="#c3c2b7",label="무작위 30명"); ax.plot([],[],color=C[2],lw=2,label="가장 크게 늘어난 2명"); ax.plot([],[],color=C[1],lw=2,label="가장 크게 줄어든 2명")
ax.legend(frameon=False,fontsize=9,loc="lower left",ncol=3)
ax.set_xlabel("이달 블리츠 판 수"); ax.set_ylabel("최근 40판의 10수 안 캐슬링 비율 (%)")
ax.set_title("개인 궤적: 평평한 사람이 대부분이지만, 뚜렷하게 움직이는 사람도 있다",loc="left",color=TP,fontsize=12.5)
fig.tight_layout(); fig.savefig("fig/figC_indiv.png",dpi=160); plt.close()
# Fig D: event study
E=pd.read_csv("event.csv").set_index("type").loc[["mated","resign","time","win"]]
lab={"mated":"체크메이트로 패배","resign":"기권 패배","time":"시간패","win":"승리(비교)"}
fig,ax=plt.subplots(figsize=(8,4.4))
y=np.arange(len(E))[::-1]
ax.errorbar(E.eff*100,y+0.12,xerr=1.96*E.se*100,fmt="o",color=C[0],ms=7,capsize=0,lw=2,label="사건 직후 5판 - 직전 5판")
ax.errorbar(E.pre*100,y-0.12,xerr=1.96*E.pre_se*100,fmt="o",color="#8a8985",ms=6,capsize=0,lw=1.5,label="사전 추세(직전 5판 - 그 전 5판)")
ax.axvline(0,color="#8a8985",lw=1); ax.set_yticks(y); ax.set_yticklabels([f"{lab[t]} (n={n:,})" for t,n in zip(E.index,E.n)])
ax.set_xlabel("10수 안 캐슬링 비율의 변화 (%p, 플레이어·색별 평균 제거, 95% 구간)"); ax.set_xlim(-1.5,1.5)
ax.legend(frameon=False,fontsize=9,loc="lower right")
ax.set_title("체크메이트 패배 직후에도 캐슬링 습관은 바로 바뀌지 않는다",loc="left",color=TP,fontsize=13)
fig.tight_layout(); fig.savefig("fig/figD_event.png",dpi=160); plt.close()
print("null frac>2",np.mean(np.abs(nz)>2), "obs", np.mean(np.abs(oz)>2), len(oz))
