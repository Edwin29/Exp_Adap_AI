import chess, chess.pgn, gzip, sys, io, re, csv
from datetime import datetime
names=set(open("/mnt/project-files/analysis/2018-01/cohort_names.txt").read().split())
fin, fout = sys.argv[1], sys.argv[2]
cols=["p","color","ts","tc","elo","oppelo","score","term","mated","plies","castled","castle_ply","castle_side",
      "shield_pawn_moves","checks_recv","sec_per_move","first_move","eco","nmoves_own"]
w=csv.writer(open(fout,"w",newline="")); w.writerow(cols)
f=io.TextIOWrapper(gzip.open(fin,"rb"),encoding="utf-8")
n=0
while True:
    g=chess.pgn.read_game(f)
    if g is None: break
    h=g.headers
    try: ts=h["UTCDate"]+" "+h["UTCTime"]
    except KeyError: continue
    base,inc=0,0
    m=re.match(r"(\d+)\+(\d+)",h.get("TimeControl",""))
    if m: base,inc=int(m.group(1)),int(m.group(2))
    res=h.get("Result","*")
    board=g.board()
    recs={chess.WHITE:dict(castled=0,cply=None,cside="",shield=0,checks=0,clks=[],first="",nm=0),
          chess.BLACK:dict(castled=0,cply=None,cside="",shield=0,checks=0,clks=[],first="",nm=0)}
    ply=0
    for node in g.mainline():
        mv=node.move; side=board.turn; r=recs[side]
        if r["nm"]==0: r["first"]=board.san(mv)
        r["nm"]+=1
        if board.is_castling(mv):
            r["castled"]=1; r["cply"]=r["nm"]; r["cside"]="K" if board.is_kingside_castling(mv) else "Q"
        elif r["castled"] and board.piece_type_at(mv.from_square)==chess.PAWN:
            fl=chess.square_file(mv.from_square)
            if (r["cside"]=="K" and fl>=5) or (r["cside"]=="Q" and fl<=2): r["shield"]+=1
        board.push(mv); ply+=1
        if board.is_check(): recs[board.turn]["checks"]+=1
        c=node.clock()
        if c is not None: r["clks"].append(c)
    mate=board.is_checkmate()
    for side,nm in ((chess.WHITE,h.get("White")),(chess.BLACK,h.get("Black"))):
        if nm not in names: continue
        r=recs[side]
        score={"1-0":1.0,"0-1":0.0,"1/2-1/2":0.5}.get(res)
        if score is not None and side==chess.BLACK: score=1-score
        cl=r["clks"]; spm=""
        if len(cl)>=2 and base>0:
            used=base-cl[-1]+inc*(len(cl)-1)
            spm=round(used/len(cl),2)
        mated=int(mate and board.turn==side)
        w.writerow([nm,"w" if side else "b",ts,h.get("TimeControl"),h.get(("WhiteElo","BlackElo")[side==chess.BLACK]),
                    h.get(("BlackElo","WhiteElo")[side==chess.BLACK]),score,h.get("Termination"),mated,ply,r["castled"],
                    r["cply"] if r["cply"] else "",r["cside"],r["shield"],r["checks"],spm,r["first"],h.get("ECO"),r["nm"]])
    n+=1
print(fin,n)
