import pandas as pd, numpy as np, json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family":"WenQuanYi Zen Hei","axes.unicode_minus":False,"font.size":11,
 "axes.spines.top":False,"axes.spines.right":False,"axes.edgecolor":"#8a8985","axes.labelcolor":"#52514e",
 "xtick.color":"#52514e","ytick.color":"#52514e","axes.grid":True,"grid.color":"#e6e5e0","grid.linewidth":0.8,
 "figure.facecolor":"#fcfcfb","axes.facecolor":"#fcfcfb","savefig.facecolor":"#fcfcfb"})
C=["#2a78d6","#eb6834"]; TP="#0b0b0b"; TS="#52514e"
S=json.load(open("S4.json")); B=pd.DataFrame(S["by_elo"])
lab=["~1200","1200-1400","1400-1600","1600-1800","1800-2000","2000~"]
fig,axs=plt.subplots(1,2,figsize=(10,4.2))
x=np.arange(6)
axs[0].plot(x,B.delay_rate.astype(float)*100,color=C[0],marker="o",lw=2); axs[0].set_ylabel("캐슬링 가능한 차례 중 미룬 비율 (%)")
axs[0].set_title("캐슬링 미룸: 잘할수록 줄어든다 (통과)",loc="left",color=TP,fontsize=12)
axs[1].plot(x,B.svmg_r.astype(float),color=C[1],marker="o",lw=2); axs[1].set_ylabel("중반전 10수당 방패 폰 전진 (h3류 제외)")
axs[1].set_title("방패 약화: 잘할수록 오히려 늘어난다 (탈락)",loc="left",color=TP,fontsize=12)
for a in axs: a.set_xticks(x); a.set_xticklabels(lab,fontsize=9); a.set_xlabel("레이팅 구간")
fig.tight_layout(); fig.savefig("fig/figE_validity.png",dpi=160); plt.close()
oz=pd.read_csv("z_delay_rate.csv").z; nz=pd.read_csv("znull_delay_rate.csv").z
I=json.load(open("indiv_delay_rate.json"))["delay_rate"]
fig,ax=plt.subplots(figsize=(8,4.6)); bins=np.arange(-6,6.01,0.5)
ax.hist(nz,bins=bins,density=True,color="#c3c2b7",rwidth=0.92,label="순서를 섞은 경우(우연만 있을 때)")
ax.hist(oz,bins=bins,density=True,histtype="step",color=C[0],lw=2.2,label="실제 순서")
for v in (-2,2): ax.axvline(v,color="#8a8985",ls="--",lw=1)
ax.text(2.2,ax.get_ylim()[1]*0.8,f"z 절댓값이 2를 넘는 사람\n실제 {I['obs_gt2']*100:.1f}% vs 우연 {I['null_gt2']*100:.1f}%",color=TS,fontsize=9)
ax.set_xlabel("플레이어별 변화 점수 z (1~50판 대비 101~150판의 캐슬링 미룸 비율)"); ax.set_ylabel("밀도")
ax.legend(frameon=False,fontsize=9,loc="upper left")
ax.set_title("새 지표에서도 개인 변화는 우연의 약 두 배",loc="left",color=TP,fontsize=13)
fig.tight_layout(); fig.savefig("fig/figF_delay_z.png",dpi=160); plt.close()
E=pd.read_csv("event2.csv"); E=E[E.m=="delay_rate"].set_index("ev").loc[["ka_loss","other_loss","ka_win"]]
L={"ka_loss":"왕 공격 패배","other_loss":"다른 패배","ka_win":"왕 공격 승리"}
fig,ax=plt.subplots(figsize=(8,3.8)); y=np.arange(3)[::-1]
ax.errorbar(E.eff*100,y+0.12,xerr=1.96*E.se*100,fmt="o",color=C[0],ms=7,lw=2,label="사건 직후 5판 - 직전 5판")
ax.errorbar(E.pre*100,y-0.12,xerr=1.96*E.pre_se*100,fmt="o",color="#8a8985",ms=6,lw=1.5,label="사전 추세")
ax.axvline(0,color="#8a8985",lw=1); ax.set_yticks(y); ax.set_yticklabels([f"{L[t]} (n={n:,})" for t,n in zip(E.index,E.n)])
ax.set_xlim(-1.2,1.2); ax.set_xlabel("캐슬링 미룸 비율 변화 (%p, 플레이어·색 평균 제거, 95% 구간)")
ax.legend(frameon=False,fontsize=9,loc="lower right")
ax.set_title("왕이 공격받아 진 직후에도 캐슬링을 덜 미루지 않는다",loc="left",color=TP,fontsize=13)
fig.tight_layout(); fig.savefig("fig/figG_event.png",dpi=160); plt.close()
