import chess, chess.pgn, chess.svg, gzip, io, csv, subprocess, json
rows=list(csv.DictReader(open("/tmp/claude-0/ana3/eyeball20.csv")))
want={r["링크"].split("lichess.org/")[1][:8]:r for r in rows}
U="/mnt/user-data/uploads/Exp_Adap_AI/outputs/analysis_2018-01/sel%d.pgn.gz"
games={}
for i in (1,2,3,4):
    f=io.TextIOWrapper(gzip.open(U%i,"rb"),encoding="utf-8")
    while len(games)<len(want):
        off=None
        h=chess.pgn.read_headers(f)
        if h is None: break
        sid=h.get("Site","")[-8:]
        if sid in want:
            # re-read: skip approach -> store headers offset not trivial; read game text via second pass
            games[sid]=None
    f.close()
# second pass collecting full games
for i in (1,2,3,4):
    f=io.TextIOWrapper(gzip.open(U%i,"rb"),encoding="utf-8")
    while True:
        g=chess.pgn.read_game(f)
        if g is None: break
        sid=g.headers.get("Site","")[-8:]
        if sid in want and games.get(sid) is None: games[sid]=g
        if all(v is not None for v in games.values()) and len(games)==len(want): break
    if all(v is not None for v in games.values()) and len(games)==len(want): break
U2={chess.KNIGHT:2,chess.BISHOP:2,chess.ROOK:3,chess.QUEEN:5}
info=[]
for n,r in enumerate(rows,1):
    sid=r["링크"].split("lichess.org/")[1][:8]; g=games[sid]
    side=chess.WHITE if r["색"]=="백" else chess.BLACK
    b=g.board(); moves=list(g.mainline_moves())
    if r["종류"]=="캐슬링 미룸":
        own=0
        for mv in moves:
            if b.turn==side:
                own+=1
                lc=[m for m in b.legal_moves if b.is_castling(m)]
                if lc and not b.is_castling(mv):
                    arrows=[chess.svg.Arrow(m.from_square,m.to_square,color="#1baf7a") for m in lc]+[chess.svg.Arrow(mv.from_square,mv.to_square,color="#eb6834")]
                    svg=chess.svg.board(b,orientation=side,arrows=arrows,size=360,lastmove=None)
                    info.append(dict(n=n,sid=sid,kind="delay",own=own,played=b.san(mv),castle=[b.san(m) for m in lc],
                        oppq=bool(b.pieces(chess.QUEEN,not side)),check=b.is_check(),fen=b.fen()))
                    break
            b.push(mv)
    else:
        for mv in moves: b.push(mv)
        k=b.king(side); zone=chess.SquareSet(b.attacks(k))|chess.SquareSet.from_square(k)
        att=[]
        for pt,u in U2.items():
            for sq in b.pieces(pt,not side):
                if b.attacks(sq)&zone: att.append((chess.piece_name(pt),chess.square_name(sq)))
        fill={sq:"#eb683466" for sq in zone}
        arrows=[chess.svg.Arrow(chess.parse_square(s),k,color="#d03b3b") for _,s in att]
        svg=chess.svg.board(b,orientation=side,fill=fill,arrows=arrows,size=360,check=k if b.is_check() else None)
        info.append(dict(n=n,sid=sid,kind="ka",attackers=att,mate=b.is_checkmate(),check=b.is_check(),
            material=sum(len(b.pieces(p,side))*v for p,v in {1:1,2:3,3:3,4:5,5:9}.items())-sum(len(b.pieces(p,not side))*v for p,v in {1:1,2:3,3:3,4:5,5:9}.items()),
            term=g.headers.get("Termination"),plies=len(moves),fen=b.fen()))
    open(f"b{n:02d}.svg","w").write(svg)
    import cairosvg; cairosvg.svg2png(bytestring=svg.encode(),write_to=f"b{n:02d}.png")
json.dump(info,open("info.json","w"),indent=1,ensure_ascii=False)
for x in info: print(x)
