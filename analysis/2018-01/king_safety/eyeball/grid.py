import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family":"WenQuanYi Zen Hei","figure.facecolor":"#fcfcfb"})
V={1:("△","퀸사이드만 가능, 6수째 미룸은 보통"),2:("○","13수째까지 왕이 가운데"),3:("△","체크하며 기물 교환 우선"),4:("○","폰을 잡느라 캐슬링 미룸"),
5:("X","퀸이 이미 교환돼 캐슬링 필요 없음"),6:("△","한 수 미룸, 보통의 오프닝"),7:("△","한 수 미룸, 보통의 오프닝"),8:("○","캐슬링 대신 g4로 공격"),
9:("○","끝까지 캐슬링 안 함"),10:("△","폰을 잡느라 한 수 미룸"),
11:("△","왕이 공격받다 시간패, 이미 기물 열세"),12:("○","왕이 끌려나와 메이트"),13:("X","기물을 다 잃고 기권"),14:("○","가운데 왕이 메이트"),
15:("X","폰 승진으로 기권, 왕 공격 아님"),16:("○","왕 공격으로 메이트"),17:("X","기물을 다 잃은 끝내기에서 메이트"),18:("X","기물을 다 잃은 끝내기에서 메이트"),
19:("○","캐슬링한 왕이 h2에서 메이트"),20:("X","기물을 다 잃은 끝내기에서 메이트")}
col={"○":"#1baf7a","△":"#eda100","X":"#d03b3b"}
for name,rng,title in (("grid_delay.png",range(1,11),"캐슬링 미룸 10판: 초록 화살표 = 가능했던 캐슬링, 주황 = 실제로 둔 수"),
                       ("grid_ka.png",range(11,21),"왕 공격 패배 10판 (마지막 국면): 빨간 칸 = 왕 주변, 빨간 화살표 = 왕 주변을 노리는 상대 기물")):
    fig,axs=plt.subplots(2,5,figsize=(16,8))
    for ax,n in zip(axs.flat,rng):
        ax.imshow(mpimg.imread(f"b{n:02d}.png")); ax.axis("off")
        v,t=V[n]; ax.set_title(f"{n}. {v} {t}",fontsize=10.5,color=col[v],loc="left")
    fig.suptitle(title,fontsize=14,x=0.01,ha="left",color="#0b0b0b"); fig.tight_layout(); fig.savefig(name,dpi=110); plt.close()
