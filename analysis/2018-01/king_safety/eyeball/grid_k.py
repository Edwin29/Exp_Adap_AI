import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family":"WenQuanYi Zen Hei","figure.facecolor":"#fcfcfb"})
V={1:("○","걸어나온 왕이 나이트·퀸에 메이트"),2:("○","가운데 왕이 공격받다 무너지고 시간패"),3:("○","왕 앞 나이트 침투로 메이트"),4:("○","퀸·비숍 공격에 기권"),
5:("○","h7 퀸으로 메이트"),6:("△","왕이 노출됐지만 기물 손실도 큼"),7:("○","기물이 앞섰는데 메이트당함"),8:("△","끝내기 직전 왕 노출 중 시간패"),
9:("○","메이트 위협에 기권"),10:("○","퀸·룩에 메이트")}
col={"○":"#1baf7a","△":"#eda100","X":"#d03b3b"}
fig,axs=plt.subplots(2,5,figsize=(16,8))
for ax,n in zip(axs.flat,range(1,11)):
    ax.imshow(mpimg.imread(f"k{n:02d}.png")); ax.axis("off"); v,t=V[n]; ax.set_title(f"{n}. {v} {t}",fontsize=10.5,color=col[v],loc="left")
fig.suptitle("고친 정의의 왕 공격 패배 10판 (새 무작위 표본, 마지막 국면)",fontsize=14,x=0.01,ha="left"); fig.tight_layout(); fig.savefig("grid_ka_clean.png",dpi=110)
