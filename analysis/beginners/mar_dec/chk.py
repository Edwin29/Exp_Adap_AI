import chess, chess.pgn, chess.engine, gzip, math, csv, sys, random
import pandas as pd
u=sys.argv[1]
M=pd.read_csv(f"/tmp/claude-0/ana10/raw/moves/{u}.csv")
sites=list(M.site.unique()); random.seed(3); pick=set(random.sample(sites,min(15,len(sites))))
e=chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish"); e.configure({"Threads":1,"Hash":64})
L=chess.engine.Limit(depth=10)
def ev(b):
    if b.is_checkmate(): return -1000
    if b.is_game_over(): return 0
    return max(-1000,min(1000,e.analyse(b,L)["score"].pov(b.turn).score(mate_score=1000)))
wp=lambda cp: 50+50*(2/(1+math.exp(-0.00368208*cp))-1)
f=gzip.open(f"/mnt/user-data/uploads/Exp_Adap_AI/data/lichess_api/beginners_2018-03_12/{u}.pgn.gz","rt")
rows=[]
while True:
    g=chess.pgn.read_game(f)
    if g is None: break
    sid=g.headers["Site"][-8:]
    if sid not in pick: continue
    side=chess.WHITE if g.headers["White"].lower()==u.lower() else chess.BLACK
    b=g.board(); cur=ev(b); ply=0
    for n in g.mainline():
        s=b.turn; b.push(n.move); ply+=1; nx=ev(b)
        if s==side: rows.append((sid,ply,max(0,wp(cur)-wp(-nx))))
        cur=nx
e.quit()
R=pd.DataFrame(rows,columns=["site","ply","wl_me"])
J=R.merge(M[["site","ply","wp_loss"]],on=["site","ply"],how="outer",indicator=True)
print(u,J._merge.value_counts().to_dict())
J=J[J._merge=="both"]; d=(J.wl_me-J.wp_loss).abs()
print("n",len(J),"mean|diff|",round(d.mean(),3),"p95",round(d.quantile(.95),2),"corr",round(J.wl_me.corr(J.wp_loss),4),"blunder agree",((J.wl_me>=30)==(J.wp_loss>=30)).mean().round(4))
