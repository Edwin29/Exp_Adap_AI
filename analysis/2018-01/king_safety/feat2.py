import chess, chess.pgn, gzip, sys, io, csv
names=set(open("/mnt/project-files/analysis/2018-01/cohort_names.txt").read().split())
fin,fout=sys.argv[1],sys.argv[2]
U={chess.KNIGHT:2,chess.BISHOP:2,chess.ROOK:3,chess.QUEEN:5}
def danger(b,side):
    k=b.king(side)
    if k is None: return 0
    zone=chess.SquareSet(b.attacks(k))|chess.SquareSet.from_square(k)
    s=0
    for pt,u in U.items():
        for sq in b.pieces(pt,not side):
            if b.attacks(sq)&zone: s+=u
    kf=chess.square_file(k)
    for f in range(max(0,kf-1),min(7,kf+1)+1):
        if not any(chess.square_file(sq)==f for sq in b.pieces(chess.PAWN,side)): s+=1
    return s
cols=["site","p","color","ts","elo","oppelo","score","term","mated","nm","castled","castle_nm","castle_side",
 "first_legal_nm","opp","delay","forfeit","shield_vol","shield_vol_storm","luft","dmax","dlast10","odlast10","delay_moves","shield_moves"]
w=csv.writer(open(fout,"w",newline="")); w.writerow(cols)
f=io.TextIOWrapper(gzip.open(fin,"rb"),encoding="utf-8")
n=0
while True:
    g=chess.pgn.read_game(f)
    if g is None: break
    h=g.headers
    sides=[s for s,k in ((chess.WHITE,"White"),(chess.BLACK,"Black")) if h.get(k) in names]
    if not sides: continue
    b=g.board()
    R={s:dict(nm=0,castled=0,cnm="",cside="",fl="",opp=0,delay=0,forfeit=0,sv=0,svs=0,luft=0,ds=[],dm=[],sm=[]) for s in (True,False)}
    for node in g.mainline():
        mv=node.move; s=b.turn; r=R[s]; r["nm"]+=1
        clk=node.clock()
        if s in sides: r["ds"].append(danger(b,s))
        else: R[s]["ds"].append(danger(b,s))
        legal_c=[m for m in b.legal_moves if b.is_castling(m)] if b.has_castling_rights(s) else []
        if legal_c and r["fl"]=="": r["fl"]=r["nm"]
        iscastle=b.is_castling(mv)
        if legal_c and (clk is None or clk>=10):
            r["opp"]+=1
            if not iscastle: r["delay"]+=1; r["dm"].append(r["nm"])
        pt=b.piece_type_at(mv.from_square)
        if iscastle:
            r["castled"]=1; r["cnm"]=r["nm"]; r["cside"]="K" if b.is_kingside_castling(mv) else "Q"
        elif pt==chess.KING and b.has_castling_rights(s) and not b.is_check() and not r["castled"]:
            r["forfeit"]=1
        elif r["castled"] and pt==chess.PAWN and not b.is_capture(mv) and not b.is_check():
            fl=chess.square_file(mv.from_square); k=b.king(s); kf=chess.square_file(k)
            wing=(r["cside"]=="K" and fl>=5 and kf>=5) or (r["cside"]=="Q" and fl<=2 and kf<=2)
            if wing and not b.is_attacked_by(not s,mv.from_square) and (clk is None or clk>=10):
                oc=R[not s]
                storm = oc["castled"] and oc["cside"]!=r["cside"]
                if storm: r["svs"]+=1
                else:
                    r["sv"]+=1; r["sm"].append(r["nm"])
                    if fl in (0,7) and abs(chess.square_rank(mv.to_square)-chess.square_rank(mv.from_square))==1: r["luft"]+=1
        b.push(mv)
    mate=b.is_checkmate(); res=h.get("Result")
    for s in sides:
        r=R[s]; o=R[not s]
        sc={"1-0":1.0,"0-1":0.0,"1/2-1/2":0.5}.get(res)
        if sc is not None and not s: sc=1-sc
        w.writerow([h.get("Site","")[-8:],h["White" if s else "Black"],"w" if s else "b",h.get("UTCDate","")+" "+h.get("UTCTime",""),
          h.get("WhiteElo" if s else "BlackElo"),h.get("BlackElo" if s else "WhiteElo"),sc,h.get("Termination"),int(mate and b.turn==s),
          r["nm"],r["castled"],r["cnm"],r["cside"],r["fl"],r["opp"],r["delay"],r["forfeit"],r["sv"],r["svs"],r["luft"],
          max(r["ds"],default=0),max(r["ds"][-10:],default=0),max(o["ds"][-10:],default=0)," ".join(map(str,r["dm"]))," ".join(map(str,r["sm"]))])
    n+=1
    if n%20000==0: print(fin,n,flush=True)
print(fin,"done",n,flush=True)
