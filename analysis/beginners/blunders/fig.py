import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, json, numpy as np
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family":"WenQuanYi Zen Hei","figure.facecolor":"#fcfcfb","axes.facecolor":"#fcfcfb","axes.spines.top":False,"axes.spines.right":False,"axes.unicode_minus":False})
R=json.load(open("/tmp/claude-0/ana7/blund_types.json"))
K=[("moved_piece_hung","옮긴 기물을 내줌"),("other_piece_hung","다른 기물을 내줌"),("missed_capture","잡을 기물 놓침"),("ignored_threat","위협 무시"),
   ("allowed_tactic","전술 허용"),("mate_allowed","메이트 허용"),("positional_other","기타")]
fig,ax=plt.subplots(figsize=(8,4.4)); y=np.arange(len(K))[::-1]
for off,key,c,lab in ((0.17,"jan_early->feb_late","#2a78d6","1월 처음 → 2월 말"),(-0.17,"jan_late->feb_late","#eda100","1월 말 → 2월 말")):
    m=[R["by_cat"][k][key][0] for k,_ in K]; s=[R["by_cat"][k][key][1] for k,_ in K]
    ax.errorbar(m,y+off,xerr=np.array(s)*2,fmt="o",color=c,ms=6,capsize=0,lw=1.6,label=lab)
ax.axvline(0,color="#888",lw=0.8); ax.set_yticks(y); ax.set_yticklabels([n for _,n in K],fontsize=11)
ax.axhspan(3.5,6.5,color="#e5f4e4",zorder=0)
ax.set_xlabel("100수당 큰 실수 변화 (점 = 평균, 선 = ±2 표준오차)",fontsize=10)
ax.legend(frameon=False,loc="upper right",fontsize=10); ax.set_title("유형별 큰 실수 변화: 초록 띠 = 공짜 기물을 주거나 놓친 실수",loc="left",fontsize=12)
fig.tight_layout(); fig.savefig("blund_change.png",dpi=130)
