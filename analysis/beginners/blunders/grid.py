import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg, json
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family":"WenQuanYi Zen Hei","figure.facecolor":"#fcfcfb"})
I=json.load(open("eye.json"))
K={"moved_piece_hung":"옮긴 기물을 내줌","other_piece_hung":"다른 기물을 내줌","ignored_threat":"위협 무시","missed_capture":"잡을 기물 놓침",
   "allowed_tactic":"전술 허용","mate_allowed":"메이트 허용","positional_other":"기타"}
J={0:("○","Bg4를 폰이 잡음"),1:("○","Rf4를 비숍이 잡음"),2:("○","Nh4로 g5 비숍 지킴이 사라짐"),3:("○","나이트가 떠나 퀸이 핀에 걸림"),
4:("○","b7 비숍이 이미 노려지는데 Bh6"),5:("○","c5 나이트가 폰에 잡힐 위기인데 a5"),6:("○","공짜 나이트 Qxc3+를 놓침"),7:("○","공짜 나이트 Bxe6를 놓침"),
8:("○","Rg2 뒤 Qd1+ 연속 체크"),9:("○","Ng3 뒤 Nxc2+ 포크"),10:("○","룩을 잡다 백랭크 메이트"),11:("○","Ng1 뒤 Qxf2# 메이트"),
12:("△","한 수로 보이지 않는 손해"),13:("△","실은 두 수짜리 전술")}
col={"○":"#1baf7a","△":"#eda100","X":"#d03b3b"}
fig,axs=plt.subplots(2,7,figsize=(24,8.4))
for ax,n in zip(axs.T.flat,range(14)):
    ax.imshow(mpimg.imread(f"e{n:02d}.png")); ax.axis("off")
    v,t=J[n]; ax.set_title(f"{K[I[str(n)]['cat']]}\n{v} {t}",fontsize=11,color=col[v],loc="left")
fig.suptitle("큰 실수 유형별 2판씩: 주황 = 실제로 둔 수, 초록 = 엔진 최선수, 빨강 = 상대의 최선 응수 (둔 사람 쪽에서 본 판)",fontsize=14,x=0.01,ha="left")
fig.tight_layout(); fig.savefig("grid_blunders.png",dpi=95)
