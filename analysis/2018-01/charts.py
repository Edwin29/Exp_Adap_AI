import pandas as pd, numpy as np, json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family":"WenQuanYi Zen Hei","axes.unicode_minus":False,"font.size":11,
 "axes.spines.top":False,"axes.spines.right":False,"axes.edgecolor":"#8a8985","axes.labelcolor":"#52514e",
 "xtick.color":"#52514e","ytick.color":"#52514e","axes.grid":True,"grid.color":"#e6e5e0","grid.linewidth":0.8,
 "figure.facecolor":"#fcfcfb","axes.facecolor":"#fcfcfb","savefig.facecolor":"#fcfcfb"})
C=["#2a78d6","#eb6834","#1baf7a","#eda100"]; TP="#0b0b0b"; TS="#52514e"
S=json.load(open("summary.json"))
import os; os.makedirs("fig",exist_ok=True)
# Fig1
sc=S["speed_counts"]; lab={"Blitz":"블리츠","Bullet":"불릿","Rapid*":"래피드*","Classical":"클래식","UltraBullet":"울트라불릿","Correspondence":"통신"}
ks=sorted(sc,key=sc.get)
fig,ax=plt.subplots(figsize=(8,4))
v=[sc[k]/1e6 for k in ks]
ax.barh([lab[k] for k in ks],v,color=C[0],height=0.6)
for i,x in enumerate(v): ax.text(x+0.1,i,f"{x:.2f}M",va="center",color=TP,fontsize=10)
ax.set_xlabel("대국 수 (백만 판)"); ax.grid(axis="y",visible=False)
ax.set_title("2018-01 Lichess rated 대국 1,794만 판의 속도별 구성",loc="left",color=TP,fontsize=13)
fig.text(0.01,0.01,"* 원본 Event 표기는 'Standard'. 주로 10+0으로, 현재 Lichess의 래피드에 해당",color=TS,fontsize=9)
fig.tight_layout(rect=(0,0.04,1,1)); fig.savefig("fig/fig1_speed.png",dpi=160); plt.close()
# Fig2 CCDF
P=pd.read_pickle("players.pkl")
fig,ax=plt.subplots(figsize=(8,5))
for i,s in enumerate(["Blitz","Bullet","Rapid*","Classical"]):
    g=np.sort(P[P.speed==s].games.values)
    xs=np.unique(np.round(np.logspace(0,np.log10(g.max()),200)).astype(int))
    ys=[(g>=x).sum() for x in xs]
    ax.plot(xs,ys,color=C[i],lw=2)
    ax.text(xs[-1]*1.08,1.0,lab[s],color=TP,fontsize=10,va="center",rotation=90)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(0.6,4e5); ax.set_xlim(0.8,2e4)
for x in [100,500]:
    ax.axvline(x,color="#8a8985",lw=1,ls="--")
t=S["thresholds"]
ax.text(105,2e5,f"100판 이상\n블리츠 {t['Blitz>=100']:,}명",color=TS,fontsize=9,va="top")
ax.text(520,2e5,f"500판 이상\n블리츠 {t['Blitz>=500']:,}명\n래피드* {t['Rapid*>=500']:,}명",color=TS,fontsize=9,va="top")
ax.set_xlabel("한 달 동안 둔 판 수 (해당 속도, 로그)"); ax.set_ylabel("그 이상 둔 플레이어 수 (로그)")
ax.set_title("플레이어별 한 달 판 수: x판 이상 둔 사람이 몇 명인가",loc="left",color=TP,fontsize=13)
fig.tight_layout(); fig.savefig("fig/fig2_games_ccdf.png",dpi=160); plt.close()
# Fig3 new cohort rating trajectory
q=pd.read_csv("blitz_new_traj.csv",index_col=0); q.columns=[c for c in q.columns]
k=q.index.values+1
fig,ax=plt.subplots(figsize=(8,5))
ax.fill_between(k,q["0.1"],q["0.9"],color=C[0],alpha=0.15,lw=0,label="10–90 백분위")
ax.fill_between(k,q["0.25"],q["0.75"],color=C[0],alpha=0.30,lw=0,label="25–75 백분위")
ax.plot(k,q["0.5"],color=C[0],lw=2,label="중앙값")
ax.axvspan(1,30,color="#e6e5e0",alpha=0.6,lw=0); ax.text(3,q["0.9"].max()+20,"레이팅 보정 구간\n(약 30판)",color=TS,fontsize=9,va="bottom")
ax.set_xlabel("블리츠 풀에서 둔 판 수 (첫 판 = 1)"); ax.set_ylabel("대국 시작 시 레이팅")
ax.set_ylim(q["0.1"].min()-50,q["0.9"].max()+150)
ax.legend(loc="lower right",frameon=False,fontsize=9)
ax.set_title(f"1500에서 시작한 블리츠 신규 플레이어(추정) {S.get('nb',4691):,}명의 레이팅 궤적",loc="left",color=TP,fontsize=13)
fig.text(0.01,0.01,"신규 추정: 이달 첫 블리츠 판이 1500이고 레이팅 변동이 50 이상(잠정 레이팅). 한 달 100판 이상 둔 사람만.",color=TS,fontsize=9)
fig.tight_layout(rect=(0,0.04,1,1)); fig.savefig("fig/fig3_new_traj.png",dpi=160); plt.close()
# Fig4 rel change new vs established
qn=pd.read_csv("blitz_new_rel.csv",index_col=0); qe=pd.read_csv("blitz_est_rel.csv",index_col=0)
fig,ax=plt.subplots(figsize=(8,5))
for qq,c,l in [(qe,C[1],"기존 플레이어 4.6만 명"),(qn,C[0],"신규 추정 4,691명")]:
    kk=qq.index.values+1
    ax.fill_between(kk,qq["0.1"],qq["0.9"],color=c,alpha=0.15,lw=0)
    ax.plot(kk,qq["0.5"],color=c,lw=2,label=l+" 중앙값, 띠는 10–90%")
ax.axhline(0,color="#8a8985",lw=1)
ax.set_xlabel("이달 블리츠 판 수 (첫 판 = 1)"); ax.set_ylabel("이달 첫 판 대비 레이팅 변화")
ax.legend(loc="lower left",frameon=False,fontsize=9)
ax.set_title("신규(추정)의 큰 변동폭은 대부분 첫 30판의 보정에서 생긴다",loc="left",color=TP,fontsize=12.5)
fig.tight_layout(); fig.savefig("fig/fig4_new_vs_est.png",dpi=160); plt.close()
print("ok")
