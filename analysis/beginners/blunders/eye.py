import chess, chess.pgn, chess.svg, chess.engine, cairosvg, pandas as pd, json
Bl=pd.concat([pd.read_csv(f"/tmp/claude-0/ana7/blund{k}.csv").assign(k=k) for k in range(4)]).reset_index(drop=True)
cats=["moved_piece_hung","other_piece_hung","ignored_threat","missed_capture","allowed_tactic","mate_allowed","positional_other"]
S=pd.concat([Bl[Bl.cat==c].sample(2,random_state=11) for c in cats]).reset_index(drop=True)
want={(r.site,r.ply):i for i,r in S.iterrows()}
e=chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish"); L=chess.engine.Limit(depth=10)
info={}
for k in range(4):
    f=open(f"/tmp/claude-0/ana7/part{k}.pgn")
    while (g:=chess.pgn.read_game(f)) is not None:
        sid=g.headers["Site"][-8:]
        if not any(s==sid for s,_ in want): continue
        b=g.board(); ply=0
        for node in g.mainline():
            ply+=1; mv=node.move
            if (sid,ply) in want:
                i=want[(sid,ply)]
                bm=e.analyse(b,L)["pv"][0]; b1=b.copy(); b1.push(mv)
                rp=e.analyse(b1,L).get("pv",[None])[0]
                arrows=[chess.svg.Arrow(mv.from_square,mv.to_square,color="#eda100cc"),chess.svg.Arrow(bm.from_square,bm.to_square,color="#1baf7acc")]
                if rp: arrows.append(chess.svg.Arrow(rp.from_square,rp.to_square,color="#d03b3bcc"))
                svg=chess.svg.board(b,orientation=b.turn,arrows=arrows,size=360,lastmove=None)
                cairosvg.svg2png(bytestring=svg.encode(),write_to=f"/tmp/claude-0/ana8/e{i:02d}.png")
                info[i]=dict(cat=S.cat[i],site=sid,ply=ply,played=b.san(mv),best=b.san(bm),reply=b1.san(rp) if rp else "",fen=b.fen(),own_nm=int(S.own_nm[i]),wp=float(S.wp_loss[i]))
            b.push(mv)
e.quit(); json.dump(info,open("/tmp/claude-0/ana8/eye.json","w"),indent=1,ensure_ascii=False)
for i in sorted(info): print(i,info[i])
