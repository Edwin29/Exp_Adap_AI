import chess, chess.pgn, chess.engine, csv, sys
k=sys.argv[1]
V={1:1,2:3,3:3,4:5,5:9,6:0}
B={}
for r in csv.DictReader(open(f"moves{k}.csv")):
    c=float(r["clk"]) if r["clk"] not in ("","None") else 999
    if float(r["wp_loss"])>=30 and c>=10: B[(r["site"],int(r["ply"]))]=r
e=chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish"); e.configure({"Threads":1,"Hash":64})
LIM=chess.engine.Limit(depth=10)
def enprise(b,sq):
    p=b.piece_at(sq)
    if p is None or p.piece_type==6: return False
    att=b.attackers(not p.color,sq)
    if not att: return False
    if not b.attackers(p.color,sq): return True
    return min(V[b.piece_type_at(a)] for a in att)<V[p.piece_type]
def hanging(b,color,minv=3):
    return [sq for sq in chess.SQUARES if (pc:=b.piece_at(sq)) and pc.color==color and V[pc.piece_type]>=minv and enprise(b,sq)]
def best(b):
    if b.is_game_over(): return None,None
    i=e.analyse(b,LIM); pv=i.get("pv",[]); return (pv[0] if pv else None),i["score"].pov(b.turn)
def netgain(b,mv):
    t=b.piece_type_at(mv.to_square); cap=V[t] if t else 1
    mover=V[b.piece_type_at(mv.from_square)]; b2=b.copy(); b2.push(mv)
    return cap-mover if b2.attackers(b2.turn,mv.to_square) else cap
out=csv.writer(open(f"blund{k}.csv","w",newline=""))
out.writerow(["site","ply","p","win","own_nm","clk","wp_loss","cp_before","cp_after","cat","reply_cap","reply_check","best_cap","was_check","n_legal"])
f=open(f"part{k}.pgn"); n=0
while True:
    g=chess.pgn.read_game(f)
    if g is None: break
    sid=g.headers.get("Site","")[-8:]; b=g.board(); ply=0
    for node in g.mainline():
        ply+=1; mv=node.move
        r=B.get((sid,ply))
        if r is None: b.push(mv); continue
        me=b.turn; was_check=b.is_check(); nleg=b.legal_moves.count()
        bm,_=best(b); hang0=set(hanging(b,me))
        best_cap=0
        if bm and b.is_capture(bm):
            best_cap=netgain(b,bm)
        b1=b.copy(); b1.push(mv)
        rp,sc=best(b1); rcap=0; rchk=0; capsq=None
        if rp:
            rchk=int(b1.gives_check(rp))
            if b1.is_capture(rp):
                rcap=netgain(b1,rp); capsq=rp.to_square
        ca=float(r["cp_after"])
        if bm==mv: cat="noise"
        elif b1.is_checkmate() or (sc is not None and sc.is_mate() and sc.mate()>0): cat="mate_allowed"
        elif rcap>=2 and not rchk:
            if capsq==mv.to_square: cat="moved_piece_hung"
            elif capsq in hang0 or (b.piece_at(capsq) and capsq!=mv.from_square and enprise(b,capsq)): cat="ignored_threat"
            else: cat="other_piece_hung"
        elif best_cap>=2: cat="missed_capture"
        elif rchk or rcap>=1: cat="allowed_tactic"
        else: cat="positional_other"
        out.writerow([sid,ply,r["p"],r["win"],r["own_nm"],r["clk"],r["wp_loss"],r["cp_before"],ca,cat,rcap,rchk,best_cap,int(was_check),nleg])
        b.push(mv)
    n+=1
    if n%500==0: print(k,n,flush=True)
e.quit(); print(k,"done",flush=True)
